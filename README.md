# Learnia – Deliverables

> **PWP 2026**  
> Group: Amirhossein Ayoubi · _Ata Jodeiri_ · _Sahar Fatemi_ 

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Dependencies & How to Install](#2-dependencies--how-to-install)
3. [Database](#3-database)
4. [Database Models & Rationale](#4-database-models--rationale)
5. [Relationships & ON DELETE Behaviour](#5-relationships--on-delete-behaviour)
6. [Environment Setup](#6-environment-setup)
7. [Running the API Locally](#7-running-the-api-locally)
8. [Running the Client Locally](#8-running-the-client-locally)
9. [Running Tests](#9-running-tests)
10. [Deployment to CSC Rahti / OpenShift](#10-deployment-to-csc-rahti--openshift)
11. [Public URL & Health Endpoint](#11-public-url--health-endpoint)
12. [Own Work vs AI-Assisted Work](#12-own-work-vs-ai-assisted-work)

---

## 1. Project Overview

Learnia is a microservices-based AI-powered learning platform. Students log in, create a personal **study workspace** (e.g. "DB-Course"), upload materials (PDF, PPTX, TXT), and the AI generates questions, quizzes, and explanations from those materials.

| Layer | Technology | Services |
|---|---|---|
| Java / Spring Boot | Spring Boot 3.2, Java 17 | Gateway, Eureka, Config, Auth, User, Course, Document |
| Python / FastAPI | Python 3.11, FastAPI 0.104 | Processing, Content, AI, Question, Quiz |
| Infrastructure | Docker, PostgreSQL 16 + pgvector, Redis 7, RabbitMQ 3 | — |
| Frontend | React (Vite) | `client/` |

---

## 2. Dependencies & How to Install

### System Requirements

| Tool | Minimum Version | Purpose |
|---|---|---|
| Docker | 24+ | Runs PostgreSQL, Redis, RabbitMQ |
| Docker Compose | 2.0+ | Orchestrates all infrastructure containers |
| Java JDK | 17 | Spring Boot microservices |
| Maven | 3.9+ | Java build tool |
| Python | 3.11+ | FastAPI microservices |
| Node.js | 18+ | React frontend |
| `oc` CLI | 4.x | OpenShift / Rahti deployment (optional, for cloud deploy only) |

### Python — Install dependencies

```bash
cd python-services/processing-service
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**`requirements.txt`** (key libraries):

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.104.1 | Web framework |
| `uvicorn[standard]` | 0.24.0 | ASGI server |
| `pydantic` / `pydantic-settings` | 2.5.0 / 2.1.0 | Data validation & config |
| `sqlalchemy` | 2.0.23 | ORM for PostgreSQL |
| `alembic` | 1.12.1 | Database migrations |
| `psycopg2-binary` | 2.9.9 | PostgreSQL driver |
| `pgvector` | 0.2.3 | Vector similarity search |
| `openai` | 1.3.0 | GPT / embedding API client |
| `tiktoken` | 0.5.1 | Token counting for OpenAI |
| `PyPDF2` / `pdfplumber` | 3.0.1 / 0.10.3 | PDF text extraction |
| `python-pptx` | 0.6.23 | PowerPoint text extraction |
| `pika` | 1.3.2 | RabbitMQ client |
| `httpx` | 0.25.1 | HTTP client |

### Java — Install dependencies

```bash
cd spring-boot-services
mvn install -DskipTests
```

All Java dependencies are declared in each service's `pom.xml` and managed via Maven. Key Spring Boot starters:

| Dependency | Version | Purpose |
|---|---|---|
| `spring-boot-starter-web` | 3.2.0 | REST API layer |
| `spring-boot-starter-data-jpa` | 3.2.0 | ORM / Hibernate |
| `spring-boot-starter-security` | 3.2.0 | Authentication & authorisation |
| `spring-cloud-starter-netflix-eureka-client` | 2023.0.0 | Service discovery |
| `spring-cloud-starter-gateway` | 2023.0.0 | API gateway routing |
| `spring-cloud-starter-config` | 2023.0.0 | Centralised configuration |
| `postgresql` (JDBC) | managed | PostgreSQL driver |
| `flyway-core` | managed | Schema migrations |

---

## 3. Database

### Engine & Version

**PostgreSQL 16** with the **pgvector** extension.

- Docker image: `pgvector/pgvector:pg16`
- The `pgvector` extension is required for the `embeddings` table (semantic search vectors).

### Connection Details (development)

| Parameter | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |

Copy [`env.template`](env.template) into `.env` and adjust for your environment.

### Database-per-Service Architecture

One dedicated PostgreSQL database per microservice (database-per-service pattern):

| # | Database | Tables |
|---|---|---|
| 1 | `learnia_auth_db` | `api_keys` |
| 2 | `learnia_user_db` | `users`, `user_activities` |
| 3 | `learnia_course_db` | `courses`, `modules`, `lessons`, `student_workspaces`, `workspace_documents` |
| 4 | `learnia_document_db` | `documents`, `document_processing_jobs` |
| 5 | `learnia_content_db` | `content_chunks`, `embeddings` |
| 6 | `learnia_question_db` | `questions`, `answers` |
| 7 | `learnia_quiz_db` | `quizzes`, `quiz_questions`, `quiz_attempts`, `quiz_attempt_answers` |

---

## 4. Database Models & Rationale

### Document Service (`learnia_document_db`)

**`documents`** — core entity representing an uploaded file.

| Column | Type | Rationale |
|---|---|---|
| `id` | UUID | Globally unique, safe to expose in URLs |
| `title` | VARCHAR | Human-readable label |
| `file_name` | VARCHAR | Original filename on disk |
| `file_type` | VARCHAR | Used by processing-service to select the correct extractor (PDF/PPTX/TXT) |
| `file_url` | VARCHAR | Absolute path on the shared volume; passed to processing-service via RabbitMQ |
| `file_size` | BIGINT | Stored for informational purposes |
| `uploaded_by` | VARCHAR | User identifier |
| `workspace_id` | UUID | Links document to a student workspace |
| `processing_status` | VARCHAR | `PENDING` → `PROCESSING` → `COMPLETED` / `FAILED` |
| `created_at` | TIMESTAMP | Audit trail |

**`document_processing_jobs`** — tracks individual processing attempts.

| Column | Type | Rationale |
|---|---|---|
| `id` | UUID | Primary key |
| `document_id` | UUID (FK) | References `documents.id`, CASCADE DELETE |
| `status` | VARCHAR | Job-level status |
| `error_message` | TEXT | Populated on failure for debugging |
| `created_at` | TIMESTAMP | Job start time |

**Design rationale**: Separating job history from the document itself allows retrying processing without losing audit history, and allows a document to have multiple processing attempts.

### Auth Service (`learnia_auth_db`)

**`api_keys`** — stores API keys used for stateless authentication.

| Column | Type | Rationale |
|---|---|---|
| `id` | UUID | Primary key |
| `key_value` | VARCHAR | The actual API key sent in `X-API-Key` header |
| `description` | VARCHAR | Human-readable label |
| `enabled` | BOOLEAN | Allows revoking a key without deleting it |
| `created_at` | TIMESTAMP | Audit trail |

**Design rationale**: Stateless API-key authentication removes the need for session management or JWT refresh flows, which simplifies the architecture for a microservices deployment.

---

## 5. Relationships & ON DELETE Behaviour

| Parent | Child | Relationship | ON DELETE |
|---|---|---|---|
| `courses` | `modules` | 1 → many | CASCADE |
| `modules` | `lessons` | 1 → many | CASCADE |
| `courses` | `student_workspaces` | 1 → many (optional) | SET NULL |
| `student_workspaces` | `workspace_documents` | 1 → many | CASCADE |
| `documents` | `document_processing_jobs` | 1 → many | CASCADE |
| `content_chunks` | `embeddings` | 1 → 1 | CASCADE |
| `questions` | `answers` | 1 → many | CASCADE |
| `quizzes` | `quiz_questions` | 1 → many | CASCADE |
| `quizzes` | `quiz_attempts` | 1 → many | CASCADE |
| `quiz_attempts` | `quiz_attempt_answers` | 1 → many | CASCADE |
| `quiz_questions` | `quiz_attempt_answers` | 1 → many | CASCADE |

---

## 6. Environment Setup

### Copy the environment template

```bash
cp env.template .env
```

Open `.env` and fill in the required values. Never commit `.env` to git.

### Key environment variables

| Variable | Used by | Description |
|---|---|---|
| `DB_USERNAME` | document-service | PostgreSQL username |
| `DB_PASSWORD` | document-service | PostgreSQL password |
| `RABBITMQ_USER` | document-service | RabbitMQ username |
| `RABBITMQ_PASS` | document-service | RabbitMQ password |
| `RABBITMQ_PASSWORD` | processing-service | RabbitMQ password (Python config) |
| `DOCUMENT_SERVICE_URL` | processing-service | `http://document-service:8084` |
| `FILE_UPLOAD_DIR` | document-service | Path to shared uploads directory |
| `PROCESSING_SERVICE_URL` | gateway | URL to processing-service |

### Start infrastructure (PostgreSQL, RabbitMQ)

```bash
docker-compose up -d postgres rabbitmq
```

Wait until healthy:

```bash
docker-compose ps
```

---

## 7. Running the API Locally

### Option A — Docker Compose (recommended)

Starts all services including document-service and processing-service:

```bash
docker-compose up --build
```

The gateway will be available at: `http://localhost:8080`

### Option B — Run services individually

**Spring Boot services** (run each in a separate terminal):

```bash
# Eureka (start first)
cd spring-boot-services
mvn spring-boot:run -pl learnia-eureka-server

# Gateway
mvn spring-boot:run -pl learnia-gateway

# Auth service
mvn spring-boot:run -pl learnia-auth-service

# Document service
mvn spring-boot:run -pl learnia-document-service
```

**Python processing service**:

```bash
cd python-services/processing-service
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### API Entry Point (local)

```
http://localhost:8080
```

Health check:

```bash
curl http://localhost:8080/actuator/health
```

---

## 8. Running the Client Locally

```bash
cd client
npm install
npm run dev
```

The React frontend will be available at: `http://localhost:5173`

Make sure the gateway is running on port 8080 before starting the client.

---

## 9. Running Tests

### Java — document-service

```bash
cd spring-boot-services
mvn test -pl learnia-document-service
```

Test classes:
- `DocumentServiceImplTest` — 12 unit tests for the service layer (Mockito, no Spring context)
- `DocumentControllerTest` — 10 integration tests for the REST layer (`@WebMvcTest`)

Test configuration uses H2 in-memory database with Flyway disabled. RabbitMQ and Eureka are excluded from the test context.

### Python — processing-service

```bash
cd python-services/processing-service
source .venv/bin/activate
pip install pytest
pytest tests/ -v
```

Test files:
- `tests/test_processors.py` — 13 tests (text extraction and chunking logic)
- `tests/test_clients.py` — 7 tests (HTTP callback client)
- `tests/test_services.py` — 6 tests (process_document orchestration)
- `tests/test_consumers.py` — 5 tests (RabbitMQ consumer callback)

All external dependencies (RabbitMQ, HTTP, file I/O) are mocked using `unittest.mock`.

---

## 10. Deployment to CSC Rahti / OpenShift

The document-processing pipeline is deployed on **CSC Rahti 2 (OpenShift 4)** in the `learnia` namespace.

### Prerequisites

- `oc` CLI installed and logged in: `oc login https://api.2.rahti.csc.fi:6443 --token=<your-token>`
- Docker logged in to the Rahti registry: `docker login image-registry.apps.2.rahti.csc.fi`
- Active project: `oc project learnia`

### Step 1 — Build and push images

All images must be built for `linux/amd64` (Rahti runs AMD64):

```bash
# Eureka
docker build --platform linux/amd64 --provenance=false \
  -f spring-boot-services/Dockerfile.eureka spring-boot-services/ \
  -t image-registry.apps.2.rahti.csc.fi/learnia/eureka:latest
docker push image-registry.apps.2.rahti.csc.fi/learnia/eureka:latest

# Gateway
docker build --platform linux/amd64 --provenance=false \
  -f spring-boot-services/Dockerfile.gateway spring-boot-services/ \
  -t image-registry.apps.2.rahti.csc.fi/learnia/gateway:latest
docker push image-registry.apps.2.rahti.csc.fi/learnia/gateway:latest

# Document service
docker build --platform linux/amd64 --provenance=false \
  -f spring-boot-services/Dockerfile.document spring-boot-services/ \
  -t image-registry.apps.2.rahti.csc.fi/learnia/document-service:latest
docker push image-registry.apps.2.rahti.csc.fi/learnia/document-service:latest

# Processing service
docker build --platform linux/amd64 --provenance=false \
  python-services/processing-service/ \
  -t image-registry.apps.2.rahti.csc.fi/learnia/processing-service:latest
docker push image-registry.apps.2.rahti.csc.fi/learnia/processing-service:latest
```

Infrastructure images (PostgreSQL and RabbitMQ) are mirrored to the Rahti internal registry because CSC Rahti nodes have limited access to Docker Hub. See `rahti/03-postgres.yaml` and `rahti/04-rabbitmq.yaml` for the images used.

### Step 2 — Create secrets

Secrets are never stored in git. Create them manually:

```bash
oc create secret generic learnia-db-secret \
  --from-literal=username=<db-user> \
  --from-literal=password=<db-password> -n learnia

oc create secret generic learnia-rabbitmq-secret \
  --from-literal=username=<rabbit-user> \
  --from-literal=password=<rabbit-password> -n learnia
```

### Step 3 — Apply manifests

```bash
oc apply -f rahti/01-configmap.yaml
oc apply -f rahti/02-uploads-pvc.yaml
oc apply -f rahti/03-postgres.yaml
oc apply -f rahti/04-rabbitmq.yaml

# Wait for postgres and rabbitmq to be ready
oc rollout status deployment/postgres -n learnia
oc rollout status deployment/rabbitmq -n learnia

oc apply -f rahti/05-eureka.yaml
oc apply -f rahti/06-document-service.yaml
oc apply -f rahti/07-processing-service.yaml
oc apply -f rahti/08-gateway.yaml
```

> `rahti/00-secrets.yaml` contains placeholder values only. Do not apply it — use `oc create secret` above instead.

### Manifest files overview

| File | What it does |
|---|---|
| `rahti/00-secrets.yaml` | Placeholder template — fill and create manually |
| `rahti/01-configmap.yaml` | All non-sensitive shared configuration |
| `rahti/02-uploads-pvc.yaml` | 10Gi ReadWriteOnce PVC for uploaded files |
| `rahti/03-postgres.yaml` | PostgreSQL Deployment + PVC + Service |
| `rahti/04-rabbitmq.yaml` | RabbitMQ Deployment + PVC + Service |
| `rahti/05-eureka.yaml` | Eureka service registry Deployment + Service |
| `rahti/06-document-service.yaml` | Java document-service Deployment + Service |
| `rahti/07-processing-service.yaml` | Python processing-service Deployment + Service (with podAffinity) |
| `rahti/08-gateway.yaml` | Gateway Deployment + Service + OpenShift Route (TLS) |

### Verify deployment

```bash
oc get pods -n learnia
curl https://gateway-learnia.2.rahtiapp.fi/actuator/health
```

---

## 11. Public URL & Health Endpoint

| | Value |
|---|---|
| **Public URL** | `https://gateway-learnia.2.rahtiapp.fi` |
| **Health endpoint** | `https://gateway-learnia.2.rahtiapp.fi/actuator/health` |
| **Expected response** | `{"status":"UP","groups":["liveness","readiness"]}` |
| **Platform** | CSC Rahti 2 / OpenShift 4 |
| **Namespace** | `learnia` |

All traffic enters through the gateway. TLS is terminated at the OpenShift Route edge (certificate provided by Rahti).

### Document API endpoints (via gateway)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/documents` | List all documents |
| `GET` | `/api/v1/documents/{id}` | Get document by ID |
| `POST` | `/api/v1/documents` | Create a document record and trigger processing |
| `PATCH` | `/api/v1/documents/{id}/status` | Update processing status (called by processing-service) |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |

---

## 12. Own Work vs AI-Assisted Work

### Implemented by the team

- Overall microservices architecture design and service boundaries
- Database schema design for all services
- Document upload flow: API design, controller, service, repository layers
- RabbitMQ message publishing and consumer design
- Python processing pipeline: text extraction, chunking, status callback
- Docker Compose configuration for local development
- Rahti deployment strategy (storage design, pod affinity solution)
- All test case logic and coverage decisions

### AI-assisted (Claude / GitHub Copilot)

- Boilerplate code generation for Spring Boot controllers, services, and repositories
- Test class scaffolding (`@WebMvcTest`, `@ExtendWith(MockitoExtension.class)` patterns)
- Kubernetes/OpenShift manifest files (`rahti/*.yaml`) — reviewed and corrected by the team
- Debugging of deployment issues (ARM64/AMD64 image mismatch, Cinder RWO storage limitation, RabbitMQ image tag changes)
- Dockerfile patterns for multi-stage Maven builds
- README and wiki documentation drafts — reviewed and verified by the team

All AI-generated code was reviewed, tested, and corrected where necessary before being committed. The team is responsible for the final state of all files in this repository.
