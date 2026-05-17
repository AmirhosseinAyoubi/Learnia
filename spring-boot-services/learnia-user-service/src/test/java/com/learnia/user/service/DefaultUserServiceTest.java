package com.learnia.user.service;

import com.learnia.user.model.User;
import com.learnia.user.model.UserRole;
import com.learnia.user.repository.UserRepository;
import com.learnia.user.service.dto.UserProfileUpdateRequest;
import com.learnia.user.service.dto.UserRegistrationRequest;
import com.learnia.user.service.impl.DefaultUserService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DefaultUserServiceTest {

    @Mock
    UserRepository userRepository;

    @Mock
    UserActivityService userActivityService;

    @Mock
    PasswordEncoder passwordEncoder;

    @InjectMocks
    DefaultUserService userService;

    @Test
    void registerUser_success_savesAndReturnsUser() {
        UserRegistrationRequest request = registrationRequest("alice@example.com", "alice");

        when(userRepository.existsByEmail("alice@example.com")).thenReturn(false);
        when(userRepository.existsByUsername("alice")).thenReturn(false);

        User saved = buildUser("alice@example.com", "alice");
        when(userRepository.save(any(User.class))).thenReturn(saved);

        User result = userService.registerUser(request);

        assertThat(result.getEmail()).isEqualTo("alice@example.com");
        verify(userActivityService).recordActivity(any(), eq("USER_REGISTERED"), any(), any(), any());
    }

    @Test
    void registerUser_duplicateEmail_throwsException() {
        when(userRepository.existsByEmail("alice@example.com")).thenReturn(true);

        assertThatThrownBy(() -> userService.registerUser(registrationRequest("alice@example.com", "alice")))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Email already in use");
    }

    @Test
    void registerUser_duplicateUsername_throwsException() {
        when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
        when(userRepository.existsByUsername("alice")).thenReturn(true);

        assertThatThrownBy(() -> userService.registerUser(registrationRequest("new@example.com", "alice")))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Username already in use");
    }

    @Test
    void findById_existingUser_returnsOptional() {
        User user = buildUser("bob@example.com", "bob");
        when(userRepository.findById(user.getId())).thenReturn(Optional.of(user));

        Optional<User> result = userService.findById(user.getId());

        assertThat(result).isPresent();
        assertThat(result.get().getUsername()).isEqualTo("bob");
    }

    @Test
    void findById_missing_returnsEmpty() {
        UUID id = UUID.randomUUID();
        when(userRepository.findById(id)).thenReturn(Optional.empty());

        assertThat(userService.findById(id)).isEmpty();
    }

    @Test
    void updateProfile_existingUser_updatesFields() {
        User user = buildUser("carol@example.com", "carol");
        when(userRepository.findById(user.getId())).thenReturn(Optional.of(user));
        when(userRepository.save(any())).thenReturn(user);

        UserProfileUpdateRequest req = new UserProfileUpdateRequest();
        req.setFirstName("Caroline");
        req.setLastName("Smith");

        User result = userService.updateProfile(user.getId(), req);

        assertThat(result.getFirstName()).isEqualTo("Caroline");
        verify(userActivityService).recordActivity(any(), eq("USER_PROFILE_UPDATED"), any(), any(), any());
    }

    @Test
    void updateProfile_unknownUser_throwsException() {
        UUID id = UUID.randomUUID();
        when(userRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userService.updateProfile(id, new UserProfileUpdateRequest()))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("User not found");
    }

    @Test
    void deactivateUser_activeUser_setsInactive() {
        User user = buildUser("dave@example.com", "dave");
        user.setIsActive(true);
        when(userRepository.findById(user.getId())).thenReturn(Optional.of(user));
        when(userRepository.save(any())).thenReturn(user);

        userService.deactivateUser(user.getId());

        assertThat(user.getIsActive()).isFalse();
        verify(userActivityService).recordActivity(any(), eq("USER_DEACTIVATED"), any(), any(), any());
    }

    @Test
    void verifyPassword_correctPassword_returnsTrue() {
        User user = buildUser("eve@example.com", "eve");
        user.setPasswordHash("$2a$hashed");
        when(userRepository.findByEmail("eve@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("rawPassword", "$2a$hashed")).thenReturn(true);

        assertThat(userService.verifyPassword("eve@example.com", "rawPassword")).isTrue();
    }

    @Test
    void verifyPassword_wrongPassword_returnsFalse() {
        User user = buildUser("eve@example.com", "eve");
        user.setPasswordHash("$2a$hashed");
        when(userRepository.findByEmail("eve@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("wrong", "$2a$hashed")).thenReturn(false);

        assertThat(userService.verifyPassword("eve@example.com", "wrong")).isFalse();
    }

    @Test
    void verifyPassword_unknownUser_returnsFalse() {
        when(userRepository.findByEmail("ghost@example.com")).thenReturn(Optional.empty());

        assertThat(userService.verifyPassword("ghost@example.com", "anything")).isFalse();
    }

    private User buildUser(String email, String username) {
        User u = new User();
        u.setId(UUID.randomUUID());
        u.setEmail(email);
        u.setUsername(username);
        u.setPasswordHash("hash");
        u.setFirstName("First");
        u.setLastName("Last");
        u.setRole(UserRole.STUDENT);
        u.setIsActive(true);
        u.setIsVerified(false);
        return u;
    }

    private UserRegistrationRequest registrationRequest(String email, String username) {
        UserRegistrationRequest r = new UserRegistrationRequest();
        r.setEmail(email);
        r.setUsername(username);
        r.setPassword("Password1!");
        r.setFirstName("First");
        r.setLastName("Last");
        return r;
    }
}
