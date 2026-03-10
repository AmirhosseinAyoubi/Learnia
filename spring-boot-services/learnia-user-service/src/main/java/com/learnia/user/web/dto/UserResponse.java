package com.learnia.user.web.dto;

import com.learnia.user.model.UserRole;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * UserResponse — safe DTO returned from UserController.
 *
 * Intentionally omits passwordHash so it is never exposed over HTTP.
 * Map from User entity using UserResponse.from(User).
 */
public class UserResponse {

    private UUID id;
    private String email;
    private String username;
    private String firstName;
    private String lastName;
    private String role;
    private String avatarUrl;
    private Boolean isVerified;
    private Boolean isActive;
    private LocalDateTime createdAt;

    public static UserResponse from(com.learnia.user.model.User user) {
        UserResponse dto = new UserResponse();
        dto.id = user.getId();
        dto.email = user.getEmail();
        dto.username = user.getUsername();
        dto.firstName = user.getFirstName();
        dto.lastName = user.getLastName();
        dto.role = user.getRole() != null ? user.getRole().name() : UserRole.STUDENT.name();
        dto.avatarUrl = user.getAvatarUrl();
        dto.isVerified = user.getIsVerified();
        dto.isActive = user.getIsActive();
        dto.createdAt = user.getCreatedAt();
        return dto;
    }

    public UUID getId() {
        return id;
    }

    public String getEmail() {
        return email;
    }

    public String getUsername() {
        return username;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getRole() {
        return role;
    }

    public String getAvatarUrl() {
        return avatarUrl;
    }

    public Boolean getIsVerified() {
        return isVerified;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
