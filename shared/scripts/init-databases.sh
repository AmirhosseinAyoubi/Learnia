#!/bin/bash

# Initialize databases for Learnia services
# This script should be run after PostgreSQL is started

echo "Initializing Learnia databases..."

psql -U learnia_user -d postgres -f - <<EOF
-- Create databases for each service
CREATE DATABASE learnia_auth_db;
CREATE DATABASE learnia_user_db;
CREATE DATABASE learnia_course_db;
CREATE DATABASE learnia_document_db;
CREATE DATABASE learnia_content_db;
CREATE DATABASE learnia_question_db;
CREATE DATABASE learnia_quiz_db;
EOF

echo "Enabling pgvector extension for content database..."
psql -U learnia_user -d learnia_content_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Database initialization complete!"
