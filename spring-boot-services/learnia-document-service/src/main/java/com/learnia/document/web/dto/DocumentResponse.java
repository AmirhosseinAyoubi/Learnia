package com.learnia.document.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;
import java.util.UUID;

public class DocumentResponse {

    private UUID id;
    private String title;
    private String fileName;
    private String fileType;
    private Long fileSize;
    private String processingStatus;
    private UUID uploadedBy;
    @JsonProperty("_links")
    private Map<String, Map<String, String>> links;

    public DocumentResponse() {
    }

    public DocumentResponse(UUID id, String title, String fileName, String fileType, Long fileSize, String processingStatus) {
        this.id = id;
        this.title = title;
        this.fileName = fileName;
        this.fileType = fileType;
        this.fileSize = fileSize;
        this.processingStatus = processingStatus;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }

    public String getFileType() { return fileType; }
    public void setFileType(String fileType) { this.fileType = fileType; }

    public Long getFileSize() { return fileSize; }
    public void setFileSize(Long fileSize) { this.fileSize = fileSize; }

    public String getProcessingStatus() { return processingStatus; }
    public void setProcessingStatus(String processingStatus) { this.processingStatus = processingStatus; }

    public UUID getUploadedBy() { return uploadedBy; }
    public void setUploadedBy(UUID uploadedBy) { this.uploadedBy = uploadedBy; }

    public Map<String, Map<String, String>> getLinks() { return links; }
    public void setLinks(Map<String, Map<String, String>> links) { this.links = links; }
}
