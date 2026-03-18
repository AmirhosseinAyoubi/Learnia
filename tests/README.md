# Learnia API — Functional Tests

## Dependencies

```bash
pip install -r tests/requirements.txt
```

## Prerequisites

The following services must be running before executing the tests:

| Service | Default URL |
|---------|------------|
| Auth Service | http://localhost:8081 |
| Document Service | http://localhost:8084 |

Start infrastructure first:
```bash
docker compose up -d
```

Then run the Spring Boot services from IntelliJ (or `mvn spring-boot:run` in each service directory).

## Running the tests

From the project root:

```bash
# All tests
pytest tests/ -v

# Auth tests only
pytest tests/test_auth.py -v

# Document tests only
pytest tests/test_documents.py -v

# With coverage report
pytest tests/ -v --cov=tests
```

## Custom service URLs

If your services run on different ports, override with environment variables:

```bash
AUTH_BASE_URL=http://localhost:8081/api/v1/auth \
DOC_BASE_URL=http://localhost:8084/api/v1/documents \
pytest tests/ -v
```
