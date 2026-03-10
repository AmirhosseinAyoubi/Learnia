package com.learnia.auth.service.impl;

import com.learnia.auth.model.BlacklistedToken;
import com.learnia.auth.model.RefreshToken;
import com.learnia.auth.repository.BlacklistedTokenRepository;
import com.learnia.auth.repository.RefreshTokenRepository;
import com.learnia.auth.service.JwtService;
import com.learnia.auth.service.TokenService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class DefaultTokenService implements TokenService {

    private static final Logger log = LoggerFactory.getLogger(DefaultTokenService.class);

    private final RefreshTokenRepository refreshTokenRepository;
    private final BlacklistedTokenRepository blacklistedTokenRepository;
    private final JwtService jwtService;

    public DefaultTokenService(RefreshTokenRepository refreshTokenRepository,
            BlacklistedTokenRepository blacklistedTokenRepository,
            JwtService jwtService) {
        this.refreshTokenRepository = refreshTokenRepository;
        this.blacklistedTokenRepository = blacklistedTokenRepository;
        this.jwtService = jwtService;
    }

    /** Delegates to JwtService to generate a signed HS256 access token. */
    @Override
    public String generateAccessToken(UUID userId, String email, String role) {
        return jwtService.generateToken(userId, email, role);
    }

    @Override
    public RefreshToken createRefreshToken(UUID userId, Duration ttl) {
        LocalDateTime now = LocalDateTime.now();

        RefreshToken token = new RefreshToken();
        token.setUserId(userId);
        token.setToken(UUID.randomUUID().toString());
        token.setExpiresAt(now.plus(ttl));

        RefreshToken saved = refreshTokenRepository.save(token);
        log.debug("Created refresh token id={} for userId={}", saved.getId(), userId);
        return saved;
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<RefreshToken> findRefreshToken(String token) {
        return refreshTokenRepository.findByToken(token);
    }

    @Override
    public void revokeRefreshToken(String token) {
        refreshTokenRepository.findByToken(token).ifPresent(rt -> {
            if (!rt.isRevoked()) {
                rt.setRevokedAt(LocalDateTime.now());
                refreshTokenRepository.save(rt);
                log.debug("Revoked refresh token id={}", rt.getId());
            }
        });
    }

    @Override
    public void revokeAllTokensForUser(UUID userId) {
        refreshTokenRepository.findByUserId(userId).stream()
                .filter(rt -> !rt.isRevoked())
                .forEach(rt -> {
                    rt.setRevokedAt(LocalDateTime.now());
                    refreshTokenRepository.save(rt);
                });
        log.debug("Revoked all refresh tokens for userId={}", userId);
    }

    @Override
    public BlacklistedToken blacklistAccessToken(String tokenHash, Duration remainingTtl) {
        LocalDateTime now = LocalDateTime.now();

        BlacklistedToken blacklistedToken = new BlacklistedToken();
        blacklistedToken.setTokenHash(tokenHash);
        blacklistedToken.setExpiresAt(now.plus(remainingTtl));

        BlacklistedToken saved = blacklistedTokenRepository.save(blacklistedToken);
        log.debug("Blacklisted access token hash={} until={}", tokenHash, saved.getExpiresAt());
        return saved;
    }

    @Override
    @Transactional(readOnly = true)
    public boolean isAccessTokenBlacklisted(String tokenHash) {
        return blacklistedTokenRepository.findByTokenHash(tokenHash)
                .filter(bt -> bt.getExpiresAt().isAfter(LocalDateTime.now()))
                .isPresent();
    }

    @Override
    public void purgeExpired() {
        LocalDateTime now = LocalDateTime.now();

        blacklistedTokenRepository.findAll().stream()
                .filter(bt -> bt.getExpiresAt().isBefore(now))
                .forEach(bt -> blacklistedTokenRepository.deleteById(bt.getId()));

        refreshTokenRepository.findAll().stream()
                .filter(rt -> rt.getExpiresAt().isBefore(now))
                .forEach(rt -> refreshTokenRepository.deleteById(rt.getId()));

        log.debug("Purged expired tokens at {}", now);
    }
}
