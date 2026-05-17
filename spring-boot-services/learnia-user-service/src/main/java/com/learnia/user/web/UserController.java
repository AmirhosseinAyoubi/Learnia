package com.learnia.user.web;

import com.learnia.user.model.User;
import com.learnia.user.service.UserService;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;
import com.learnia.user.web.dto.UserResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@Tag(name = "Users", description = "User registration, lookup, and profile management")
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @Operation(summary = "Register a new user")
    @ApiResponse(responseCode = "201", description = "User registered")
    @ApiResponse(responseCode = "409", description = "Email or username already in use")
    @PostMapping
    public ResponseEntity<UserResponse> registerUser(@RequestBody UserRegistrationRequest request) {
        try {
            User user = userService.registerUser(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(UserResponse.from(user));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
    }

    @Operation(summary = "Get user by ID")
    @ApiResponse(responseCode = "200", description = "User found")
    @ApiResponse(responseCode = "404", description = "User not found")
    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable UUID id) {
        return userService.findById(id)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Get user by email")
    @ApiResponse(responseCode = "200", description = "User found")
    @ApiResponse(responseCode = "404", description = "User not found")
    @GetMapping("/email/{email}")
    public ResponseEntity<UserResponse> getUserByEmail(@PathVariable String email) {
        return userService.findByEmail(email)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Get user by username")
    @ApiResponse(responseCode = "200", description = "User found")
    @ApiResponse(responseCode = "404", description = "User not found")
    @GetMapping("/username/{username}")
    public ResponseEntity<UserResponse> getUserByUsername(@PathVariable String username) {
        return userService.findByUsername(username)
                .map(u -> ResponseEntity.ok(UserResponse.from(u)))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Update user profile fields")
    @ApiResponse(responseCode = "200", description = "Profile updated")
    @ApiResponse(responseCode = "404", description = "User not found")
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

    @Operation(summary = "Deactivate (soft-delete) a user")
    @ApiResponse(responseCode = "204", description = "User deactivated")
    @ApiResponse(responseCode = "404", description = "User not found")
    @PutMapping("/{id}/deactivate")
    public ResponseEntity<Void> deactivateUser(@PathVariable UUID id) {
        try {
            userService.deactivateUser(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @Operation(summary = "Mark user email as verified")
    @ApiResponse(responseCode = "204", description = "User verified")
    @ApiResponse(responseCode = "404", description = "User not found")
    @PutMapping("/{id}/verify")
    public ResponseEntity<Void> markUserVerified(@PathVariable UUID id) {
        try {
            userService.markUserVerified(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @Operation(summary = "Verify password (internal)", description = "Called by auth-service to verify BCrypt hash during login. Not exposed publicly.")
    @ApiResponse(responseCode = "200", description = "Returns true if password matches, false otherwise")
    @PostMapping("/verify-password")
    public ResponseEntity<Boolean> verifyPassword(@RequestBody Map<String, String> body) {
        String email = body.get("email");
        String password = body.get("password");

        if (email == null || password == null) {
            return ResponseEntity.badRequest().build();
        }

        boolean match = userService.verifyPassword(email, password);
        return ResponseEntity.ok(match);
    }
}
