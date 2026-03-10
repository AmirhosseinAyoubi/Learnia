package com.learnia.user.service.impl;

import com.learnia.user.model.UserActivity;
import com.learnia.user.repository.UserActivityRepository;
import com.learnia.user.service.UserActivityService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.UUID;

@Service
@Transactional
public class DefaultUserActivityService implements UserActivityService {

    private static final Logger log = LoggerFactory.getLogger(DefaultUserActivityService.class);

    private final UserActivityRepository userActivityRepository;

    public DefaultUserActivityService(UserActivityRepository userActivityRepository) {
        this.userActivityRepository = userActivityRepository;
    }

    @Override
    public void recordActivity(UUID userId,
                               String activityType,
                               String entityType,
                               UUID entityId,
                               Map<String, Object> metadata) {
        UserActivity activity = new UserActivity();
        activity.setUserId(userId);
        activity.setActivityType(activityType);
        activity.setEntityType(entityType);
        activity.setEntityId(entityId);
        activity.setMetadata(metadata);

        userActivityRepository.save(activity);

        log.debug("Recorded user activity: userId={}, activityType={}, entityType={}, entityId={}",
                userId, activityType, entityType, entityId);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<UserActivity> getRecentActivities(UUID userId, Pageable pageable) {
        return userActivityRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);
    }
}

