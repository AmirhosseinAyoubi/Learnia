package com.learnia.auth.client;

import com.learnia.auth.web.dto.UserDto;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * UserServiceClient — Feign client for inter-service calls to
 * learnia-user-service.
 *
 * Spring Cloud automatically routes these calls through Eureka service
 * discovery,
 * so we only need to specify the registered service name.
 * Within Docker Compose all services are on the same "learnia-net" network.
 */
@FeignClient(name = "learnia-user-service")
public interface UserServiceClient {

    /**
     * Lookup a user by email. Throws FeignException.NotFound (404) if not found.
     */
    @GetMapping("/api/v1/users/email/{email}")
    UserDto getUserByEmail(@PathVariable("email") String email);

    /** Lookup a user by ID. Throws FeignException.NotFound (404) if not found. */
    @GetMapping("/api/v1/users/{id}")
    UserDto getUserById(@PathVariable("id") UUID id);

    /** Create a new user. Returns the created UserDto. */
    @PostMapping("/api/v1/users")
    UserDto registerUser(@RequestBody RegistrationRequest request);

    /**
     * Internal password verification endpoint.
     * Returns true if the raw password matches the stored BCrypt hash.
     * This keeps the hash inside user-service and never exposes it over the wire.
     */
    @PostMapping("/api/v1/users/verify-password")
    boolean verifyPassword(@RequestBody VerifyPasswordRequest request);

    // ─── DTOs ────────────────────────────────────────────────────────────────

    class RegistrationRequest {
        private String email;
        private String username;
        private String password;
        private String firstName;
        private String lastName;

        public RegistrationRequest() {
        }

        public RegistrationRequest(String email, String username, String password,
                String firstName, String lastName) {
            this.email = email;
            this.username = username;
            this.password = password;
            this.firstName = firstName;
            this.lastName = lastName;
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

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
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
    }

    class VerifyPasswordRequest {
        private String email;
        private String password;

        public VerifyPasswordRequest() {
        }

        public VerifyPasswordRequest(String email, String password) {
            this.email = email;
            this.password = password;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }
}
