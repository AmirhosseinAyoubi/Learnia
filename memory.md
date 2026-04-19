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
