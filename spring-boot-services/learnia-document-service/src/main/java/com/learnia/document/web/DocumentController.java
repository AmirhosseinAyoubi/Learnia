package com.learnia.document.web;

import com.learnia.document.service.DocumentService;
import com.learnia.document.web.dto.CreateDocumentRequest;
import com.learnia.document.web.dto.DocumentResponse;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @GetMapping
    public List<DocumentResponse> getAllDocuments() {
        return documentService.getAllDocuments();
    }

    @GetMapping("/{id}")
    public DocumentResponse getDocumentById(@PathVariable UUID id) {
        return documentService.getDocumentById(id);
    }

    @PostMapping
    public DocumentResponse createDocument(@RequestBody CreateDocumentRequest request) {
        return documentService.createDocument(request);
    }

    @PostMapping("/upload")
    public String uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("title") String title
    ) {
        try {
            String uploadDir = System.getProperty("user.dir") + "/spring-boot-services/learnia-document-service/uploads/";
            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            String filePath = uploadDir + file.getOriginalFilename();
            File dest = new File(filePath);
            file.transferTo(dest);

            return "File uploaded successfully: " + file.getOriginalFilename() + " | Title: " + title;
        } catch (Exception e) {
            return "Upload failed: " + e.getMessage();
        }
    }
}