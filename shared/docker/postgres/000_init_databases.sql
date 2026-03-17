\c postgres;

-- Create databases for each microservice.
-- These run only on first container initialization via docker-entrypoint-initdb.d.

CREATE DATABASE learnia_auth_db;
CREATE DATABASE learnia_user_db;
CREATE DATABASE learnia_course_db;
CREATE DATABASE learnia_document_db;
CREATE DATABASE learnia_content_db;
CREATE DATABASE learnia_question_db;
CREATE DATABASE learnia_quiz_db;

-- Ensure pgvector extension is available in the content database.
\c learnia_content_db;
CREATE EXTENSION IF NOT EXISTS vector;

