package com.learnia.auth.config;

import com.learnia.auth.model.BlacklistedToken;
import com.learnia.auth.model.RefreshToken;
import com.learnia.auth.repository.BlacklistedTokenRepository;
import com.learnia.auth.repository.RefreshTokenRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDateTime;
import java.util.UUID;

@Configuration
public class AuthDataInitializer {

    private static final Logger log = LoggerFactory.getLogger(AuthDataInitializer.class);

    @Bean
    CommandLineRunner initAuthData(
            RefreshTokenRepository refreshTokenRepository,
            BlacklistedTokenRepository blacklistedTokenRepository
    ) {
        return args -> {
            // Keep this idempotent so local runs don't duplicate data,
            // but also "top up" to at least 5 records when there are fewer.
            long refreshCount = refreshTokenRepository.count();
            long blacklistedCount = blacklistedTokenRepository.count();

            if (refreshCount >= 5 && blacklistedCount >= 5) {
                log.info("Auth data already present ({} refresh tokens, {} blacklisted tokens). Skipping seeding.",
                        refreshCount, blacklistedCount);
            } else {
                log.info("Seeding initial auth data. Current counts: refresh_tokens={}, blacklisted_tokens={}",
                        refreshCount, blacklistedCount);

                // Seed refresh tokens up to 5 total
                for (int i = 1; i <= 5 - refreshCount; i++) {
                    UUID exampleUserId = UUID.randomUUID();

                    RefreshToken refreshToken = new RefreshToken();
                    refreshToken.setUserId(exampleUserId);
                    refreshToken.setToken("dev-sample-refresh-token-" + (refreshCount + i));
                    refreshToken.setExpiresAt(LocalDateTime.now().plusDays(7 + (refreshCount + i)));
                    refreshTokenRepository.save(refreshToken);
                }

                // Seed blacklisted tokens up to 5 total
                for (int i = 1; i <= 5 - blacklistedCount; i++) {
                    BlacklistedToken blacklistedToken = new BlacklistedToken();
                    blacklistedToken.setTokenHash("dev-sample-blacklisted-token-hash-" + (blacklistedCount + i));
                    blacklistedToken.setExpiresAt(LocalDateTime.now().plusDays(blacklistedCount + i));
                    blacklistedTokenRepository.save(blacklistedToken);
                }

                log.info("Finished seeding auth data. New counts: refresh_tokens={}, blacklisted_tokens={}",
                        refreshTokenRepository.count(), blacklistedTokenRepository.count());
            }
        };
    }
}

