#!/bin/bash

set -e

echo "Initializing Learnia databases inside Docker container..."

# Ensure the Postgres container is running
if ! docker ps --format '{{.Names}}' | grep -q '^learnia-postgres$'; then
  echo "Error: Docker container 'learnia-postgres' is not running."
  echo "Start it first from the project root with:"
  echo "  docker-compose up -d postgres"
  exit 1
fi

docker exec -i learnia-postgres psql -U learnia_user -d postgres <<EOF
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
docker exec -i learnia-postgres psql -U learnia_user -d learnia_content_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Database initialization complete!"
