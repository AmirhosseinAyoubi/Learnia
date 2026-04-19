# Learnia Project Log

> Rules: Never delete or overwrite entries. Append only.

---

## [2026-04-19] — Project Log Initialized

**What was done:** Created `memory.md` as a running project log in the project root.

**Why:** Establish a persistent, append-only record of all analysis and changes made to this codebase.

**Affected files:**
- `memory.md` (created)

**Next steps / Warnings:**
- No application code has been modified.
- Awaiting next task instructions before touching any source files.

---

## [2026-04-19] — Step 1: Make document service stateless

**What was analyzed:** Full source of `learnia-document-service` checked for anything preventing stateless behavior.

**Verdict: Already stateless. No changes made.**

Evidence:
- No `spring-boot-starter-security` or `spring-session` in `pom.xml`
- No `HttpSession`, `SecurityContext`, `@SessionAttributes`, or cookie usage in any Java file
- No session/security config in `application.yml`
- Every endpoint is purely request-scoped

**Affected files:** None (no changes required)

**Next steps / Warnings:**
- Step 1 complete. Service is confirmed stateless.
- If Spring Security is added in future steps, session policy must be explicitly set to `STATELESS`.
- Hardcoded `@CrossOrigin(origins = "http://localhost:3000")` in `DocumentController.java` is a separate concern to address later.

---

## [2026-04-19] — Step 1 (Full Backend): Make all services stateless

**What was analyzed:** All spring-boot services and all python services checked for session, cookie, login state, and server-side user state.

**Findings per service:**

| Service | Was Stateless? | Action Taken |
|---|---|---|
| learnia-document-service | Yes | No change |
| learnia-auth-service | Yes | No change — `SessionCreationPolicy.STATELESS` already set; JWT Bearer header auth; no `HttpSession` |
| learnia-gateway | Partial | Changed `allowCredentials: true` → `false` in CORS config |
| processing-service (Python) | Yes | No change — stub service, no auth |
| content-service (Python) | Yes | No change — stub service, no auth |
| ai-service (Python) | Yes | No change — stub service, no auth |
| question-service (Python) | Yes | No change — stub service, no auth |
| quiz-service (Python) | Yes | No change — stub service, no auth |

**Why `allowCredentials: true` was changed:**
`allowCredentials: true` in CORS permits browsers to send session cookies on cross-origin requests. This is unnecessary and counter to API-key/Bearer token auth — JWT is carried in the `Authorization` header, not in cookies.

**Affected files:**
- `spring-boot-services/learnia-gateway/src/main/resources/application.yml` (1 line changed)

**Next steps / Warnings:**
- Auth service has `RefreshToken` and `BlacklistedToken` persisted in DB. These are not HTTP sessions, but they represent server-side token lifecycle state. If full API-key auth (no login/refresh flow) is the end target, these should be evaluated in a future step.
- Auth service still exposes `/login`, `/register`, `/refresh`, `/logout` endpoints — this is login-based auth, not API-key auth. Replacing these is a larger architectural step, not done here.
- Document service still has hardcoded `@CrossOrigin(origins = "http://localhost:3000")` — should be removed once the gateway is the sole entry point.

---

## [2026-04-19] — auth-service: Replace login/JWT auth with API-key auth

**What changed:** Removed all login/session/JWT infrastructure. Replaced with API-key-based auth (`X-API-Key` header).

**Created:**
- `model/ApiKey.java` — entity: id, keyValue, userId, active, note, createdAt
- `repository/ApiKeyRepository.java` — findByKeyValueAndActiveTrue, findByUserId
- `config/ApiKeyAuthFilter.java` — reads `X-API-Key` header, validates against DB, sets SecurityContext per request
- `web/ApiKeyController.java` — POST /api/v1/auth/keys (create), GET (list by userId), DELETE /{id} (revoke)

**Modified:**
- `config/SecurityConfig.java` — removed JwtAuthFilter + PasswordEncoder bean; wired ApiKeyAuthFilter; STATELESS session policy kept
- `config/AuthDataInitializer.java` — seeds 3 dev API keys on startup instead of refresh/blacklisted tokens
- `AuthServiceApplication.java` — removed `@EnableFeignClients`
- `application.yml` — removed `jwt.*` config block
- `pom.xml` — removed jjwt-api/impl/jackson, spring-cloud-starter-openfeign, spring-security-crypto

