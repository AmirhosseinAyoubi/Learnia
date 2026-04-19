package com.learnia.document.web.dto;

public class UpdateStatusRequest {

    private String status;
    private Integer pageCount;
    private String error;

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Integer getPageCount() { return pageCount; }
    public void setPageCount(Integer pageCount) { this.pageCount = pageCount; }
    public String getError() { return error; }
    public void setError(String error) { this.error = error; }
}
