
\c learnia_document_db;

-- Processing Status Enum
CREATE TYPE processing_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- Documents Table
-- Document metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    file_url TEXT NOT NULL,
    uploaded_by UUID NOT NULL,
    workspace_id UUID,
    processing_status processing_status NOT NULL DEFAULT 'PENDING',
    processing_error TEXT,
    page_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Document Processing Jobs Table
-- Track processing jobs for documents
CREATE TABLE document_processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    CONSTRAINT fk_processing_jobs_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Indexes for documents
CREATE INDEX idx_documents_uploaded_by_created_at ON documents(uploaded_by, created_at DESC);
CREATE INDEX idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_file_type ON documents(file_type);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Indexes for document_processing_jobs
CREATE INDEX idx_processing_jobs_document_id_status ON document_processing_jobs(document_id, status);
CREATE INDEX idx_processing_jobs_status ON document_processing_jobs(status);
CREATE INDEX idx_processing_jobs_started_at ON document_processing_jobs(started_at DESC);

-- Comments for documentation
COMMENT ON TABLE documents IS 'Document metadata and file storage references';
COMMENT ON TABLE document_processing_jobs IS 'Tracks document processing jobs (PDF, PPTX, TXT extraction)';
COMMENT ON COLUMN documents.uploaded_by IS 'Reference to user ID in user service (UUID)';
COMMENT ON COLUMN documents.workspace_id IS 'Reference to workspace ID in course service, NULL if uploaded to instructor course';
COMMENT ON COLUMN documents.file_type IS 'Document type: PDF, PPTX, TXT, etc.';
COMMENT ON COLUMN documents.file_url IS 'Storage location: S3 path, local path, etc.';
COMMENT ON COLUMN documents.processing_status IS 'Status of document processing: PENDING, PROCESSING, COMPLETED, or FAILED';
COMMENT ON COLUMN documents.page_count IS 'Number of pages (for PDFs) or slides (for PPTX)';
