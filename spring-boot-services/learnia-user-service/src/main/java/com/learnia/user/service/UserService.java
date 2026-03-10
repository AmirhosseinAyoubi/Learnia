package com.learnia.user.service;

import com.learnia.user.model.User;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;

import java.util.Optional;
import java.util.UUID;

public interface UserService {

    User registerUser(UserRegistrationRequest request);

    Optional<User> findById(UUID id);

    Optional<User> findByEmail(String email);

    Optional<User> findByUsername(String username);

    User updateProfile(UUID userId, UserProfileUpdateRequest request);

    void deactivateUser(UUID userId);

    void markUserVerified(UUID userId);

    /**
     * Verifies that rawPassword matches the stored BCrypt hash for the given email.
     * Returns false (not an exception) if the user does not exist.
     */
    boolean verifyPassword(String email, String rawPassword);
}
