package com.learnia.auth.web;

import com.learnia.auth.model.ApiKey;
import com.learnia.auth.repository.ApiKeyRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.SecurityFilterAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
        value = ApiKeyController.class,
        excludeAutoConfiguration = {SecurityAutoConfiguration.class, SecurityFilterAutoConfiguration.class}
)
class ApiKeyControllerTest {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    ApiKeyRepository apiKeyRepository;

    @Test
    void createKey_returnsCreatedWithKeyDetails() throws Exception {
        UUID userId = UUID.randomUUID();
        ApiKey saved = buildKey(userId, "abc123", true);

        when(apiKeyRepository.save(any(ApiKey.class))).thenReturn(saved);

        mockMvc.perform(post("/api/v1/auth/keys")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"userId\":\"" + userId + "\",\"note\":\"test\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.key").value("abc123"))
                .andExpect(jsonPath("$.userId").value(userId.toString()));
    }

    @Test
    void createKey_missingUserId_returnsBadRequest() throws Exception {
        mockMvc.perform(post("/api/v1/auth/keys")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("userId is required"));
    }

    @Test
    void listKeys_returnsKeysForUser() throws Exception {
        UUID userId = UUID.randomUUID();
        when(apiKeyRepository.findByUserId(userId))
                .thenReturn(List.of(buildKey(userId, "key1", true)));

        mockMvc.perform(get("/api/v1/auth/keys").param("userId", userId.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].keyValue").value("key1"));
    }

    @Test
    void revokeKey_existingKey_returnsNoContent() throws Exception {
        UUID keyId = UUID.randomUUID();
        ApiKey key = buildKey(UUID.randomUUID(), "key1", true);
        when(apiKeyRepository.findById(keyId)).thenReturn(Optional.of(key));
        when(apiKeyRepository.save(any())).thenReturn(key);

        mockMvc.perform(delete("/api/v1/auth/keys/" + keyId))
                .andExpect(status().isNoContent());
    }

    @Test
    void revokeKey_notFound_returns404() throws Exception {
        UUID keyId = UUID.randomUUID();
        when(apiKeyRepository.findById(keyId)).thenReturn(Optional.empty());

        mockMvc.perform(delete("/api/v1/auth/keys/" + keyId))
                .andExpect(status().isNotFound());
    }

    @Test
    void validateKey_validKey_returns200WithUserId() throws Exception {
        UUID userId = UUID.randomUUID();
        ApiKey key = buildKey(userId, "validkey", true);
        when(apiKeyRepository.findByKeyValueAndActiveTrue("validkey"))
                .thenReturn(Optional.of(key));

        mockMvc.perform(get("/api/v1/auth/validate").header("X-API-Key", "validkey"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.valid").value(true))
                .andExpect(jsonPath("$.userId").value(userId.toString()));
    }

    @Test
    void validateKey_invalidKey_returns401() throws Exception {
        when(apiKeyRepository.findByKeyValueAndActiveTrue("badkey"))
                .thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/auth/validate").header("X-API-Key", "badkey"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.valid").value(false));
    }

    @Test
    void validateKey_missingHeader_returns401() throws Exception {
        mockMvc.perform(get("/api/v1/auth/validate"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.valid").value(false));
    }

    private ApiKey buildKey(UUID userId, String keyValue, boolean active) {
        ApiKey k = new ApiKey();
        k.setId(UUID.randomUUID());
        k.setUserId(userId);
        k.setKeyValue(keyValue);
        k.setActive(active);
        k.setNote("");
        return k;
    }
}
