package com.learnia.document.service;

import com.learnia.document.model.Document;
import com.learnia.document.model.ProcessingStatus;
import com.learnia.document.repository.DocumentRepository;
import com.learnia.document.service.impl.DocumentServiceImpl;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DocumentServiceImplTest {

    @Mock
    private DocumentRepository documentRepository;

    @Mock
    private RabbitTemplate rabbitTemplate;

    @InjectMocks
    private DocumentServiceImpl documentService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(documentService, "processingQueue", "test.queue");
    }

    // ---- createDocument ----

    @Test
    void createDocument_savesEntityWithPendingStatus() {
        CreateDocumentRequest request = buildRequest();
        Document saved = documentFrom(request);
        when(documentRepository.save(any(Document.class))).thenReturn(saved);

        documentService.createDocument(request);

        ArgumentCaptor<Document> captor = ArgumentCaptor.forClass(Document.class);
        verify(documentRepository).save(captor.capture());
        assertThat(captor.getValue().getProcessingStatus()).isEqualTo(ProcessingStatus.PENDING);
    }

    @Test
    void createDocument_publishesProcessingJobToQueue() {
        CreateDocumentRequest request = buildRequest();
        Document saved = documentFrom(request);
        when(documentRepository.save(any(Document.class))).thenReturn(saved);

        documentService.createDocument(request);

        ArgumentCaptor<Object> messageCaptor = ArgumentCaptor.forClass(Object.class);
        verify(rabbitTemplate).convertAndSend(eq("test.queue"), messageCaptor.capture());

        @SuppressWarnings("unchecked")
        Map<String, Object> message = (Map<String, Object>) messageCaptor.getValue();
        assertThat(message).containsKey("documentId");
        assertThat(message).containsEntry("fileUrl", saved.getFileUrl());
        assertThat(message).containsEntry("fileType", saved.getFileType());
    }

    @Test
    void createDocument_returnsResponseWithFileUrl() {
        CreateDocumentRequest request = buildRequest();
        Document saved = documentFrom(request);
        when(documentRepository.save(any(Document.class))).thenReturn(saved);

        DocumentResponse response = documentService.createDocument(request);

        assertThat(response.getFileUrl()).isEqualTo("/tmp/file.pdf");
        assertThat(response.getProcessingStatus()).isEqualTo("PENDING");
    }

    @Test
    void createDocument_continuesWhenRabbitFails() {
        CreateDocumentRequest request = buildRequest();
        Document saved = documentFrom(request);
        when(documentRepository.save(any(Document.class))).thenReturn(saved);
        doThrow(new RuntimeException("RabbitMQ unavailable"))
                .when(rabbitTemplate).convertAndSend(anyString(), any(Object.class));

        DocumentResponse response = documentService.createDocument(request);

        assertThat(response).isNotNull();
        assertThat(response.getProcessingStatus()).isEqualTo("PENDING");
    }

    // ---- updateStatus ----

    @Test
    void updateStatus_setsCompletedWithPageCount() {
        UUID id = UUID.randomUUID();
        Document doc = new Document();
        doc.setId(id);
        doc.setProcessingStatus(ProcessingStatus.PROCESSING);
        when(documentRepository.findById(id)).thenReturn(Optional.of(doc));

        documentService.updateStatus(id, "COMPLETED", 42, null);

        ArgumentCaptor<Document> captor = ArgumentCaptor.forClass(Document.class);
        verify(documentRepository).save(captor.capture());
        assertThat(captor.getValue().getProcessingStatus()).isEqualTo(ProcessingStatus.COMPLETED);
        assertThat(captor.getValue().getPageCount()).isEqualTo(42);
    }

    @Test
    void updateStatus_setsFailedWithError() {
        UUID id = UUID.randomUUID();
        Document doc = new Document();
        doc.setId(id);
        doc.setProcessingStatus(ProcessingStatus.PROCESSING);
        when(documentRepository.findById(id)).thenReturn(Optional.of(doc));

        documentService.updateStatus(id, "FAILED", null, "extraction failed");

        ArgumentCaptor<Document> captor = ArgumentCaptor.forClass(Document.class);
        verify(documentRepository).save(captor.capture());
        assertThat(captor.getValue().getProcessingStatus()).isEqualTo(ProcessingStatus.FAILED);
        assertThat(captor.getValue().getProcessingError()).isEqualTo("extraction failed");
    }

    @Test
    void updateStatus_throwsWhenDocumentNotFound() {
        UUID id = UUID.randomUUID();
        when(documentRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> documentService.updateStatus(id, "COMPLETED", null, null))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Document not found");
    }

    @Test
    void updateStatus_doesNotOverridePageCountWhenNull() {
        UUID id = UUID.randomUUID();
        Document doc = new Document();
        doc.setId(id);
        doc.setPageCount(10);
        doc.setProcessingStatus(ProcessingStatus.PROCESSING);
        when(documentRepository.findById(id)).thenReturn(Optional.of(doc));

        documentService.updateStatus(id, "COMPLETED", null, null);

        ArgumentCaptor<Document> captor = ArgumentCaptor.forClass(Document.class);
        verify(documentRepository).save(captor.capture());
        assertThat(captor.getValue().getPageCount()).isEqualTo(10);
    }

    // ---- getDocumentById ----

    @Test
    void getDocumentById_returnsResponseForExistingDocument() {
        UUID id = UUID.randomUUID();
        Document doc = new Document();
        doc.setId(id);
        doc.setTitle("Test Doc");
        doc.setFileName("test.pdf");
        doc.setFileType("PDF");
        doc.setFileSize(1024L);
        doc.setFileUrl("/tmp/test.pdf");
        doc.setProcessingStatus(ProcessingStatus.COMPLETED);
        doc.setCreatedAt(LocalDateTime.now());
        when(documentRepository.findById(id)).thenReturn(Optional.of(doc));

        DocumentResponse response = documentService.getDocumentById(id);

        assertThat(response.getId()).isEqualTo(id);
        assertThat(response.getTitle()).isEqualTo("Test Doc");
        assertThat(response.getProcessingStatus()).isEqualTo("COMPLETED");
    }

    @Test
    void getDocumentById_throwsWhenNotFound() {
        UUID id = UUID.randomUUID();
        when(documentRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> documentService.getDocumentById(id))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Document not found");
    }

    // ---- getAllDocuments ----

    @Test
    void getAllDocuments_returnsAllMappedResponses() {
        Document d1 = new Document();
        d1.setId(UUID.randomUUID());
        d1.setTitle("D1");
        d1.setFileName("a.pdf");
        d1.setFileType("PDF");
        d1.setFileSize(100L);
        d1.setFileUrl("/a.pdf");
        d1.setProcessingStatus(ProcessingStatus.PENDING);

        Document d2 = new Document();
        d2.setId(UUID.randomUUID());
        d2.setTitle("D2");
        d2.setFileName("b.pdf");
        d2.setFileType("PDF");
        d2.setFileSize(200L);
        d2.setFileUrl("/b.pdf");
        d2.setProcessingStatus(ProcessingStatus.COMPLETED);

        when(documentRepository.findAll()).thenReturn(List.of(d1, d2));

        List<DocumentResponse> responses = documentService.getAllDocuments();

        assertThat(responses).hasSize(2);
        assertThat(responses).extracting(DocumentResponse::getTitle)
                .containsExactlyInAnyOrder("D1", "D2");
    }

    @Test
    void getAllDocuments_returnsEmptyListWhenNone() {
        when(documentRepository.findAll()).thenReturn(List.of());

        assertThat(documentService.getAllDocuments()).isEmpty();
    }

    // ---- helpers ----

    private CreateDocumentRequest buildRequest() {
        return new CreateDocumentRequest(
                "My Doc", "file.pdf", "PDF", 2048L,
                "/tmp/file.pdf", UUID.randomUUID(), UUID.randomUUID()
        );
    }

    private Document documentFrom(CreateDocumentRequest request) {
        Document doc = new Document();
        doc.setId(UUID.randomUUID());
        doc.setTitle(request.getTitle());
        doc.setFileName(request.getFileName());
        doc.setFileType(request.getFileType());
        doc.setFileSize(request.getFileSize());
        doc.setFileUrl(request.getFileUrl());
        doc.setUploadedBy(request.getUploadedBy());
        doc.setWorkspaceId(request.getWorkspaceId());
        doc.setProcessingStatus(ProcessingStatus.PENDING);
        doc.setCreatedAt(LocalDateTime.now());
        return doc;
    }
}
