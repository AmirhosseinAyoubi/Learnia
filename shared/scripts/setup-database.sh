#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_DIR="$SCRIPT_DIR/../docker/postgres"

docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/001_auth_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/002_user_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/003_course_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/004_document_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/005_content_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/006_question_service_schema.sql"
docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SQL_DIR/007_quiz_service_schema.sql"
