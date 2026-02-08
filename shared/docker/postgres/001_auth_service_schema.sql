
\c learnia_auth_db;

-- Refresh Tokens Table
-- Stores refresh tokens for JWT rotation
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

-- Blacklisted Tokens Table
-- Stores revoked JWT tokens
CREATE TABLE blacklisted_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    blacklisted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for refresh_tokens
CREATE INDEX idx_refresh_tokens_user_id_expires ON refresh_tokens(user_id, expires_at);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Indexes for blacklisted_tokens
CREATE INDEX idx_blacklisted_tokens_token_hash ON blacklisted_tokens(token_hash);
CREATE INDEX idx_blacklisted_tokens_expires_at ON blacklisted_tokens(expires_at);

-- Comments for documentation
COMMENT ON TABLE refresh_tokens IS 'Stores refresh tokens for JWT token rotation';
COMMENT ON TABLE blacklisted_tokens IS 'Stores revoked JWT tokens that should be rejected';
COMMENT ON COLUMN refresh_tokens.user_id IS 'Reference to user ID in user service (UUID)';
COMMENT ON COLUMN refresh_tokens.revoked_at IS 'Timestamp when token was revoked, NULL if still active';
