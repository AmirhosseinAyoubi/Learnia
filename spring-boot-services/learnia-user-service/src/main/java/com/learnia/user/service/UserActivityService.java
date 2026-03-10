package com.learnia.user.service;

import com.learnia.user.model.UserActivity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.Map;
import java.util.UUID;

public interface UserActivityService {

    void recordActivity(UUID userId,
                        String activityType,
                        String entityType,
                        UUID entityId,
                        Map<String, Object> metadata);

    Page<UserActivity> getRecentActivities(UUID userId, Pageable pageable);
}

