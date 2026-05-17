-- Learnia Content Service – Database Initialisation
-- Run once against learnia_content_db to create all required tables.
--
-- Usage (local):
--   psql -U learnia_user -d learnia_content_db -f init_content_db.sql
--
-- Usage (Docker):
--   docker exec -i <postgres-container> psql -U learnia_user learnia_content_db \
--     < python-services/content-service/scripts/init_content_db.sql

-- Enable UUID generation (PostgreSQL 13+: gen_random_uuid() is built-in)

-- ---------------------------------------------------------------------------
-- document_chunks
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id   UUID         NOT NULL,
    chunk_index   INTEGER      NOT NULL,
    content       TEXT         NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks (document_id);

-- ---------------------------------------------------------------------------
-- generated_materials
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS generated_materials (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id   UUID         NOT NULL,
    material_type VARCHAR(50)  NOT NULL,  -- summary | key_concepts | flashcards
    content       JSONB        NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_materials_document_id ON generated_materials (document_id);

-- ---------------------------------------------------------------------------
-- Sample data (useful for smoke-testing the service)
-- ---------------------------------------------------------------------------
INSERT INTO document_chunks (document_id, chunk_index, content) VALUES
    ('00000000-0000-0000-0000-000000000001', 0,
     'Microservices architecture decomposes applications into small, independently deployable services.'),
    ('00000000-0000-0000-0000-000000000001', 1,
     'Each service owns its own database and communicates via well-defined APIs.')
ON CONFLICT DO NOTHING;

INSERT INTO generated_materials (document_id, material_type, content) VALUES
    ('00000000-0000-0000-0000-000000000001', 'summary',
     '"Microservices split large applications into focused, independently deployable units."'),
    ('00000000-0000-0000-0000-000000000001', 'key_concepts',
     '["microservices", "service mesh", "API gateway", "database per service"]'),
    ('00000000-0000-0000-0000-000000000001', 'flashcards',
     '[{"question": "What is a microservice?", "answer": "A small, independently deployable service with a single responsibility."}]')
ON CONFLICT DO NOTHING;
