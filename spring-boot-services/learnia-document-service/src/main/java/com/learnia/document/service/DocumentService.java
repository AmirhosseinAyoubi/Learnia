package com.learnia.document.service;

import com.learnia.document.web.dto.DocumentResponse;
import com.learnia.document.web.dto.CreateDocumentRequest;

import java.util.List;
import java.util.UUID;

public interface DocumentService {

    List<DocumentResponse> getAllDocuments();

    DocumentResponse getDocumentById(UUID id);

    DocumentResponse createDocument(CreateDocumentRequest request);
}