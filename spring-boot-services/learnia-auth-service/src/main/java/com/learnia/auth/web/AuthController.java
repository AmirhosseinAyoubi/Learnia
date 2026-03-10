package com.learnia.auth.web;

import com.learnia.auth.model.RefreshToken;
import com.learnia.auth.service.TokenService;
import com.learnia.auth.web.dto.AuthResponse;
import com.learnia.auth.web.dto.LoginRequest;
import com.learnia.auth.web.dto.RegisterRequest;
import com.learnia.auth.web.dto.UserDto;
import feign.FeignException;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import com.learnia.auth.client.UserServiceClient;

import java.time.Duration;
import java.util.Map;
import java.util.UUID;

/**
 * AuthController — public endpoints for authentication.
 *
 * POST /api/v1/auth/register — create account, return accessToken +
 * refreshToken + user
 * POST /api/v1/auth/login — verify credentials, return accessToken +
 * refreshToken + user
 * GET /api/v1/auth/me — return the caller's profile (JWT required)
 * POST /api/v1/auth/refresh — exchange a valid refreshToken for a new
 * accessToken
 * POST /api/v1/auth/logout — revoke refreshToken, blacklist current accessToken
 */
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private static final Logger log = LoggerFactory.getLogger(AuthController.class);

    private final TokenService tokenService;
    private final UserServiceClient userServiceClient;
    private final PasswordEncoder passwordEncoder;

    public AuthController(TokenService tokenService,
            UserServiceClient userServiceClient,
            PasswordEncoder passwordEncoder) {
        this.tokenService = tokenService;
        this.userServiceClient = userServiceClient;
        this.passwordEncoder = passwordEncoder;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // POST /login
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Authenticates a user.
     *
     * 1. Loads the user by email via Feign → user-service.
     * 2. Verifies the raw password against the stored BCrypt hash via a dedicated
     * internal endpoint in user-service (so that the hash never leaves
     * user-service).
     * 3. Generates a short-lived JWT access token and a long-lived opaque refresh
     * token.
     * 4. Returns both tokens and a safe user view.
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        if (!StringUtils.hasText(request.getEmail()) || !StringUtils.hasText(request.getPassword())) {
            return ResponseEntity.badRequest().build();
        }

        try {
            // Step 1: fetch user (404 → UNAUTHORIZED)
            UserDto user = userServiceClient.getUserByEmail(request.getEmail());

            // Step 2: verify password via internal user-service endpoint
            boolean passwordMatch = userServiceClient.verifyPassword(
                    new UserServiceClient.VerifyPasswordRequest(request.getEmail(), request.getPassword()));

            if (!passwordMatch) {
                log.warn("Login failed: wrong password for email={}", request.getEmail());
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            }

            // Step 3: issue tokens
            String role = user.getRole() != null ? user.getRole() : "STUDENT";
            String accessToken = tokenService.generateAccessToken(user.getId(), user.getEmail(), role);
            RefreshToken refreshToken = tokenService.createRefreshToken(user.getId(), Duration.ofDays(7));

            log.info("Login successful for email={}", request.getEmail());
            return ResponseEntity.ok(buildAuthResponse(accessToken, refreshToken.getToken(), user));

        } catch (FeignException.NotFound e) {
            log.warn("Login failed: user not found for email={}", request.getEmail());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        } catch (Exception e) {
            log.error("Error during login", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // POST /register
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Registers a new user account.
     *
     * Hashes the password here (auth-service owns authentication concerns),
     * then delegates user persistence to user-service via Feign.
     * On success, returns tokens so the user is immediately logged in.
     */
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@RequestBody RegisterRequest request) {
        if (!StringUtils.hasText(request.getEmail())
                || !StringUtils.hasText(request.getPassword())
                || !StringUtils.hasText(request.getUsername())) {
            return ResponseEntity.badRequest().build();
        }

        try {
            String hashedPassword = passwordEncoder.encode(request.getPassword());

            UserServiceClient.RegistrationRequest regRequest = new UserServiceClient.RegistrationRequest(
                    request.getEmail(),
                    request.getUsername(),
                    hashedPassword,
                    request.getFirstName(),
                    request.getLastName());

            UserDto createdUser = userServiceClient.registerUser(regRequest);

            String role = createdUser.getRole() != null ? createdUser.getRole() : "STUDENT";
            String accessToken = tokenService.generateAccessToken(createdUser.getId(), createdUser.getEmail(), role);
            RefreshToken refreshToken = tokenService.createRefreshToken(createdUser.getId(), Duration.ofDays(7));

            log.info("Registered new user email={} username={}", request.getEmail(), request.getUsername());
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(buildAuthResponse(accessToken, refreshToken.getToken(), createdUser));

        } catch (FeignException.BadRequest | FeignException.Conflict e) {
            log.warn("Registration failed (bad request / conflict): {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        } catch (Exception e) {
            log.error("Error during registration", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // GET /me
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Returns the profile of the currently authenticated user.
     *
     * The JwtAuthFilter has already validated the JWT and placed the userId
     * (UUID) into SecurityContextHolder as the authentication principal.
     * We use that userId to fetch the real user from user-service.
     */
    @GetMapping("/me")
    public ResponseEntity<UserDto> me() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        if (auth == null || !auth.isAuthenticated() || !(auth.getPrincipal() instanceof UUID)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        UUID userId = (UUID) auth.getPrincipal();

        try {
            UserDto user = userServiceClient.getUserById(userId);
            return ResponseEntity.ok(user);
        } catch (FeignException.NotFound e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        } catch (Exception e) {
            log.error("Error fetching user for /me, userId={}", userId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // POST /refresh
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Exchanges a valid, non-expired, non-revoked refresh token for a new JWT
     * access token.
     * Body: { "refreshToken": "..." }
     */
    @PostMapping("/refresh")
    public ResponseEntity<?> refresh(@RequestBody Map<String, String> body) {
        String refreshTokenValue = body.get("refreshToken");
        if (!StringUtils.hasText(refreshTokenValue)) {
            return ResponseEntity.badRequest().body(Map.of("error", "refreshToken is required"));
        }

        return tokenService.findRefreshToken(refreshTokenValue)
                .filter(rt -> !rt.isRevoked() && rt.getExpiresAt().isAfter(java.time.LocalDateTime.now()))
                .map(rt -> {
                    try {
                        UserDto user = userServiceClient.getUserById(rt.getUserId());
                        String role = user.getRole() != null ? user.getRole() : "STUDENT";
                        String newAccessToken = tokenService.generateAccessToken(user.getId(), user.getEmail(), role);
                        log.info("Refreshed access token for userId={}", rt.getUserId());
                        return ResponseEntity.ok(Map.of("accessToken", newAccessToken));
                    } catch (Exception e) {
                        log.error("Error issuing refresh token", e);
                        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                                .<Map<String, String>>build();
                    }
                })
                .orElseGet(() -> ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid or expired refresh token")));
    }

    // ─────────────────────────────────────────────────────────────────────────
    // POST /logout
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Logs out the current user by revoking their refresh token and blacklisting
     * the current access token so it cannot be reused before it naturally expires.
     *
     * Body: { "refreshToken": "..." }
     * Header: Authorization: Bearer <accessToken>
     */
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestBody Map<String, String> body,
            HttpServletRequest request) {
        String refreshTokenValue = body.get("refreshToken");

        // Revoke the refresh token if provided
        if (StringUtils.hasText(refreshTokenValue)) {
            tokenService.revokeRefreshToken(refreshTokenValue);
        }

        // Blacklist the current access token (so it can't be reused until expiry)
        String authHeader = request.getHeader("Authorization");
        if (StringUtils.hasText(authHeader) && authHeader.startsWith("Bearer ")) {
            String accessToken = authHeader.substring(7);
            // Use the raw token string as the "hash" key for simplicity.
            // In production, store only a real SHA-256 hash.
            tokenService.blacklistAccessToken(accessToken, Duration.ofMinutes(16)); // slightly > JWT TTL
        }

        log.info("Logout successful");
        return ResponseEntity.noContent().build();
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────────

    private AuthResponse buildAuthResponse(String accessToken, String refreshToken, UserDto user) {
        AuthResponse response = new AuthResponse();
        response.setAccessToken(accessToken);
        response.setRefreshToken(refreshToken);

        AuthResponse.UserView userView = new AuthResponse.UserView();
        userView.setId(user.getId());
        userView.setEmail(user.getEmail());
        userView.setUsername(user.getUsername());
        userView.setFirstName(user.getFirstName());
        userView.setLastName(user.getLastName());
        userView.setRole(user.getRole() != null ? user.getRole() : "STUDENT");
        userView.setIsVerified(user.getIsVerified() != null ? user.getIsVerified() : false);
        response.setUser(userView);

        return response;
    }
}
