package com.learnia.auth.repository;

import com.learnia.auth.model.ApiKey;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ApiKeyRepository extends JpaRepository<ApiKey, UUID> {

    Optional<ApiKey> findByKeyValueAndActiveTrue(String keyValue);

    List<ApiKey> findByUserId(UUID userId);
}
