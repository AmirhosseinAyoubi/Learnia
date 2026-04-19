package com.learnia.document.web.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class DocumentResponse {

    private UUID id;
    private String title;
    private String fileName;
    private String fileType;
    private Long fileSize;
    private String fileUrl;
    private String processingStatus;
    private LocalDateTime createdAt;

    public DocumentResponse() {
    }

    public DocumentResponse(
            UUID id,
            String title,
            String fileName,
            String fileType,
            Long fileSize,
            String fileUrl,
            String processingStatus,
            LocalDateTime createdAt
    ) {
        this.id = id;
        this.title = title;
        this.fileName = fileName;
        this.fileType = fileType;
        this.fileSize = fileSize;
        this.fileUrl = fileUrl;
        this.processingStatus = processingStatus;
        this.createdAt = createdAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getFileType() {
        return fileType;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public String getFileUrl() {
        return fileUrl;
    }

    public void setFileUrl(String fileUrl) {
        this.fileUrl = fileUrl;
    }

    public String getProcessingStatus() {
        return processingStatus;
    }

    public void setProcessingStatus(String processingStatus) {
        this.processingStatus = processingStatus;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}