**Deleted:**
- `config/JwtAuthFilter.java`
- `service/JwtService.java`, `TokenService.java`, `impl/DefaultTokenService.java`
- `model/RefreshToken.java`, `BlacklistedToken.java`
- `repository/RefreshTokenRepository.java`, `BlacklistedTokenRepository.java`
- `web/AuthController.java` (login, register, refresh, logout)
- `web/dto/AuthResponse.java`, `LoginRequest.java`, `RegisterRequest.java`, `UserDto.java`
- `client/UserServiceClient.java`

**Next steps / Warnings:**
- `/api/v1/auth/keys` (create/list) is open without auth — intentional for bootstrapping dev keys; lock down in production.
- Frontend still calls login/register endpoints — do not touch frontend per rules; it will need updating separately.
- Other services (user-service, course-service) do not yet validate the `X-API-Key` header — they are unprotected; address in a future step.

---

## [2026-04-19] — auth-service: Post-rewrite error check

**What was checked:** All remaining Java files in `learnia-auth-service` statically verified after the API-key rewrite.

**Result: No errors found. No code changes made.**

Checks performed:
- No references to any deleted class (`RefreshToken`, `BlacklistedToken`, `JwtService`, `TokenService`, `JwtAuthFilter`, `UserServiceClient`, `LoginRequest`, `RegisterRequest`, `AuthResponse`, `UserDto`) remain in any source file
- All imports across 7 remaining files resolve correctly
- `GenerationType.UUID` valid: Spring Boot 3.2.0 uses Hibernate 6.4 + Jakarta Persistence 3.1 ✓
- `jakarta.servlet.*` and `jakarta.persistence.*` namespaces used correctly (Spring Boot 3.x) ✓
- `ApiKey.keyValue` column length 64 matches generated key length (32+32 chars, two UUIDs without dashes) ✓
- Empty residual directories (`client/`, `service/`, `service/impl/`, `web/dto/`) are harmless; Maven ignores them
- `pom.xml` has no orphaned dependencies pointing to removed code

**Affected files:** None (verification only)

---

## [2026-04-19] — Step 2 (Java): Document upload + processing foundation

**What changed:** Wired upload → metadata → RabbitMQ pipeline; added processing status callback endpoint.

**Created:**
- `config/RabbitMQConfig.java` — declares durable queue, sets Jackson JSON message converter on RabbitTemplate
- `web/dto/UpdateStatusRequest.java` — DTO for Python service to report processing result (status, pageCount, error)

**Modified:**
- `application.yml` — added `document.processing.queue` property (default: `document.processing`)
- `web/dto/DocumentResponse.java` — added `fileUrl` field + getter/setter so callers know where the file lives
- `service/DocumentService.java` — added `updateStatus(UUID, String, Integer, String)` to interface
- `service/impl/DocumentServiceImpl.java` — injected `RabbitTemplate`; publishes `{documentId, fileUrl, fileType}` message after save; implemented `updateStatus`; extracted `toResponse()` helper; RabbitMQ publish errors are caught and logged, not fatal
- `web/DocumentController.java` — removed hardcoded `System.getProperty("user.dir")` path; now uses `@Value("${file.upload-dir}")`; upload returns `{fileUrl, fileName}` JSON instead of plain string; added `PATCH /documents/{id}/status` endpoint; removed `@CrossOrigin` (gateway handles CORS)

**Next steps / Warnings:**
- Python processing-service is still empty — it must consume from queue `document.processing`, extract text, chunk it, and call `PATCH /documents/{id}/status` when done.
- Upload still uses a timestamp prefix to avoid filename collisions — production should use UUID-named files.
- `DocumentResponse.fileUrl` is now returned, but the frontend currently ignores it; no frontend change made.

---

## [2026-04-19] — Step 2 (Python): processing-service foundation

**What changed:** Implemented the full document processing pipeline in the previously empty Python service.

**Modified:**
- `src/config.py` — fixed `rabbitmq_queue` default from `document_processing` to `document.processing` to match Java's published queue name

