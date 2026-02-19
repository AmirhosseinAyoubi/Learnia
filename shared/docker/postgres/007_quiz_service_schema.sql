

\c learnia_quiz_db;

-- Question Type Enum
CREATE TYPE question_type AS ENUM ('MULTIPLE_CHOICE', 'TRUE_FALSE', 'SHORT_ANSWER');

-- Quizzes Table
-- Quiz definitions
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    document_id UUID,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_ai_generated BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Quiz Questions Table
-- Questions within quizzes
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL,
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL,
    options JSONB,
    correct_answer TEXT NOT NULL,
    points INTEGER NOT NULL DEFAULT 1,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_quiz_questions_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- Quiz Attempts Table
-- Student quiz attempts
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL,
    student_id UUID NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    total_points INTEGER NOT NULL,
    earned_points INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT fk_quiz_attempts_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- Quiz Attempt Answers Table
-- Individual answers in an attempt
CREATE TABLE quiz_attempt_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL,
    question_id UUID NOT NULL,
    answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points_earned INTEGER NOT NULL,
    answered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attempt_answers_attempt FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    CONSTRAINT fk_attempt_answers_question FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
);

-- Indexes for quizzes
CREATE INDEX idx_quizzes_workspace_id_created_at ON quizzes(workspace_id, created_at DESC);
CREATE INDEX idx_quizzes_document_id ON quizzes(document_id);
CREATE INDEX idx_quizzes_is_ai_generated ON quizzes(is_ai_generated);

-- Indexes for quiz_questions
CREATE INDEX idx_quiz_questions_quiz_id_order ON quiz_questions(quiz_id, order_index);
CREATE INDEX idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
CREATE INDEX idx_quiz_questions_question_type ON quiz_questions(question_type);

-- GIN index for JSONB options queries
CREATE INDEX idx_quiz_questions_options ON quiz_questions USING GIN (options);

-- Indexes for quiz_attempts
CREATE INDEX idx_quiz_attempts_quiz_id_completed_at ON quiz_attempts(quiz_id, completed_at DESC);
CREATE INDEX idx_quiz_attempts_student_id_completed_at ON quiz_attempts(student_id, completed_at DESC);
CREATE INDEX idx_quiz_attempts_student_id ON quiz_attempts(student_id);
CREATE INDEX idx_quiz_attempts_started_at ON quiz_attempts(started_at DESC);

-- Indexes for quiz_attempt_answers
CREATE INDEX idx_attempt_answers_attempt_id ON quiz_attempt_answers(attempt_id);
CREATE INDEX idx_attempt_answers_question_id ON quiz_attempt_answers(question_id);
CREATE INDEX idx_attempt_answers_is_correct ON quiz_attempt_answers(is_correct);

-- Comments for documentation
COMMENT ON TABLE quizzes IS 'Quiz definitions, can be AI-generated or manually created';
COMMENT ON TABLE quiz_questions IS 'Questions within quizzes with various types';
COMMENT ON TABLE quiz_attempts IS 'Student quiz attempts with scoring';
COMMENT ON TABLE quiz_attempt_answers IS 'Individual answers provided in a quiz attempt';
COMMENT ON COLUMN quizzes.workspace_id IS 'Reference to workspace ID in course service (UUID)';
COMMENT ON COLUMN quizzes.document_id IS 'Reference to document ID in document service, NULL if quiz is for general course content';
COMMENT ON COLUMN quiz_questions.question_type IS 'Type of question: MULTIPLE_CHOICE, TRUE_FALSE, or SHORT_ANSWER';
COMMENT ON COLUMN quiz_questions.options IS 'JSON object with answer options';
COMMENT ON COLUMN quiz_questions.correct_answer IS 'The correct answer key';
COMMENT ON COLUMN quiz_attempts.score IS 'Percentage score (0.00 to 100.00)';
COMMENT ON COLUMN quiz_attempts.student_id IS 'Reference to user ID in user service (UUID)';
