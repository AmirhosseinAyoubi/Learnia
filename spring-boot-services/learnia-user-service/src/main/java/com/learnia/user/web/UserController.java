package com.learnia.user.web;

import com.learnia.user.model.User;
import com.learnia.user.service.UserService;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;
import com.learnia.user.web.dto.UserResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

/**
 * UserController — REST API for the user-service.
 *
 * All responses use UserResponse DTO (never the raw User entity) to
 * ensure passwordHash is never serialized into HTTP responses.
 *
 * POST /api/v1/users — register a new user (called by auth-service via Feign)
 * GET /api/v1/users/{id} — get user by UUID
 * GET /api/v1/users/email/{email} — get user by email
 * GET /api/v1/users/username/{u} — get user by username
 * PUT /api/v1/users/{id}/profile — update profile fields
 * PUT /api/v1/users/{id}/deactivate — soft-delete user
 * PUT /api/v1/users/{id}/verify — mark user email as verified
 * POST /api/v1/users/verify-password — internal: verify raw password vs stored
 * hash
 */
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    public ResponseEntity<UserResponse> registerUser(@RequestBody UserRegistrationRequest request) {
        try {
            User user = userService.registerUser(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(UserResponse.from(user));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable UUID id) {
        return userService.findById(id)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/email/{email}")
    public ResponseEntity<UserResponse> getUserByEmail(@PathVariable String email) {
        return userService.findByEmail(email)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/username/{username}")
    public ResponseEntity<UserResponse> getUserByUsername(@PathVariable String username) {
        return userService.findByUsername(username)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}/profile")
    public ResponseEntity<UserResponse> updateProfile(
            @PathVariable UUID id,
            @RequestBody UserProfileUpdateRequest request) {
        try {
            User updated = userService.updateProfile(id, request);
            return ResponseEntity.ok(UserResponse.from(updated));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PutMapping("/{id}/deactivate")
    public ResponseEntity<Void> deactivateUser(@PathVariable UUID id) {
        try {
            userService.deactivateUser(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PutMapping("/{id}/verify")
    public ResponseEntity<Void> markUserVerified(@PathVariable UUID id) {
        try {
            userService.markUserVerified(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Internal endpoint — verifies raw password against the stored BCrypt hash.
     * Called by auth-service over Feign during login.
     * Returns true if password matches, false otherwise.
     *
     * This endpoint is intentionally internal (behind the gateway, not exposed
     * publicly).
     */
    @PostMapping("/verify-password")
    public ResponseEntity<Boolean> verifyPassword(
            @RequestBody Map<String, String> body) {
        String email = body.get("email");
        String password = body.get("password");

        if (email == null || password == null) {
            return ResponseEntity.badRequest().build();
        }

        boolean match = userService.verifyPassword(email, password);
        return ResponseEntity.ok(match);
    }
}
