package com.learnia.document.service.impl;

import com.learnia.document.model.Document;
import com.learnia.document.model.ProcessingStatus;
import com.learnia.document.repository.DocumentRepository;
import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;

    public DocumentServiceImpl(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }

    @Override
    public List<DocumentResponse> getAllDocuments() {
        List<Document> documents = documentRepository.findAll();

        return documents.stream()
                .map(document -> new DocumentResponse(
                        document.getId(),
                        document.getTitle(),
                        document.getFileName(),
                        document.getFileType(),
                        document.getFileSize(),
                        document.getProcessingStatus() != null
                                ? document.getProcessingStatus().name()
                                : null
                ))
                .collect(Collectors.toList());
    }

    @Override
    public DocumentResponse getDocumentById(UUID id) {
        Document document = documentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Document not found"));

        return new DocumentResponse(
                document.getId(),
                document.getTitle(),
                document.getFileName(),
                document.getFileType(),
                document.getFileSize(),
                document.getProcessingStatus() != null
                        ? document.getProcessingStatus().name()
                        : null
        );
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

        Document savedDocument = documentRepository.save(document);

        return new DocumentResponse(
                savedDocument.getId(),
                savedDocument.getTitle(),
                savedDocument.getFileName(),
                savedDocument.getFileType(),
                savedDocument.getFileSize(),
                savedDocument.getProcessingStatus() != null
                        ? savedDocument.getProcessingStatus().name()
                        : null
        );
    }
}