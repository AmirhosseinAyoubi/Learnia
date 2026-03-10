package com.learnia.auth.service;

import com.learnia.auth.model.BlacklistedToken;
import com.learnia.auth.model.RefreshToken;

import java.time.Duration;
import java.util.Optional;
import java.util.UUID;

public interface TokenService {

    /** Generate a signed JWT access token (short-lived). */
    String generateAccessToken(UUID userId, String email, String role);

    RefreshToken createRefreshToken(UUID userId, Duration ttl);

    Optional<RefreshToken> findRefreshToken(String token);

    void revokeRefreshToken(String token);

    void revokeAllTokensForUser(UUID userId);

    BlacklistedToken blacklistAccessToken(String tokenHash, Duration remainingTtl);

    boolean isAccessTokenBlacklisted(String tokenHash);

    void purgeExpired();
}
