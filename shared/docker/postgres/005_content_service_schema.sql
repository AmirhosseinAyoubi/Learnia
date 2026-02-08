
\c learnia_content_db;

-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Content Chunks Table
-- Text chunks extracted from documents
CREATE TABLE content_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Embeddings Table
-- Vector embeddings for semantic search
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL UNIQUE,
    embedding vector(1536) NOT NULL,
    model VARCHAR(50) NOT NULL DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_embeddings_chunk FOREIGN KEY (chunk_id) REFERENCES content_chunks(id) ON DELETE CASCADE
);

-- Indexes for content_chunks
CREATE INDEX idx_content_chunks_document_id_index ON content_chunks(document_id, chunk_index);
CREATE INDEX idx_content_chunks_document_id ON content_chunks(document_id);
CREATE INDEX idx_content_chunks_page_number ON content_chunks(page_number);

-- GIN index for JSONB metadata queries
CREATE INDEX idx_content_chunks_metadata ON content_chunks USING GIN (metadata);

-- Indexes for embeddings
-- Vector similarity search index using IVFFlat (for cosine similarity)
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX idx_embeddings_model ON embeddings(model);

-- Comments for documentation
COMMENT ON TABLE content_chunks IS 'Text chunks extracted from documents for processing and embedding';
COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search using pgvector';
COMMENT ON COLUMN content_chunks.document_id IS 'Reference to document ID in document service (UUID)';
COMMENT ON COLUMN content_chunks.chunk_index IS 'Order of chunk within the document';
COMMENT ON COLUMN content_chunks.page_number IS 'Page number for PDFs or slide number for PPTX';
COMMENT ON COLUMN content_chunks.metadata IS 'Additional context: slide number, section, formatting, etc.';
COMMENT ON COLUMN embeddings.embedding IS 'OpenAI embedding vector (1536 dimensions)';
COMMENT ON COLUMN embeddings.model IS 'Embedding model used: text-embedding-ada-002, etc.';
