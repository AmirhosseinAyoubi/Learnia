
\c learnia_user_db;

-- User Roles Enum
CREATE TYPE user_role AS ENUM ('STUDENT', 'INSTRUCTOR', 'ADMIN');

-- Users Table
-- Core user information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'STUDENT',
    avatar_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- User Activities Table
-- Activity tracking for analytics dashboards
CREATE TABLE user_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Indexes for user_activities
CREATE INDEX idx_user_activities_user_id_created_at ON user_activities(user_id, created_at DESC);
CREATE INDEX idx_user_activities_activity_type_created_at ON user_activities(activity_type, created_at DESC);
CREATE INDEX idx_user_activities_entity_type_id ON user_activities(entity_type, entity_id);
CREATE INDEX idx_user_activities_created_at ON user_activities(created_at DESC);

-- GIN index for JSONB metadata queries
CREATE INDEX idx_user_activities_metadata ON user_activities USING GIN (metadata);

-- Comments for documentation
COMMENT ON TABLE users IS 'Core user information and authentication data';
COMMENT ON TABLE user_activities IS 'Tracks user activities for analytics and dashboards';
COMMENT ON COLUMN users.role IS 'User role: STUDENT, INSTRUCTOR, or ADMIN';
COMMENT ON COLUMN user_activities.activity_type IS 'Type of activity: DOCUMENT_VIEW, QUIZ_ATTEMPT, QUESTION_ASKED, etc.';
COMMENT ON COLUMN user_activities.entity_type IS 'Type of entity: DOCUMENT, QUIZ, QUESTION, WORKSPACE, etc.';
COMMENT ON COLUMN user_activities.metadata IS 'Additional context as JSON: time spent, score, etc.';
