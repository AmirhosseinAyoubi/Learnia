package com.learnia.document.service.impl;

import com.learnia.document.model.Document;
import com.learnia.document.model.ProcessingStatus;
import com.learnia.document.repository.DocumentRepository;
import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class DocumentServiceImpl implements DocumentService {

    private static final Logger log = LoggerFactory.getLogger(DocumentServiceImpl.class);

    private final DocumentRepository documentRepository;
    private final RabbitTemplate rabbitTemplate;

    @Value("${document.processing.queue}")
    private String processingQueue;

    public DocumentServiceImpl(DocumentRepository documentRepository, RabbitTemplate rabbitTemplate) {
        this.documentRepository = documentRepository;
        this.rabbitTemplate = rabbitTemplate;
    }

    @Override
    public List<DocumentResponse> getAllDocuments() {
        return documentRepository.findAll().stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public DocumentResponse getDocumentById(UUID id) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Document not found: " + id));
        return toResponse(document);
    }

    @Override
    public DocumentResponse createDocument(CreateDocumentRequest request) {
        Document document = new Document();
        document.setTitle(request.getTitle());
        document.setFileName(request.getFileName());
        document.setFileType(request.getFileType());
        document.setFileSize(request.getFileSize());
        document.setFileUrl(request.getFileUrl());
        document.setUploadedBy(request.getUploadedBy());
        document.setWorkspaceId(request.getWorkspaceId());
        document.setProcessingStatus(ProcessingStatus.PENDING);

        Document saved = documentRepository.save(document);

        publishProcessingJob(saved);

        return toResponse(saved);
    }

    @Override
    public void updateStatus(UUID id, String status, Integer pageCount, String error) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Document not found: " + id));
        document.setProcessingStatus(ProcessingStatus.valueOf(status));
        if (pageCount != null) document.setPageCount(pageCount);
        if (error != null) document.setProcessingError(error);
        documentRepository.save(document);
        log.debug("Updated document {} status to {}", id, status);
    }

    private void publishProcessingJob(Document document) {
        try {
            Map<String, Object> message = new HashMap<>();
            message.put("documentId", document.getId().toString());
            message.put("fileUrl", document.getFileUrl());
            message.put("fileType", document.getFileType());
            rabbitTemplate.convertAndSend(processingQueue, message);
            log.info("Published processing job for documentId={}", document.getId());
        } catch (Exception e) {
            log.error("Failed to publish processing job for documentId={}: {}", document.getId(), e.getMessage());
        }
    }

    private DocumentResponse toResponse(Document d) {
        return new DocumentResponse(
                d.getId(),
                d.getTitle(),
                d.getFileName(),
                d.getFileType(),
                d.getFileSize(),
                d.getFileUrl(),
                d.getProcessingStatus() != null ? d.getProcessingStatus().name() : null,
                d.getCreatedAt()
        );
    }
}