**Filled in (were empty `__init__.py` stubs):**
- `src/schemas/__init__.py` — Pydantic models: `ProcessDocumentMessage` (in), `StatusUpdate` (out)
- `src/processors/__init__.py` — text extraction (PDF via pdfplumber, PPTX via python-pptx, TXT plain read) + tiktoken-based chunking at 512 tokens per chunk
- `src/clients/__init__.py` — sync `httpx.Client` calling Java `PATCH /documents/{id}/status`
- `src/services/__init__.py` — orchestration: marks PROCESSING → extract text → chunk → calls COMPLETED or FAILED with page count / error
- `src/consumers/__init__.py` — pika RabbitMQ consumer with 5-attempt exponential backoff on startup; nacks failed messages without requeue
- `src/routers/__init__.py` — `POST /api/v1/processing/process` HTTP trigger (uses FastAPI `BackgroundTasks`, non-blocking)
- `src/main.py` — wires router + starts consumer in daemon thread on `startup` event; logging configured; `allow_credentials: false`

**Flow after this change:**
```
RabbitMQ queue: document.processing
  └─ consumer receives {documentId, fileUrl, fileType}
       └─ service marks doc PROCESSING
       └─ processor extracts text + page count from file
       └─ chunker splits into ≤512-token chunks
       └─ client PATCHes Java /documents/{id}/status → COMPLETED / FAILED
```

**Next steps / Warnings:**
- Chunks are logged but not stored anywhere — content-service integration needed to persist chunks + embeddings.
- `file_url` is a local filesystem path (`/tmp/learnia/uploads/...`); both Java and Python must share the same filesystem (or object storage in production).
- RabbitMQ consumer runs in a daemon thread; if it crashes it will not restart — a supervisor or health check should be added for production.
- `POST /api/v1/processing/process` is open without auth; add API key check when auth propagation is implemented.

---

## [2026-04-19] — Step 2 verification: Java + Python consistency check

**What was checked:** All 13 step-2 files read and cross-verified for import errors, config mismatches, field name mismatches, and integration issues.

**Bugs found and fixed:**

1. `src/services/__init__.py` — **Critical**: relative imports used single dot (`.processors`, `.clients`) which resolved to `src.services.processors` / `src.services.clients` — neither exists. Would have caused `ImportError` at startup. Fixed to `..processors` and `..clients`.

2. `src/processors/__init__.py` — unused `from typing import Optional` import removed.

**Verified correct (no changes):**
- Queue name: Java publishes to `document.processing`, Python consumes from `document.processing` ✓
- RabbitMQ message fields: `documentId`, `fileUrl`, `fileType` match on both sides ✓
- Callback URL: Python calls `{document_service_url}/documents/{id}/status` → matches Java `PATCH /documents/{id}/status` ✓
- Status payload fields: Python sends `{status, pageCount, error}` → matches Java `UpdateStatusRequest` fields ✓
- Status enum values: Python sends uppercase `"PROCESSING"` / `"COMPLETED"` / `"FAILED"` → matches Java `ProcessingStatus.valueOf()` ✓
- All other Python relative imports (`..config`, `..schemas`, `..services`) are correct ✓
- Java `RabbitTemplate` bean override and `Jackson2JsonMessageConverter` setup are correct ✓

**Affected files:**
- `src/services/__init__.py` (import bug fix)
- `src/processors/__init__.py` (unused import removed)

---

## [2026-04-19] — Step 2 completeness check

**Question:** Is step 2 (document upload + processing pipeline) fully done at the code level?

**Answer: Yes.**

Full end-to-end trace verified:
- Upload → file saved to `${file.upload-dir}`, `{fileUrl, fileName}` returned ✓
- Metadata POST → DB save → RabbitMQ publish `{documentId, fileUrl, fileType}` ✓
- Queue name `document.processing` matches on both Java and Python sides ✓
- Python consumer receives message, calls `process_document` ✓
- Extractor handles PDF (pdfplumber), PPTX (python-pptx), TXT (plain read) ✓
- Chunker splits extracted text with tiktoken at 512 tokens ✓
- Python calls Java `PATCH /documents/{id}/status` with `{status, pageCount, error}` ✓
- Java `UpdateStatusRequest` fields and `ProcessingStatus.valueOf()` match Python's uppercase strings ✓
- All required Python libraries present in `requirements.txt` ✓
- All Java beans wired: `RabbitTemplate`, `Jackson2JsonMessageConverter`, `@Value` properties ✓
- No Flyway migration files — harmless (Flyway 9.x succeeds with 0 migrations; schema via `ddl-auto: update`) ✓

**Pre-existing issues (not step 2, not fixed):**
- Gateway routes `/api/v1/documents/**` but service maps to `/documents` — affects frontend, not processing pipeline
- `Document.uploadedBy` is non-nullable but can be omitted by client — pre-existing design gap

**No code changes made.**
