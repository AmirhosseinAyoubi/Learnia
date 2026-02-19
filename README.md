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
6. [Database Setup](#6-database-setup)
7. [Populating the Database](#7-populating-the-database)
8. [Verifying the Data](#8-verifying-the-data)

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
| Docker |  | Runs PostgreSQL, Redis, RabbitMQ |
| Docker Compose |  | Orchestrates all infrastructure containers |
| Java JDK | 17 | Spring Boot microservices |
| Maven | 3.9+ | Java build tool |
| Python | 3.11+ | FastAPI microservices |
| Node.js | 18+ | React frontend |

### Python — Install dependencies

```bash
cd python-services
pip install -r requirements.txt      
pip install -r requirements-dev.txt   
```

**`requirements.txt`** (key libraries):

| Package | Version |
|---|---|
| `fastapi` | 0.104.1 
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
| `celery` | 5.3.4 | Async task queue |
| `redis` | 5.0.1 | Cache & Celery broker |
| `pika` | 1.3.2 | RabbitMQ client |
| `httpx` | 0.25.1 | Async HTTP client |
| `python-jose[cryptography]` | 3.3.0 | JWT parsing in Python services |

### Java — Install dependencies

```bash
cd spring-boot-services
mvn install -DskipTests
```

All Java dependencies are declared in each service's `pom.xml` and managed via Maven. Key Spring Boot starters:

| Dependency | Version |
|---|---|
| `spring-boot-starter-web` | 3.2.0 | REST API layer |
| `spring-boot-starter-data-jpa` | 3.2.0 | ORM / Hibernate |
| `spring-boot-starter-security` | 3.2.0 | Authentication & authorisation |
| `spring-cloud-starter-netflix-eureka-client` | 2023.0.0 | Service discovery |
| `spring-cloud-starter-gateway` | 2023.0.0 | API gateway routing |
| `spring-cloud-starter-config` | 2023.0.0 | Centralised configuration |
| `postgresql` (JDBC) | managed | PostgreSQL driver |
| `flyway-core` | managed | Schema migrations |
| `jjwt-api/impl/jackson` | 0.12.3 | JWT creation & validation |

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
| 1 | `learnia_auth_db` | `refresh_tokens`, `blacklisted_tokens` |
| 2 | `learnia_user_db` | `users`, `user_activities` |
| 3 | `learnia_course_db` | `courses`, `modules`, `lessons`, `student_workspaces`, `workspace_documents` |
| 4 | `learnia_document_db` | `documents`, `document_processing_jobs` |
| 5 | `learnia_content_db` | `content_chunks`, `embeddings` |
| 6 | `learnia_question_db` | `questions`, `answers` |
| 7 | `learnia_quiz_db` | `quizzes`, `quiz_questions`, `quiz_attempts`, `quiz_attempt_answers` |

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

## 6. Database Setup

### Step 1 — Start infrastructure

```bash
# From the project root
docker-compose up -d postgres redis rabbitmq
```

Wait for the health check:
```bash
docker-compose ps  
```

### Step 2 — Create all databases and tables

```bash
./shared/scripts/setup-database.sh
```

This runs the 7 schema SQL files in order and creates all databases, enums, tables, indexes, and constraints:

```
shared/docker/postgres/
  001_auth_service_schema.sql
  002_user_service_schema.sql
  003_course_service_schema.sql
  004_document_service_schema.sql
  005_content_service_schema.sql  
  006_question_service_schema.sql
  007_quiz_service_schema.sql
```

---

## 7. Populating the Database



```bash
./shared/scripts/seed-database.sh
```

SQL file: [`shared/docker/postgres/seed-data.sql`](shared/docker/postgres/seed-data.sql)

Inserts instances of **every model** across all 7 databases:

| Database | What is seeded |
|---|---|
| `learnia_user_db` | 7 users (1 admin, 2 instructors, 4 students) + 7 activity records |
| `learnia_course_db` | 4 courses, 7 modules, 14 lessons, 6 workspaces, 7 workspace-document links |
| `learnia_document_db` | 6 documents + 6 processing jobs |
| `learnia_content_db` | 11 content chunks (embeddings require the running AI service) |
| `learnia_question_db` | 6 questions + 4 answers |
| `learnia_quiz_db` | 4 quizzes, 12 questions, 5 attempts, 17 attempt answers |
| `learnia_auth_db` | No seed needed (tokens are created at runtime) |


