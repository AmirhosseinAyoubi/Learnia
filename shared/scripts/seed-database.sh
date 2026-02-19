#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker exec -i learnia-postgres psql -U learnia_user -d postgres < "$SCRIPT_DIR/../docker/postgres/seed-data.sql"
