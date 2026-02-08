
\c learnia_course_db;

-- Enrollment Status Enum
CREATE TYPE enrollment_status AS ENUM ('ACTIVE', 'COMPLETED', 'DROPPED');

-- Courses Table
-- Instructor-created courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructor_id UUID NOT NULL,
    category VARCHAR(100),
    thumbnail_url TEXT,
    is_published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Modules Table
-- Course modules (hierarchical structure)
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_modules_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Lessons Table
-- Lessons within modules
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_lessons_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
);

-- Course Enrollments Table
-- Student enrollments in courses
CREATE TABLE course_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    student_id UUID NOT NULL,
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status enrollment_status NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    CONSTRAINT unique_enrollment UNIQUE (course_id, student_id)
);

-- Student Workspaces Table
-- Student-created workspaces for courses (independent per student)
CREATE TABLE student_workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_workspaces_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
);

-- Workspace Documents Table
-- Many-to-many relationship between workspaces and documents
CREATE TABLE workspace_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    document_id UUID NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_workspace_documents_workspace FOREIGN KEY (workspace_id) REFERENCES student_workspaces(id) ON DELETE CASCADE,
    CONSTRAINT unique_workspace_document UNIQUE (workspace_id, document_id)
);

-- Indexes for courses
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX idx_courses_is_published_created_at ON courses(is_published, created_at DESC);
CREATE INDEX idx_courses_category ON courses(category);

-- Indexes for modules
CREATE INDEX idx_modules_course_id_order ON modules(course_id, order_index);
CREATE INDEX idx_modules_course_id ON modules(course_id);

-- Indexes for lessons
CREATE INDEX idx_lessons_module_id_order ON lessons(module_id, order_index);
CREATE INDEX idx_lessons_module_id ON lessons(module_id);

-- Indexes for course_enrollments
CREATE INDEX idx_enrollments_course_id_status ON course_enrollments(course_id, status);
CREATE INDEX idx_enrollments_student_id_status ON course_enrollments(student_id, status);
CREATE INDEX idx_enrollments_student_id ON course_enrollments(student_id);
CREATE INDEX idx_enrollments_enrolled_at ON course_enrollments(enrolled_at DESC);

-- Indexes for student_workspaces
CREATE INDEX idx_workspaces_student_id_created_at ON student_workspaces(student_id, created_at DESC);
CREATE INDEX idx_workspaces_course_id ON student_workspaces(course_id);
CREATE INDEX idx_workspaces_student_id ON student_workspaces(student_id);

-- Indexes for workspace_documents
CREATE INDEX idx_workspace_documents_workspace_id ON workspace_documents(workspace_id);
CREATE INDEX idx_workspace_documents_document_id ON workspace_documents(document_id);
CREATE INDEX idx_workspace_documents_added_at ON workspace_documents(added_at DESC);

-- Comments for documentation
COMMENT ON TABLE courses IS 'Instructor-created courses with hierarchical structure';
COMMENT ON TABLE modules IS 'Course modules containing lessons';
COMMENT ON TABLE lessons IS 'Lessons within modules';
COMMENT ON TABLE course_enrollments IS 'Student enrollments in instructor-created courses';
COMMENT ON TABLE student_workspaces IS 'Student-created independent workspaces for personalized learning';
COMMENT ON TABLE workspace_documents IS 'Many-to-many relationship: documents can belong to multiple workspaces';
COMMENT ON COLUMN student_workspaces.course_id IS 'Optional link to instructor course, NULL for independent student workspaces';
COMMENT ON COLUMN student_workspaces.title IS 'Student-defined course/workspace name';
