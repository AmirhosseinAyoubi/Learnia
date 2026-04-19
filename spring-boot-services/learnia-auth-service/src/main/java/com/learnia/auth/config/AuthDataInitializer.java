package com.learnia.auth.config;

import com.learnia.auth.model.ApiKey;
import com.learnia.auth.repository.ApiKeyRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.UUID;

@Configuration
public class AuthDataInitializer {

    private static final Logger log = LoggerFactory.getLogger(AuthDataInitializer.class);

    @Bean
    CommandLineRunner initAuthData(ApiKeyRepository apiKeyRepository) {
        return args -> {
            if (apiKeyRepository.count() > 0) {
                log.info("API keys already present. Skipping seed.");
                return;
            }

            UUID devUserId = UUID.fromString("00000000-0000-0000-0000-000000000001");
            for (int i = 1; i <= 3; i++) {
                ApiKey key = new ApiKey();
                key.setUserId(devUserId);
                key.setKeyValue("dev-api-key-" + i + "-" + UUID.randomUUID().toString().replace("-", ""));
                key.setNote("dev seed key " + i);
                apiKeyRepository.save(key);
            }

            log.info("Seeded 3 dev API keys for userId={}", devUserId);
        };
    }
}
