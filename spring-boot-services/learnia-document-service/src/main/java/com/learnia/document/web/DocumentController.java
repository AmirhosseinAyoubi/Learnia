package com.learnia.document.web;

import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import com.learnia.document.web.dto.UpdateStatusRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Tag(name = "Documents", description = "Document upload, retrieval, and processing status")
@RestController
@RequestMapping("/documents")
public class DocumentController {

    private final DocumentService documentService;

    @Value("${file.upload-dir}")
    private String uploadDir;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @Operation(summary = "List all documents")
    @ApiResponse(responseCode = "200", description = "Document list returned")
    @GetMapping
    public List<DocumentResponse> getAllDocuments() {
        return documentService.getAllDocuments();
    }

    @Operation(summary = "Get a document by ID")
    @ApiResponse(responseCode = "200", description = "Document found")
    @ApiResponse(responseCode = "404", description = "Document not found")
    @GetMapping("/{id}")
    public DocumentResponse getDocumentById(@PathVariable UUID id) {
        return documentService.getDocumentById(id);
    }

    @Operation(summary = "Create a document record", description = "Registers a document and triggers async processing via RabbitMQ")
    @ApiResponse(responseCode = "201", description = "Document created")
    @PostMapping
    public ResponseEntity<DocumentResponse> createDocument(@RequestBody CreateDocumentRequest request) {
        return ResponseEntity.status(201).body(documentService.createDocument(request));
    }

    @Operation(summary = "Upload a file", description = "Saves the file to disk and returns the stored file URL and name")
    @ApiResponse(responseCode = "200", description = "File uploaded successfully")
    @ApiResponse(responseCode = "500", description = "Upload failed")
    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("title") String title
    ) {
        try {
            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            String savedFileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            File dest = new File(uploadDir + File.separator + savedFileName);
            file.transferTo(dest);

            String fileUrl = uploadDir + File.separator + savedFileName;
            return ResponseEntity.ok(Map.of("fileUrl", fileUrl, "fileName", savedFileName));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Upload failed: " + e.getMessage()));
        }
    }

    @Operation(summary = "Delete a document", description = "Permanently removes a document record")
    @ApiResponse(responseCode = "204", description = "Document deleted")
    @ApiResponse(responseCode = "404", description = "Document not found")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDocument(@PathVariable UUID id) {
        documentService.deleteDocument(id);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Update document processing status", description = "Called by the processing-service after document parsing completes")
    @ApiResponse(responseCode = "204", description = "Status updated")
    @PatchMapping("/{id}/status")
    public ResponseEntity<Void> updateStatus(
            @PathVariable UUID id,
            @RequestBody UpdateStatusRequest request
    ) {
        documentService.updateStatus(id, request.getStatus(), request.getPageCount(), request.getError());
        return ResponseEntity.noContent().build();
    }
}
