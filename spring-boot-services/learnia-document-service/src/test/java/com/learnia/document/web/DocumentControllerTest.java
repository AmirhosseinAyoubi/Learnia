package com.learnia.document.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import com.learnia.document.web.dto.UpdateStatusRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DocumentController.class)
@TestPropertySource(properties = {
        "file.upload-dir=/tmp/learnia-test/uploads",
        "document.processing.queue=test.queue",
        "spring.cloud.config.enabled=false",
        "eureka.client.enabled=false"
})
class DocumentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private DocumentService documentService;

    // ---- GET /documents ----

    @Test
    void getAllDocuments_returnsEmptyList() throws Exception {
        when(documentService.getAllDocuments()).thenReturn(List.of());

        mockMvc.perform(get("/documents"))
                .andExpect(status().isOk())
                .andExpect(content().json("[]"));
    }

    @Test
    void getAllDocuments_returnsDocumentList() throws Exception {
        DocumentResponse doc = buildResponse("My Doc", "PENDING");
        when(documentService.getAllDocuments()).thenReturn(List.of(doc));

        mockMvc.perform(get("/documents"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].title", is("My Doc")))
                .andExpect(jsonPath("$[0].processingStatus", is("PENDING")));
    }

    // ---- GET /documents/{id} ----

    @Test
    void getDocumentById_returnsDocument() throws Exception {
        DocumentResponse doc = buildResponse("Test Doc", "COMPLETED");
        when(documentService.getDocumentById(doc.getId())).thenReturn(doc);

        mockMvc.perform(get("/documents/" + doc.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title", is("Test Doc")))
                .andExpect(jsonPath("$.processingStatus", is("COMPLETED")))
                .andExpect(jsonPath("$.fileUrl", notNullValue()));
    }

    @Test
    void getDocumentById_throwsWhenNotFound() throws Exception {
        UUID id = UUID.randomUUID();
        when(documentService.getDocumentById(id)).thenThrow(new RuntimeException("Document not found: " + id));

        mockMvc.perform(get("/documents/" + id))
                .andExpect(status().is5xxServerError());
    }

    // ---- POST /documents ----

    @Test
    void createDocument_returnsCreatedDocument() throws Exception {
        DocumentResponse doc = buildResponse("New Doc", "PENDING");
        when(documentService.createDocument(any(CreateDocumentRequest.class))).thenReturn(doc);

        CreateDocumentRequest request = new CreateDocumentRequest(
                "New Doc", "file.pdf", "PDF", 1024L,
                "/tmp/file.pdf", UUID.randomUUID(), UUID.randomUUID()
        );

        mockMvc.perform(post("/documents")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title", is("New Doc")))
                .andExpect(jsonPath("$.processingStatus", is("PENDING")));
    }

    // ---- POST /documents/upload ----

    @Test
    void uploadFile_returnsFileUrlAndFileName() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.pdf", MediaType.APPLICATION_PDF_VALUE, "fake content".getBytes()
        );

        mockMvc.perform(multipart("/documents/upload")
                        .file(file)
                        .param("title", "Test Upload"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.fileUrl", notNullValue()))
                .andExpect(jsonPath("$.fileName", containsString("test.pdf")));
    }

    @Test
    void uploadFile_fileNameContainsTimestampPrefix() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "document.pdf", MediaType.APPLICATION_PDF_VALUE, "data".getBytes()
        );

        mockMvc.perform(multipart("/documents/upload")
                        .file(file)
                        .param("title", "Doc"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.fileName", matchesPattern("\\d+_document\\.pdf")));
    }

    // ---- PATCH /documents/{id}/status ----

    @Test
    void updateStatus_returnsNoContent() throws Exception {
        UUID id = UUID.randomUUID();
        UpdateStatusRequest req = new UpdateStatusRequest();
        req.setStatus("COMPLETED");
        req.setPageCount(10);

        doNothing().when(documentService).updateStatus(eq(id), eq("COMPLETED"), eq(10), isNull());

        mockMvc.perform(patch("/documents/" + id + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isNoContent());

        verify(documentService).updateStatus(id, "COMPLETED", 10, null);
    }

    @Test
    void updateStatus_withError_passesErrorToService() throws Exception {
        UUID id = UUID.randomUUID();
        UpdateStatusRequest req = new UpdateStatusRequest();
        req.setStatus("FAILED");
        req.setError("extraction failed");

        doNothing().when(documentService).updateStatus(any(), any(), any(), any());

        mockMvc.perform(patch("/documents/" + id + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isNoContent());

        verify(documentService).updateStatus(id, "FAILED", null, "extraction failed");
    }

    @Test
    void updateStatus_throwsWhenDocumentNotFound() throws Exception {
        UUID id = UUID.randomUUID();
        UpdateStatusRequest req = new UpdateStatusRequest();
        req.setStatus("COMPLETED");

        doThrow(new RuntimeException("Document not found: " + id))
                .when(documentService).updateStatus(any(), any(), any(), any());

        mockMvc.perform(patch("/documents/" + id + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().is5xxServerError());
    }

    // ---- helper ----

    private DocumentResponse buildResponse(String title, String status) {
        return new DocumentResponse(
                UUID.randomUUID(), title, "file.pdf", "PDF", 1024L,
                "/tmp/file.pdf", status, LocalDateTime.now()
        );
    }
}
