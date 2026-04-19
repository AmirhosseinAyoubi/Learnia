package com.learnia.auth.web;

import com.learnia.auth.model.ApiKey;
import com.learnia.auth.repository.ApiKeyRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth/keys")
public class ApiKeyController {

    private final ApiKeyRepository apiKeyRepository;

    public ApiKeyController(ApiKeyRepository apiKeyRepository) {
        this.apiKeyRepository = apiKeyRepository;
    }

    @PostMapping
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

    @GetMapping
    public ResponseEntity<List<ApiKey>> listKeys(@RequestParam UUID userId) {
        return ResponseEntity.ok(apiKeyRepository.findByUserId(userId));
    }

    @DeleteMapping("/{id}")
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
}
