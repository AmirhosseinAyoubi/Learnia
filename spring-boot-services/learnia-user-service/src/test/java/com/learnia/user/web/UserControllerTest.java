package com.learnia.user.web;

import com.learnia.user.model.User;
import com.learnia.user.model.UserRole;
import com.learnia.user.service.UserService;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.SecurityFilterAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
        value = UserController.class,
        excludeAutoConfiguration = {SecurityAutoConfiguration.class, SecurityFilterAutoConfiguration.class}
)
class UserControllerTest {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    UserService userService;

    @Test
    void registerUser_success_returnsCreated() throws Exception {
        User user = buildUser("alice@example.com", "alice");
        when(userService.registerUser(any(UserRegistrationRequest.class))).thenReturn(user);

        mockMvc.perform(post("/api/v1/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"email":"alice@example.com","username":"alice",
                                 "password":"Secret1!","firstName":"Alice","lastName":"Smith"}
                                """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value("alice@example.com"))
                .andExpect(jsonPath("$.username").value("alice"));
    }

    @Test
    void registerUser_duplicateEmail_returnsConflict() throws Exception {
        when(userService.registerUser(any())).thenThrow(new IllegalArgumentException("Email already in use"));

        mockMvc.perform(post("/api/v1/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"x@x.com\",\"username\":\"x\",\"password\":\"p\",\"firstName\":\"F\",\"lastName\":\"L\"}"))
                .andExpect(status().isConflict());
    }

    @Test
    void getUserById_found_returnsOk() throws Exception {
        User user = buildUser("bob@example.com", "bob");
        when(userService.findById(user.getId())).thenReturn(Optional.of(user));

        mockMvc.perform(get("/api/v1/users/" + user.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("bob"));
    }

    @Test
    void getUserById_notFound_returns404() throws Exception {
        UUID id = UUID.randomUUID();
        when(userService.findById(id)).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/users/" + id))
                .andExpect(status().isNotFound());
    }

    @Test
    void getUserByEmail_found_returnsOk() throws Exception {
        User user = buildUser("carol@example.com", "carol");
        when(userService.findByEmail("carol@example.com")).thenReturn(Optional.of(user));

        mockMvc.perform(get("/api/v1/users/email/carol@example.com"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("carol@example.com"));
    }

    @Test
    void updateProfile_success_returnsUpdatedUser() throws Exception {
        User user = buildUser("dave@example.com", "dave");
        when(userService.updateProfile(eq(user.getId()), any(UserProfileUpdateRequest.class))).thenReturn(user);

        mockMvc.perform(put("/api/v1/users/" + user.getId() + "/profile")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"David\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("dave"));
    }

    @Test
    void updateProfile_userNotFound_returns404() throws Exception {
        UUID id = UUID.randomUUID();
        when(userService.updateProfile(eq(id), any())).thenThrow(new IllegalArgumentException("User not found"));

        mockMvc.perform(put("/api/v1/users/" + id + "/profile")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"X\"}"))
                .andExpect(status().isNotFound());
    }

    @Test
    void deactivateUser_success_returnsNoContent() throws Exception {
        User user = buildUser("eve@example.com", "eve");

        mockMvc.perform(put("/api/v1/users/" + user.getId() + "/deactivate"))
                .andExpect(status().isNoContent());
    }

    @Test
    void deactivateUser_notFound_returns404() throws Exception {
        UUID id = UUID.randomUUID();
        doThrow(new IllegalArgumentException("User not found")).when(userService).deactivateUser(id);

        mockMvc.perform(put("/api/v1/users/" + id + "/deactivate"))
                .andExpect(status().isNotFound());
    }

    @Test
    void verifyPassword_correctCredentials_returnsTrue() throws Exception {
        when(userService.verifyPassword("alice@example.com", "correct")).thenReturn(true);

        mockMvc.perform(post("/api/v1/users/verify-password")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"alice@example.com\",\"password\":\"correct\"}"))
                .andExpect(status().isOk())
                .andExpect(content().string("true"));
    }

    @Test
    void verifyPassword_wrongPassword_returnsFalse() throws Exception {
        when(userService.verifyPassword("alice@example.com", "wrong")).thenReturn(false);

        mockMvc.perform(post("/api/v1/users/verify-password")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"alice@example.com\",\"password\":\"wrong\"}"))
                .andExpect(status().isOk())
                .andExpect(content().string("false"));
    }

    private User buildUser(String email, String username) {
        User u = new User();
        u.setId(UUID.randomUUID());
        u.setEmail(email);
        u.setUsername(username);
        u.setPasswordHash("$2a$hash");
        u.setFirstName("First");
        u.setLastName("Last");
        u.setRole(UserRole.STUDENT);
        u.setIsActive(true);
        u.setIsVerified(false);
        u.setCreatedAt(LocalDateTime.now());
        u.setUpdatedAt(LocalDateTime.now());
        return u;
    }
}
