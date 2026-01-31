-- Create databases for each service
CREATE DATABASE learnia_auth_db;
CREATE DATABASE learnia_user_db;
CREATE DATABASE learnia_course_db;
CREATE DATABASE learnia_document_db;
CREATE DATABASE learnia_content_db;
CREATE DATABASE learnia_question_db;
CREATE DATABASE learnia_quiz_db;

-- Enable pgvector extension for content service database
\c learnia_content_db;
CREATE EXTENSION IF NOT EXISTS vector;
