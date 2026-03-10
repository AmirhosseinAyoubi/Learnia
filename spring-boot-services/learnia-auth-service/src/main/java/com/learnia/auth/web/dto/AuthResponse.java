package com.learnia.auth.web.dto;

import java.util.UUID;

/**
 * AuthResponse — returned by /login and /register.
 *
 * accessToken : short-lived JWT (15 min) — sent as "Authorization: Bearer" on
 * every API request.
 * refreshToken : long-lived opaque UUID (7 days) — used only to get a new
 * accessToken via /refresh.
 * user : minimal user view so the frontend can render the profile immediately.
 */
public class AuthResponse {

    private String accessToken;
    private String refreshToken;
    private UserView user;

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public UserView getUser() {
        return user;
    }

    public void setUser(UserView user) {
        this.user = user;
    }

    public static class UserView {
        private UUID id;
        private String email;
        private String username;
        private String firstName;
        private String lastName;
        private String role;
        private Boolean isVerified;

        public UUID getId() {
            return id;
        }

        public void setId(UUID id) {
            this.id = id;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getFirstName() {
            return firstName;
        }

        public void setFirstName(String firstName) {
            this.firstName = firstName;
        }

        public String getLastName() {
            return lastName;
        }

        public void setLastName(String lastName) {
            this.lastName = lastName;
        }

        public String getRole() {
            return role;
        }

        public void setRole(String role) {
            this.role = role;
        }

        public Boolean getIsVerified() {
            return isVerified;
        }

        public void setIsVerified(Boolean isVerified) {
            this.isVerified = isVerified;
        }
    }
}
