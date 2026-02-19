
\c learnia_quiz_db;
TRUNCATE quiz_attempt_answers, quiz_attempts, quiz_questions, quizzes RESTART IDENTITY CASCADE;

\c learnia_question_db;
TRUNCATE answers, questions RESTART IDENTITY CASCADE;

\c learnia_content_db;
TRUNCATE embeddings, content_chunks RESTART IDENTITY CASCADE;

\c learnia_document_db;
TRUNCATE document_processing_jobs, documents RESTART IDENTITY CASCADE;

\c learnia_course_db;
TRUNCATE workspace_documents, student_workspaces, lessons, modules, courses RESTART IDENTITY CASCADE;

\c learnia_user_db;
TRUNCATE user_activities, users RESTART IDENTITY CASCADE;

\c learnia_auth_db;
TRUNCATE blacklisted_tokens, refresh_tokens RESTART IDENTITY CASCADE;

SELECT 'All tables cleared.' AS status;
