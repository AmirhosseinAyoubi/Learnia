package com.learnia.user.service.impl;

import com.learnia.user.model.User;
import com.learnia.user.model.UserRole;
import com.learnia.user.repository.UserRepository;
import com.learnia.user.service.UserActivityService;
import com.learnia.user.service.UserService;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class DefaultUserService implements UserService {

    private static final Logger log = LoggerFactory.getLogger(DefaultUserService.class);

    private final UserRepository userRepository;
    private final UserActivityService userActivityService;
    private final PasswordEncoder passwordEncoder;

    public DefaultUserService(UserRepository userRepository,
            UserActivityService userActivityService,
            PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.userActivityService = userActivityService;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public User registerUser(UserRegistrationRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already in use");
        }
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already in use");
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setUsername(request.getUsername());
        user.setPasswordHash(request.getPassword()); // already hashed by auth-service
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setAvatarUrl(request.getAvatarUrl());
        user.setRole(UserRole.STUDENT);
        user.setIsActive(true);
        user.setIsVerified(false);

        User saved = userRepository.save(user);

        userActivityService.recordActivity(saved.getId(), "USER_REGISTERED", "USER", saved.getId(), null);
        log.info("Registered new user id={} email={}", saved.getId(), saved.getEmail());
        return saved;
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<User> findById(UUID id) {
        return userRepository.findById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    @Override
    public User updateProfile(UUID userId, UserProfileUpdateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (request.getFirstName() != null)
            user.setFirstName(request.getFirstName());
        if (request.getLastName() != null)
            user.setLastName(request.getLastName());
        if (request.getAvatarUrl() != null)
            user.setAvatarUrl(request.getAvatarUrl());

        User saved = userRepository.save(user);
        userActivityService.recordActivity(saved.getId(), "USER_PROFILE_UPDATED", "USER", saved.getId(), null);
        log.info("Updated profile for user id={}", saved.getId());
        return saved;
    }

    @Override
    public void deactivateUser(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (!Boolean.FALSE.equals(user.getIsActive())) {
            user.setIsActive(false);
            userRepository.save(user);
            userActivityService.recordActivity(user.getId(), "USER_DEACTIVATED", "USER", user.getId(), null);
            log.info("Deactivated user id={}", user.getId());
        }
    }

    @Override
    public void markUserVerified(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (!Boolean.TRUE.equals(user.getIsVerified())) {
            user.setIsVerified(true);
            userRepository.save(user);
            userActivityService.recordActivity(user.getId(), "USER_VERIFIED", "USER", user.getId(), null);
            log.info("Marked user id={} as verified", user.getId());
        }
    }

    /**
     * Verifies that the submitted rawPassword matches the BCrypt hash stored for
     * the given email.
     *
     * The hash was created by auth-service at registration time and stored here.
     * This method is called by auth-service over Feign at login time (so the hash
     * never leaves user-service over the API).
     *
     * Returns false if the user does not exist so callers can treat missing user
     * and wrong password the same way (no user-enumeration).
     */
    @Override
    @Transactional(readOnly = true)
    public boolean verifyPassword(String email, String rawPassword) {
        return userRepository.findByEmail(email)
                .map(user -> passwordEncoder.matches(rawPassword, user.getPasswordHash()))
                .orElse(false);
    }
}
