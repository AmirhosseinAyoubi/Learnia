package com.learnia.user.config;

import com.learnia.user.model.User;
import com.learnia.user.model.UserRole;
import com.learnia.user.repository.UserRepository;
import com.learnia.user.service.UserActivityService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class UserDataInitializer {

    private static final Logger log = LoggerFactory.getLogger(UserDataInitializer.class);

    @Bean
    CommandLineRunner initUserData(UserRepository userRepository,
                                   UserActivityService userActivityService,
                                   PasswordEncoder passwordEncoder) {
        return args -> {
            long userCount = userRepository.count();
            if (userCount >= 3) {
                log.info("User data already present ({} users). Skipping seeding.", userCount);
                return;
            }

            log.info("Seeding initial user data. Current users={}", userCount);

            // For now, we store placeholder hashes; real hashing is done in the auth service.
            User admin = new User();
            admin.setEmail("admin@learnia.local");
            admin.setUsername("admin");
            admin.setPasswordHash(passwordEncoder.encode("Admin123!"));
            admin.setFirstName("Admin");
            admin.setLastName("User");
            admin.setRole(UserRole.ADMIN);
            admin.setIsActive(true);
            admin.setIsVerified(true);
            admin = userRepository.save(admin);


            User student = new User();
            student.setEmail("student@learnia.local");
            student.setUsername("student");
            student.setPasswordHash(passwordEncoder.encode("User123!"));
            student.setFirstName("John");
            student.setLastName("Student");
            student.setRole(UserRole.STUDENT);
            student.setIsActive(true);
            student.setIsVerified(false);
            student = userRepository.save(student);

            userActivityService.recordActivity(
                    admin.getId(),
                    "USER_REGISTERED",
                    "USER",
                    admin.getId(),
                    null
            );

            userActivityService.recordActivity(
                    student.getId(),
                    "USER_REGISTERED",
                    "USER",
                    student.getId(),
                    null
            );

            log.info("Finished seeding initial user data. New users={}", userRepository.count());
        };
    }
}

