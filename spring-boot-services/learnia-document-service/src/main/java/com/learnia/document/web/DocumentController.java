package com.learnia.document.web;

import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * DocumentController — CRUD endpoints for documents.
 *
 * GET  /api/v1/documents        — list all documents
 * GET  /api/v1/documents/{id}   — retrieve a single document by UUID
 * POST /api/v1/documents        — create a document record
 * POST /api/v1/documents/upload — upload a file (multipart/form-data)
 *
 * All responses include a _links object for HATEOAS navigation.
 */
@RestController
@RequestMapping("/api/v1/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    /**
     * Returns all documents. Each item includes a self-link.
     *
     * @return 200 with list of documents
     */
    @GetMapping
    public ResponseEntity<List<DocumentResponse>> getAllDocuments() {
        List<DocumentResponse> documents = documentService.getAllDocuments();
        documents.forEach(doc -> doc.setLinks(buildSelfLinks(doc)));
        return ResponseEntity.ok(documents);
    }

    /**
     * Returns a single document by UUID with full navigation links.
     *
     * @param id document UUID
     * @return 200 with document and _links, or 404 if not found
     */
    @GetMapping("/{id}")
    public ResponseEntity<DocumentResponse> getDocumentById(@PathVariable UUID id) {
        DocumentResponse doc = documentService.getDocumentById(id);
        doc.setLinks(buildDetailLinks(doc));
        return ResponseEntity.ok(doc);
    }

    /**
     * Creates a new document record.
     *
     * @param request JSON body — title, fileName, fileType, fileSize, fileUrl, uploadedBy, workspaceId
     * @return 201 Created with the new document and _links
     */
    @PostMapping
    public ResponseEntity<DocumentResponse> createDocument(@RequestBody CreateDocumentRequest request) {
        DocumentResponse doc = documentService.createDocument(request);
        doc.setLinks(buildDetailLinks(doc));
        return ResponseEntity.status(HttpStatus.CREATED).body(doc);
    }

    /**
     * Uploads a file to the server upload directory.
     *
     * @param file  binary file (multipart/form-data)
     * @param title human-readable title
     * @return 200 success message, or 500 on failure
     */
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("title") String title) {
        try {
            String uploadDir = System.getProperty("user.dir") + "/uploads/";
            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }
            file.transferTo(new File(uploadDir + file.getOriginalFilename()));
            return ResponseEntity.ok("File uploaded successfully: " + file.getOriginalFilename() + " | Title: " + title);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Upload failed: " + e.getMessage());
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    /** Minimal _links with just a self-link — used in list responses. */
    private Map<String, Map<String, String>> buildSelfLinks(DocumentResponse doc) {
        Map<String, Map<String, String>> links = new LinkedHashMap<>();
        links.put("self", Map.of("href", "/api/v1/documents/" + doc.getId()));
        return links;
    }

    /** Full _links for a single-document response. */
    private Map<String, Map<String, String>> buildDetailLinks(DocumentResponse doc) {
        Map<String, Map<String, String>> links = new LinkedHashMap<>();
        links.put("self",       Map.of("href", "/api/v1/documents/" + doc.getId()));
        links.put("collection", Map.of("href", "/api/v1/documents"));
        if (doc.getUploadedBy() != null) {
            links.put("uploader", Map.of("href", "/api/v1/users/" + doc.getUploadedBy()));
        }
        return links;
    }
}
