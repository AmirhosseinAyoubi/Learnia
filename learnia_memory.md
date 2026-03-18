# Learnia Project Memory

Last updated: 2026-03-18

---

## Team

| Name | GitHub | Role |
|------|--------|------|
| Amirhossein Ayoubi | AmirhosseinAyoubi | Auth service, user service, project setup |
| Sahar Fatemi | Saharfatemi22 | Document service (controller, service, DTOs) |
| Ata Jodeiri | (this user) | API implementation, Docker, wiki, Python service |

---

## Project

**Learnia** — AI-powered learning platform (PWP 2026, University of Oulu).
Students upload documents → AI generates quizzes and questions from them.

**API Gateway:** `http://localhost:8080`
**Wiki:** cloned at `/d/ATAAAAA/Learnia/wiki/` from `https://github.com/AmirhosseinAyoubi/Learnia.wiki.git`

---

## Branches

| Branch | Author | What's in it |
|--------|--------|--------------|
| `main` | Team | Auth service, User service, Document service (basic), DB models, frontend scaffold |
| `feat/document` | Sahar | Document service: DocumentController, DocumentService, DTOs — merged to main |
| `feat/ata-api-implementation` | Ata | HATEOAS _links, Docker setup, functional tests, Dockerfile fixes |

---

## Teammates' Work (on main)

### Amirhossein
- Auth service fully implemented: register, login, me, refresh, logout with JWT
- User service fully implemented: CRUD, password verify, deactivate, verify
- DB schema SQL init scripts for all 7 databases
- Eureka, Gateway, Config server setup
- Frontend scaffold (React + Vite)
- docker-compose.yml (infra only — postgres, redis, rabbitmq)

### Sahar
- Document service: DocumentController, DocumentServiceImpl, DTOs (CreateDocumentRequest, DocumentResponse)
- Document DB model and Flyway migration
- Note: controller had `/documents` mapping bug (not `/api/v1/documents`) — fixed by Ata

---

## Ata's Contributions (feat/ata-api-implementation)

### Commit 1 — HATEOAS _links (90139b3)
- `AuthResponse.java`: added `_links` field with `@JsonProperty("_links")`
- `AuthController.java`: populates _links in buildAuthResponse() → profile, me, refresh, logout
- `DocumentResponse.java`: added `_links` + `uploadedBy` fields
- `DocumentController.java`:
  - Fixed @RequestMapping from `/documents` → `/api/v1/documents` (was unreachable through gateway)
  - POST /documents now returns 201 Created (was 200)
  - All responses include _links (self, collection, uploader)
  - Added proper ResponseEntity return types

### Commit 2 — Docker setup (e3480e4)
- `docker-compose.yml`: fixed to infra-only (postgres, redis, rabbitmq) — all on learnia-net
- `docker-compose.services.yml`: new file — all app services (Spring Boot + Python)
- `Dockerfile.document`: new file — builds document service image
- Fixed Docker bugs: RabbitMQ had no network, wrong DB URLs (auth/user pointed to wrong DB)

### Commit 3 — Functional tests (b408c92)
- `tests/conftest.py`: shared fixtures (base URLs, session user registration, auth tokens)
- `tests/test_auth.py`: 14 tests — register, login, me, refresh, logout (happy + error paths)
- `tests/test_documents.py`: 12 tests — list, get by id, create, upload (happy + error paths)
- `tests/requirements.txt` + `tests/README.md`

### In progress (not committed yet)
- Spring Boot Dockerfile updates — Maven cache mounts for faster builds
- Python services built in Docker (processing, content, ai, question, quiz) ✅

---

## Deadline 3 Grading Rubric

### 1. Wiki Report (6 pts) — STATUS: ✅ DONE

| Item | Pts | Status |
|------|-----|--------|
| Resource Table | 1.0 | ✅ Done — Auth, User, Document, Python health endpoints with controller names |
| Addressability | 1.5 | ✅ Done — URI hierarchy examples, UUID-based, sub-resources |
| Uniform Interface | 1.5 | ✅ Done — GET/POST/PUT with examples, status code table |
| Statelessness | 1.0 | ✅ Done — JWT flow, STATELESS Spring Security, token blacklisting |
| Connectedness | 1.0 | ✅ Done — _links examples, cross-service UUID refs |

### 2. API Implementation (est. ~10 pts) — STATUS: PARTIALLY DONE

| Item | Status | Notes |
|------|--------|-------|
| Auth service endpoints | ✅ (teammates) | register, login, me, refresh, logout |
| User service endpoints | ✅ (teammates) | CRUD, verify, deactivate |
| Document service endpoints | ✅ (teammates + Ata) | list, get, create, upload + _links fix |
| Python service (1+) | ⚠️ NEEDED | Health endpoints exist, Ata needs to add real endpoints to one service |
| Functional tests | ✅ (Ata) | 26 tests across auth + document |

### 3. Extras (bonus pts) — STATUS: PARTIALLY DONE

| Item | Status |
|------|--------|
| Authentication (JWT) | ✅ Done — implemented by teammates |
| HATEOAS / Connectedness | ✅ Done — added by Ata |
| Wiki sections (Auth, Schema, Caching) | ⚠️ Still blank in wiki |
| Resources allocation table | ⚠️ Still blank in wiki |
| Use of AI section | ⚠️ Still blank in wiki |

---

## What Ata Still Needs to Do

### HIGH PRIORITY
1. **Add real endpoints to one Python service** — e.g. processing-service: add POST /process to extract text from uploaded files. This is Ata's main implementation task.
2. **Add that Python service to the wiki resource table**

### MEDIUM PRIORITY
3. **Fill wiki extras** — Authentication section, Use of AI section, Resources allocation table
4. **Commit Dockerfile Maven cache updates** (already done locally, not committed)

### LOW PRIORITY
5. **Run functional tests** — requires Spring Boot services running locally
6. **Build/run Spring Boot services in Docker** — optional, not required for grading

---

## Docker Status

| Container | Status |
|-----------|--------|
| learnia-postgres | ✅ Running |
| learnia-redis | ✅ Running |
| learnia-rabbitmq | ✅ Running |
| Python service images | ✅ Built (not started) |
| Spring Boot images | ⚠️ Not built yet |

---

## Key File Locations

| File | Path |
|------|------|
| API wiki | `/d/ATAAAAA/Learnia/wiki/API-implementation.md` |
| docker-compose (infra) | `docker-compose.yml` |
| docker-compose (services) | `docker-compose.services.yml` |
| Functional tests | `tests/` |
| Auth controller | `spring-boot-services/learnia-auth-service/src/main/java/com/learnia/auth/web/AuthController.java` |
| Document controller | `spring-boot-services/learnia-document-service/src/main/java/com/learnia/document/web/DocumentController.java` |
| Python services | `python-services/{processing,content,ai,question,quiz}-service/src/main.py` |
