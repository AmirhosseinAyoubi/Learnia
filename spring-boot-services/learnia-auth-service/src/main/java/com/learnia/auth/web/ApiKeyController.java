package com.learnia.auth.web;

import com.learnia.auth.model.ApiKey;
import com.learnia.auth.repository.ApiKeyRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Tag(name = "API Keys", description = "Manage and validate API keys for stateless authentication")
@RestController
@RequestMapping("/api/v1/auth")
public class ApiKeyController {

    private final ApiKeyRepository apiKeyRepository;

    public ApiKeyController(ApiKeyRepository apiKeyRepository) {
        this.apiKeyRepository = apiKeyRepository;
    }

    @Operation(summary = "Create a new API key", description = "Generates a new API key for the given userId")
    @ApiResponse(responseCode = "201", description = "API key created")
    @ApiResponse(responseCode = "400", description = "Missing userId")
    @PostMapping("/keys")
    public ResponseEntity<Map<String, Object>> createKey(@RequestBody Map<String, String> body) {
        String userIdStr = body.get("userId");
        if (!StringUtils.hasText(userIdStr)) {
            return ResponseEntity.badRequest().body(Map.of("error", "userId is required"));
        }

        ApiKey apiKey = new ApiKey();
        apiKey.setUserId(UUID.fromString(userIdStr));
        apiKey.setKeyValue(UUID.randomUUID().toString().replace("-", "")
                + UUID.randomUUID().toString().replace("-", ""));
        apiKey.setNote(body.getOrDefault("note", ""));

        ApiKey saved = apiKeyRepository.save(apiKey);

        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "id",     saved.getId().toString(),
                "key",    saved.getKeyValue(),
                "userId", saved.getUserId().toString(),
                "note",   saved.getNote() != null ? saved.getNote() : ""
        ));
    }

    @Operation(summary = "List API keys for a user")
    @ApiResponse(responseCode = "200", description = "List of API keys")
    @GetMapping("/keys")
    public ResponseEntity<List<ApiKey>> listKeys(@RequestParam UUID userId) {
        return ResponseEntity.ok(apiKeyRepository.findByUserId(userId));
    }

    @Operation(summary = "Revoke an API key", description = "Marks an API key as inactive (soft delete)")
    @ApiResponse(responseCode = "204", description = "Key revoked")
    @ApiResponse(responseCode = "404", description = "Key not found")
    @DeleteMapping("/keys/{id}")
    public ResponseEntity<Void> revokeKey(@PathVariable UUID id) {
        Optional<ApiKey> found = apiKeyRepository.findById(id);
        if (found.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        ApiKey apiKey = found.get();
        apiKey.setActive(false);
        apiKeyRepository.save(apiKey);
        return ResponseEntity.noContent().build();
    }

    @Operation(
            summary = "Validate an API key",
            description = "Called by the gateway to verify X-API-Key before forwarding requests. Returns 200 with userId if valid, 401 otherwise."
    )
    @ApiResponse(responseCode = "200", description = "Key is valid")
    @ApiResponse(responseCode = "401", description = "Key is missing, invalid, or inactive")
    @GetMapping("/validate")
    public ResponseEntity<Map<String, Object>> validateKey(
            @RequestHeader(value = "X-API-Key", required = false) String apiKey) {
        if (!StringUtils.hasText(apiKey)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("valid", false, "error", "Missing X-API-Key header"));
        }
        return apiKeyRepository.findByKeyValueAndActiveTrue(apiKey)
                .map(key -> ResponseEntity.ok(Map.<String, Object>of(
                        "valid", true,
                        "userId", key.getUserId().toString()
                )))
                .orElseGet(() -> ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("valid", false, "error", "Invalid or inactive API key")));
    }
}
