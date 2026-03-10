package com.learnia.auth.repository;

import com.learnia.auth.model.BlacklistedToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface BlacklistedTokenRepository extends JpaRepository<BlacklistedToken, UUID> {

    Optional<BlacklistedToken> findByTokenHash(String tokenHash);
}

