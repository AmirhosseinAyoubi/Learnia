
\c learnia_user_db;

-- ---- Users ----
INSERT INTO users (id, email, username, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at) VALUES
  -- Admin
  ('00000000-0000-0000-0000-000000000001', 'admin@learnia.com',          'admin',          '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Admin',   'User',    'ADMIN',      true, true,  NOW() - INTERVAL '180 days', NOW() - INTERVAL '1 day'),
  -- Instructors
  ('00000000-0000-0000-0000-000000000002', 'jane.smith@learnia.com',     'jane_smith',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Jane',    'Smith',    'INSTRUCTOR', true, true,  NOW() - INTERVAL '120 days', NOW() - INTERVAL '5 days'),
  ('00000000-0000-0000-0000-000000000003', 'carlos.mendez@learnia.com',  'carlos_mendez',  '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Carlos',  'Mendez',   'INSTRUCTOR', true, true,  NOW() - INTERVAL '90 days',  NOW() - INTERVAL '3 days'),
  -- Students
  ('00000000-0000-0000-0000-000000000004', 'john.doe@learnia.com',       'john_doe',       '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'John',    'Doe',      'STUDENT',    true, true,  NOW() - INTERVAL '60 days',  NOW() - INTERVAL '2 days'),
  ('00000000-0000-0000-0000-000000000005', 'alice.johnson@learnia.com',  'alice_johnson',  '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Alice',   'Johnson',  'STUDENT',    true, true,  NOW() - INTERVAL '55 days',  NOW() - INTERVAL '1 day'),
  ('00000000-0000-0000-0000-000000000006', 'bob.wilson@learnia.com',     'bob_wilson',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Bob',     'Wilson',   'STUDENT',    true, false, NOW() - INTERVAL '30 days',  NOW() - INTERVAL '30 days'),
  ('00000000-0000-0000-0000-000000000007', 'sara.lee@learnia.com',       'sara_lee',       '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Sara',    'Lee',      'STUDENT',    true, true,  NOW() - INTERVAL '45 days',  NOW() - INTERVAL '4 days')
ON CONFLICT (id) DO NOTHING;

-- ---- User Activities ----
INSERT INTO user_activities (user_id, activity_type, entity_type, entity_id, metadata, created_at) VALUES
  ('00000000-0000-0000-0000-000000000004', 'DOCUMENT_VIEW',  'DOCUMENT', 'dddddddd-0000-0000-0000-000000000001', '{"time_spent": 420, "page": 3}',            NOW() - INTERVAL '10 days'),
  ('00000000-0000-0000-0000-000000000004', 'QUIZ_ATTEMPT',   'QUIZ',     'eeeeeeee-0000-0000-0000-000000000001', '{"score": 90.0, "duration": 900}',           NOW() - INTERVAL '8 days'),
  ('00000000-0000-0000-0000-000000000004', 'QUESTION_ASKED', 'QUESTION', 'ffffffff-0000-0000-0000-000000000001', '{"workspace_id": "cccccccc-0000-0000-0000-000000000001"}', NOW() - INTERVAL '7 days'),
  ('00000000-0000-0000-0000-000000000005', 'DOCUMENT_VIEW',  'DOCUMENT', 'dddddddd-0000-0000-0000-000000000002', '{"time_spent": 600, "page": 5}',            NOW() - INTERVAL '5 days'),
  ('00000000-0000-0000-0000-000000000005', 'QUIZ_ATTEMPT',   'QUIZ',     'eeeeeeee-0000-0000-0000-000000000002', '{"score": 75.0, "duration": 1200}',          NOW() - INTERVAL '3 days'),
  ('00000000-0000-0000-0000-000000000007', 'DOCUMENT_VIEW',  'DOCUMENT', 'dddddddd-0000-0000-0000-000000000003', '{"time_spent": 300, "page": 1}',            NOW() - INTERVAL '2 days'),
  ('00000000-0000-0000-0000-000000000006', 'DOCUMENT_VIEW',  'DOCUMENT', 'dddddddd-0000-0000-0000-000000000001', '{"time_spent": 180, "page": 1}',            NOW() - INTERVAL '1 day')
ON CONFLICT DO NOTHING;



\c learnia_course_db;

-- ---- Courses ----
INSERT INTO courses (id, title, description, instructor_id, category, is_published, created_at, updated_at) VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001', 'Introduction to Database Design',
   'Learn the fundamentals of relational database design, normalization, and SQL from scratch.',
   '00000000-0000-0000-0000-000000000002', 'Computer Science', true,  NOW() - INTERVAL '100 days', NOW() - INTERVAL '10 days'),

  ('aaaaaaaa-0000-0000-0000-000000000002', 'Advanced Python Programming',
   'Master advanced Python concepts: decorators, generators, async/await, and design patterns.',
   '00000000-0000-0000-0000-000000000002', 'Programming',      true,  NOW() - INTERVAL '80 days',  NOW() - INTERVAL '5 days'),

  ('aaaaaaaa-0000-0000-0000-000000000003', 'Machine Learning Fundamentals',
   'A hands-on introduction to machine learning algorithms, model evaluation, and scikit-learn.',
   '00000000-0000-0000-0000-000000000003', 'Data Science',     true,  NOW() - INTERVAL '60 days',  NOW() - INTERVAL '3 days'),

  ('aaaaaaaa-0000-0000-0000-000000000004', 'Web Development with React',
   'Build modern, responsive web applications using React, hooks, and the component model.',
   '00000000-0000-0000-0000-000000000003', 'Web Development',  false, NOW() - INTERVAL '20 days',  NOW() - INTERVAL '1 day')
ON CONFLICT (id) DO NOTHING;

-- ---- Modules ----
INSERT INTO modules (id, course_id, title, description, order_index, created_at, updated_at) VALUES
  -- Course 1: Database Design
  ('bbbbbbbb-0000-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000001', 'Module 1: Database Fundamentals',   'Core concepts of databases and DBMS',          1, NOW() - INTERVAL '99 days', NOW() - INTERVAL '10 days'),
  ('bbbbbbbb-0000-0000-0000-000000000002', 'aaaaaaaa-0000-0000-0000-000000000001', 'Module 2: SQL Basics',              'Writing SELECT, INSERT, UPDATE, DELETE',        2, NOW() - INTERVAL '98 days', NOW() - INTERVAL '10 days'),
  ('bbbbbbbb-0000-0000-0000-000000000003', 'aaaaaaaa-0000-0000-0000-000000000001', 'Module 3: Normalization',           '1NF, 2NF, 3NF and BCNF explained',             3, NOW() - INTERVAL '97 days', NOW() - INTERVAL '10 days'),

  -- Course 2: Advanced Python
  ('bbbbbbbb-0000-0000-0000-000000000004', 'aaaaaaaa-0000-0000-0000-000000000002', 'Module 1: Python Advanced Features','Decorators, generators, context managers',     1, NOW() - INTERVAL '79 days', NOW() - INTERVAL '5 days'),
  ('bbbbbbbb-0000-0000-0000-000000000005', 'aaaaaaaa-0000-0000-0000-000000000002', 'Module 2: Async Programming',       'asyncio, aiohttp, and concurrency patterns',   2, NOW() - INTERVAL '78 days', NOW() - INTERVAL '5 days'),

  -- Course 3: Machine Learning
  ('bbbbbbbb-0000-0000-0000-000000000006', 'aaaaaaaa-0000-0000-0000-000000000003', 'Module 1: ML Basics',               'Supervised vs unsupervised learning',          1, NOW() - INTERVAL '59 days', NOW() - INTERVAL '3 days'),
  ('bbbbbbbb-0000-0000-0000-000000000007', 'aaaaaaaa-0000-0000-0000-000000000003', 'Module 2: Model Evaluation',        'Cross-validation, metrics, and overfitting',   2, NOW() - INTERVAL '58 days', NOW() - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Lessons ----
INSERT INTO lessons (id, module_id, title, description, order_index, created_at, updated_at) VALUES
  -- Module 1 (DB Fundamentals)
  ('cccccccc-0000-0000-0000-000000000001', 'bbbbbbbb-0000-0000-0000-000000000001', 'What is a Database?',         'Introduction to databases and DBMS',           1, NOW() - INTERVAL '99 days', NOW() - INTERVAL '10 days'),
  ('cccccccc-0000-0000-0000-000000000002', 'bbbbbbbb-0000-0000-0000-000000000001', 'Relational Model',            'Tables, rows, columns, and relationships',     2, NOW() - INTERVAL '99 days', NOW() - INTERVAL '10 days'),
  ('cccccccc-0000-0000-0000-000000000003', 'bbbbbbbb-0000-0000-0000-000000000001', 'Keys and Constraints',        'Primary keys, foreign keys, and constraints',  3, NOW() - INTERVAL '99 days', NOW() - INTERVAL '10 days'),
  -- Module 2 (SQL Basics)
  ('cccccccc-0000-0000-0000-000000000004', 'bbbbbbbb-0000-0000-0000-000000000002', 'SELECT Statements',           'Retrieving data with SELECT',                  1, NOW() - INTERVAL '98 days', NOW() - INTERVAL '10 days'),
  ('cccccccc-0000-0000-0000-000000000005', 'bbbbbbbb-0000-0000-0000-000000000002', 'Filtering and Sorting',       'WHERE, ORDER BY, and LIMIT clauses',           2, NOW() - INTERVAL '98 days', NOW() - INTERVAL '10 days'),
  ('cccccccc-0000-0000-0000-000000000006', 'bbbbbbbb-0000-0000-0000-000000000002', 'Joins',                       'INNER, LEFT, RIGHT, and FULL JOINs',           3, NOW() - INTERVAL '98 days', NOW() - INTERVAL '10 days'),
  -- Module 3 (Normalization)
  ('cccccccc-0000-0000-0000-000000000007', 'bbbbbbbb-0000-0000-0000-000000000003', 'First Normal Form (1NF)',     'Atomic values and eliminating repeating groups', 1, NOW() - INTERVAL '97 days', NOW() - INTERVAL '10 days'),
  ('cccccccc-0000-0000-0000-000000000008', 'bbbbbbbb-0000-0000-0000-000000000003', 'Second & Third Normal Form', '2NF and 3NF with practical examples',           2, NOW() - INTERVAL '97 days', NOW() - INTERVAL '10 days'),
  -- Module 4 (Python Advanced)
  ('cccccccc-0000-0000-0000-000000000009', 'bbbbbbbb-0000-0000-0000-000000000004', 'Decorators Deep Dive',        'Writing and stacking decorators',              1, NOW() - INTERVAL '79 days', NOW() - INTERVAL '5 days'),
  ('cccccccc-0000-0000-0000-000000000010', 'bbbbbbbb-0000-0000-0000-000000000004', 'Generators and Iterators',    'yield, generator expressions, itertools',      2, NOW() - INTERVAL '79 days', NOW() - INTERVAL '5 days'),
  -- Module 5 (Async)
  ('cccccccc-0000-0000-0000-000000000011', 'bbbbbbbb-0000-0000-0000-000000000005', 'asyncio Basics',              'Event loop, coroutines, and tasks',            1, NOW() - INTERVAL '78 days', NOW() - INTERVAL '5 days'),
  -- Module 6 (ML Basics)
  ('cccccccc-0000-0000-0000-000000000012', 'bbbbbbbb-0000-0000-0000-000000000006', 'Supervised Learning',         'Regression and classification algorithms',     1, NOW() - INTERVAL '59 days', NOW() - INTERVAL '3 days'),
  ('cccccccc-0000-0000-0000-000000000013', 'bbbbbbbb-0000-0000-0000-000000000006', 'Unsupervised Learning',       'Clustering and dimensionality reduction',      2, NOW() - INTERVAL '59 days', NOW() - INTERVAL '3 days'),
  -- Module 7 (Model Evaluation)
  ('cccccccc-0000-0000-0000-000000000014', 'bbbbbbbb-0000-0000-0000-000000000007', 'Evaluation Metrics',          'Accuracy, precision, recall, F1, AUC-ROC',    1, NOW() - INTERVAL '58 days', NOW() - INTERVAL '3 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Course Enrollments ----
INSERT INTO course_enrollments (id, course_id, student_id, enrolled_at, status) VALUES
  ('11111111-0000-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', NOW() - INTERVAL '50 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000002', 'aaaaaaaa-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000004', NOW() - INTERVAL '45 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000003', 'aaaaaaaa-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000005', NOW() - INTERVAL '40 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000004', 'aaaaaaaa-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000005', NOW() - INTERVAL '35 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000005', 'aaaaaaaa-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000007', NOW() - INTERVAL '30 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000006', 'aaaaaaaa-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000007', NOW() - INTERVAL '25 days', 'COMPLETED'),
  ('11111111-0000-0000-0000-000000000007', 'aaaaaaaa-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000006', NOW() - INTERVAL '20 days', 'ACTIVE'),
  ('11111111-0000-0000-0000-000000000008', 'aaaaaaaa-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000006', NOW() - INTERVAL '15 days', 'DROPPED')
ON CONFLICT (id) DO NOTHING;

-- ---- Student Workspaces ----
INSERT INTO student_workspaces (id, student_id, course_id, title, description, created_at, updated_at) VALUES
  ('cccccccc-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', 'aaaaaaaa-0000-0000-0000-000000000001', 'DB Course Study Hub',         'My personal workspace for the database design course',   NOW() - INTERVAL '50 days', NOW() - INTERVAL '2 days'),
  ('cccccccc-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000004', 'aaaaaaaa-0000-0000-0000-000000000002', 'Python Advanced Notes',       'Workspace for advanced Python course materials',         NOW() - INTERVAL '45 days', NOW() - INTERVAL '1 day'),
  ('cccccccc-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000005', 'aaaaaaaa-0000-0000-0000-000000000001', 'SQL Practice Workspace',      'Practicing SQL queries and exercises',                   NOW() - INTERVAL '40 days', NOW() - INTERVAL '3 days'),
  ('cccccccc-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000005', 'aaaaaaaa-0000-0000-0000-000000000003', 'ML Research Workspace',       'Exploring ML papers and course content',                 NOW() - INTERVAL '35 days', NOW() - INTERVAL '2 days'),
  ('cccccccc-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000007', NULL,                                   'Self-Study: Algorithms',      'Independent workspace for algorithm study',              NOW() - INTERVAL '20 days', NOW() - INTERVAL '1 day'),
  ('cccccccc-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000006', 'aaaaaaaa-0000-0000-0000-000000000003', 'ML Beginner Notes',           'Getting started with machine learning',                  NOW() - INTERVAL '18 days', NOW() - INTERVAL '5 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Workspace Documents (many-to-many) ----
INSERT INTO workspace_documents (id, workspace_id, document_id, added_at) VALUES
  ('22222222-0000-0000-0000-000000000001', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000001', NOW() - INTERVAL '49 days'),
  ('22222222-0000-0000-0000-000000000002', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000002', NOW() - INTERVAL '48 days'),
  ('22222222-0000-0000-0000-000000000003', 'cccccccc-0000-0000-0000-000000000002', 'dddddddd-0000-0000-0000-000000000003', NOW() - INTERVAL '44 days'),
  ('22222222-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000003', 'dddddddd-0000-0000-0000-000000000001', NOW() - INTERVAL '39 days'),
  ('22222222-0000-0000-0000-000000000005', 'cccccccc-0000-0000-0000-000000000004', 'dddddddd-0000-0000-0000-000000000004', NOW() - INTERVAL '34 days'),
  ('22222222-0000-0000-0000-000000000006', 'cccccccc-0000-0000-0000-000000000005', 'dddddddd-0000-0000-0000-000000000005', NOW() - INTERVAL '19 days'),
  ('22222222-0000-0000-0000-000000000007', 'cccccccc-0000-0000-0000-000000000006', 'dddddddd-0000-0000-0000-000000000004', NOW() - INTERVAL '17 days')
ON CONFLICT (id) DO NOTHING;


\c learnia_document_db;

-- ---- Documents ----
INSERT INTO documents (id, title, file_name, file_type, file_size, file_url, uploaded_by, workspace_id, processing_status, page_count, created_at, updated_at) VALUES
  ('dddddddd-0000-0000-0000-000000000001', 'Database Design Guide',         'db_design_guide.pdf',         'PDF',  2048576, '/uploads/db_design_guide.pdf',         '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000001', 'COMPLETED', 52,  NOW() - INTERVAL '49 days', NOW() - INTERVAL '49 days'),
  ('dddddddd-0000-0000-0000-000000000002', 'SQL Cheat Sheet',               'sql_cheat_sheet.pdf',         'PDF',  524288,  '/uploads/sql_cheat_sheet.pdf',         '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000001', 'COMPLETED', 10,  NOW() - INTERVAL '48 days', NOW() - INTERVAL '48 days'),
  ('dddddddd-0000-0000-0000-000000000003', 'Python Advanced Topics Slides', 'python_advanced.pptx',        'PPTX', 3145728, '/uploads/python_advanced.pptx',        '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000002', 'COMPLETED', 45,  NOW() - INTERVAL '44 days', NOW() - INTERVAL '44 days'),
  ('dddddddd-0000-0000-0000-000000000004', 'ML Algorithms Overview',        'ml_algorithms_overview.pdf',  'PDF',  1572864, '/uploads/ml_algorithms_overview.pdf',  '00000000-0000-0000-0000-000000000005', 'cccccccc-0000-0000-0000-000000000004', 'COMPLETED', 30,  NOW() - INTERVAL '34 days', NOW() - INTERVAL '34 days'),
  ('dddddddd-0000-0000-0000-000000000005', 'Algorithm Complexity Notes',    'algo_complexity.txt',         'TXT',  102400,  '/uploads/algo_complexity.txt',         '00000000-0000-0000-0000-000000000007', 'cccccccc-0000-0000-0000-000000000005', 'COMPLETED', NULL, NOW() - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
  ('dddddddd-0000-0000-0000-000000000006', 'React Hooks Reference',         'react_hooks_reference.pdf',   'PDF',  786432,  '/uploads/react_hooks_reference.pdf',   '00000000-0000-0000-0000-000000000002', NULL,                                  'PENDING',   NULL, NOW() - INTERVAL '2 days',  NOW() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Document Processing Jobs ----
INSERT INTO document_processing_jobs (id, document_id, status, started_at, completed_at, error_message) VALUES
  ('33333333-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000001', 'COMPLETED',  NOW() - INTERVAL '49 days',                  NOW() - INTERVAL '49 days' + INTERVAL '8 minutes',  NULL),
  ('33333333-0000-0000-0000-000000000002', 'dddddddd-0000-0000-0000-000000000002', 'COMPLETED',  NOW() - INTERVAL '48 days',                  NOW() - INTERVAL '48 days' + INTERVAL '3 minutes',  NULL),
  ('33333333-0000-0000-0000-000000000003', 'dddddddd-0000-0000-0000-000000000003', 'COMPLETED',  NOW() - INTERVAL '44 days',                  NOW() - INTERVAL '44 days' + INTERVAL '12 minutes', NULL),
  ('33333333-0000-0000-0000-000000000004', 'dddddddd-0000-0000-0000-000000000004', 'COMPLETED',  NOW() - INTERVAL '34 days',                  NOW() - INTERVAL '34 days' + INTERVAL '6 minutes',  NULL),
  ('33333333-0000-0000-0000-000000000005', 'dddddddd-0000-0000-0000-000000000005', 'COMPLETED',  NOW() - INTERVAL '19 days',                  NOW() - INTERVAL '19 days' + INTERVAL '1 minute',   NULL),
  ('33333333-0000-0000-0000-000000000006', 'dddddddd-0000-0000-0000-000000000006', 'PROCESSING', NOW() - INTERVAL '2 days',                   NULL,                                               NULL)
ON CONFLICT (id) DO NOTHING;



\c learnia_content_db;

-- ---- Content Chunks ----
INSERT INTO content_chunks (id, document_id, chunk_index, content, page_number, metadata, created_at) VALUES
  -- Document 1: Database Design Guide
  ('44444444-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000001', 1,
   'A database is an organized collection of structured information or data, typically stored electronically in a computer system. A database is usually controlled by a database management system (DBMS).',
   1, '{"section": "introduction", "chapter": 1}', NOW() - INTERVAL '49 days'),

  ('44444444-0000-0000-0000-000000000002', 'dddddddd-0000-0000-0000-000000000001', 2,
   'The relational model organizes data into one or more tables (or "relations") of columns and rows, with a unique key identifying each row. Rows are also called records or tuples. Columns are also called attributes or fields.',
   2, '{"section": "relational_model", "chapter": 1}', NOW() - INTERVAL '49 days'),

  ('44444444-0000-0000-0000-000000000003', 'dddddddd-0000-0000-0000-000000000001', 3,
   'Normalization is the process of organizing a relational database to reduce data redundancy and improve data integrity. It involves dividing large tables into smaller tables and defining relationships between them.',
   15, '{"section": "normalization", "chapter": 3}', NOW() - INTERVAL '49 days'),

  ('44444444-0000-0000-0000-000000000004', 'dddddddd-0000-0000-0000-000000000001', 4,
   'A primary key is a column or set of columns in a table that uniquely identifies each row. A foreign key is a column or set of columns in one table that refers to the primary key in another table.',
   8, '{"section": "keys", "chapter": 2}', NOW() - INTERVAL '49 days'),

  -- Document 2: SQL Cheat Sheet
  ('44444444-0000-0000-0000-000000000005', 'dddddddd-0000-0000-0000-000000000002', 1,
   'SELECT column1, column2 FROM table_name WHERE condition ORDER BY column1 ASC LIMIT 10; — This is the basic structure of a SELECT query in SQL.',
   1, '{"section": "select", "chapter": 1}', NOW() - INTERVAL '48 days'),

  ('44444444-0000-0000-0000-000000000006', 'dddddddd-0000-0000-0000-000000000002', 2,
   'JOIN operations combine rows from two or more tables based on a related column. INNER JOIN returns rows with matching values in both tables. LEFT JOIN returns all rows from the left table and matched rows from the right.',
   5, '{"section": "joins", "chapter": 2}', NOW() - INTERVAL '48 days'),

  -- Document 3: Python Advanced Topics
  ('44444444-0000-0000-0000-000000000007', 'dddddddd-0000-0000-0000-000000000003', 1,
   'A decorator is a design pattern in Python that allows a user to add new functionality to an existing object without modifying its structure. Decorators are usually called before the definition of a function you want to decorate.',
   3, '{"section": "decorators", "slide": 3}', NOW() - INTERVAL '44 days'),

  ('44444444-0000-0000-0000-000000000008', 'dddddddd-0000-0000-0000-000000000003', 2,
   'A generator is a function that returns an iterator that produces a sequence of values when iterated over. Generators are useful when we want to produce a large sequence of values, but we don''t want to store all of them in memory at once.',
   12, '{"section": "generators", "slide": 12}', NOW() - INTERVAL '44 days'),

  -- Document 4: ML Algorithms Overview
  ('44444444-0000-0000-0000-000000000009', 'dddddddd-0000-0000-0000-000000000004', 1,
   'Supervised learning is a type of machine learning where the model is trained on labeled data. The algorithm learns to map input features to output labels. Common algorithms include linear regression, logistic regression, decision trees, and neural networks.',
   1, '{"section": "supervised_learning", "chapter": 1}', NOW() - INTERVAL '34 days'),

  ('44444444-0000-0000-0000-000000000010', 'dddddddd-0000-0000-0000-000000000004', 2,
   'Cross-validation is a technique for evaluating ML models by training several ML models on subsets of the available input data and evaluating them on the complementary subset of the data. K-fold cross-validation is the most common approach.',
   18, '{"section": "model_evaluation", "chapter": 3}', NOW() - INTERVAL '34 days'),

  -- Document 5: Algorithm Complexity Notes
  ('44444444-0000-0000-0000-000000000011', 'dddddddd-0000-0000-0000-000000000005', 1,
   'Big O notation describes the upper bound of an algorithm''s time or space complexity. O(1) is constant time, O(log n) is logarithmic, O(n) is linear, O(n log n) is linearithmic, O(n²) is quadratic.',
   NULL, '{"section": "big_o", "type": "text"}', NOW() - INTERVAL '19 days')
ON CONFLICT (id) DO NOTHING;


\c learnia_question_db;

-- ---- Questions ----
INSERT INTO questions (id, user_id, workspace_id, document_id, title, content, is_resolved, created_at, updated_at) VALUES
  ('ffffffff-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000001',
   'What is database normalization?',
   'I read about normalization in the guide but I am confused about the difference between 2NF and 3NF. Can someone explain with an example?',
   true, NOW() - INTERVAL '45 days', NOW() - INTERVAL '44 days'),

  ('ffffffff-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000002',
   'How do LEFT JOIN and INNER JOIN differ?',
   'I understand the basic concept but I am not sure when to use LEFT JOIN vs INNER JOIN in practice. Can you give a real-world example?',
   true, NOW() - INTERVAL '40 days', NOW() - INTERVAL '39 days'),

  ('ffffffff-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000005', 'cccccccc-0000-0000-0000-000000000003', 'dddddddd-0000-0000-0000-000000000001',
   'What is a composite primary key?',
   'The document mentions composite keys but does not give a clear example. When should I use a composite primary key instead of a surrogate key?',
   false, NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),

  ('ffffffff-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000002', 'dddddddd-0000-0000-0000-000000000003',
   'How do Python decorators work with arguments?',
   'I understand simple decorators but I am confused about how to write a decorator that itself accepts arguments. The slides show an example but it is hard to follow.',
   false, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),

  ('ffffffff-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', 'cccccccc-0000-0000-0000-000000000004', 'dddddddd-0000-0000-0000-000000000004',
   'What is overfitting and how to prevent it?',
   'The ML overview mentions overfitting but I want to understand the practical techniques to prevent it beyond just cross-validation.',
   true, NOW() - INTERVAL '25 days', NOW() - INTERVAL '24 days'),

  ('ffffffff-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000007', 'cccccccc-0000-0000-0000-000000000005', NULL,
   'Difference between O(n log n) and O(n²) in practice?',
   'I understand the theoretical difference but at what input size does the difference become significant in real programs?',
   false, NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Answers ----
INSERT INTO answers (id, question_id, content, is_ai_generated, source_chunks, created_at, updated_at) VALUES
  -- Answer to Q1: normalization
  ('99999999-0000-0000-0000-000000000001', 'ffffffff-0000-0000-0000-000000000001',
   '2NF requires that all non-key attributes are fully dependent on the entire primary key (no partial dependencies). 3NF goes further and requires that all non-key attributes are dependent only on the primary key, not on other non-key attributes (no transitive dependencies). Example: In a table (OrderID, ProductID, ProductName, CustomerName), ProductName depends only on ProductID (partial dependency → violates 2NF). CustomerName depends on OrderID → CustomerName (transitive dependency → violates 3NF).',
   true, '["44444444-0000-0000-0000-000000000003"]', NOW() - INTERVAL '44 days', NOW() - INTERVAL '44 days'),

  -- Answer to Q2: joins
  ('99999999-0000-0000-0000-000000000002', 'ffffffff-0000-0000-0000-000000000002',
   'INNER JOIN returns only the rows where there is a match in both tables. LEFT JOIN returns all rows from the left table, and the matched rows from the right table — if there is no match, NULLs are returned for the right table columns. Use INNER JOIN when you only want records that exist in both tables. Use LEFT JOIN when you want all records from the primary table regardless of whether they have a match.',
   true, '["44444444-0000-0000-0000-000000000006"]', NOW() - INTERVAL '39 days', NOW() - INTERVAL '39 days'),

  -- Answer to Q5: overfitting
  ('99999999-0000-0000-0000-000000000003', 'ffffffff-0000-0000-0000-000000000005',
   'Overfitting occurs when a model learns the training data too well, including noise, and performs poorly on unseen data. Prevention techniques include: (1) Cross-validation to detect overfitting early, (2) Regularization (L1/Lasso, L2/Ridge) to penalize model complexity, (3) Dropout in neural networks, (4) Early stopping during training, (5) Reducing model complexity, (6) Getting more training data, (7) Data augmentation.',
   true, '["44444444-0000-0000-0000-000000000010"]', NOW() - INTERVAL '24 days', NOW() - INTERVAL '24 days'),

  -- Manual answer to Q5
  ('99999999-0000-0000-0000-000000000004', 'ffffffff-0000-0000-0000-000000000005',
   'Great answer above! I would add that ensemble methods like Random Forest and Gradient Boosting are also naturally resistant to overfitting compared to single decision trees.',
   false, NULL, NOW() - INTERVAL '23 days', NOW() - INTERVAL '23 days')
ON CONFLICT (id) DO NOTHING;


\c learnia_quiz_db;

-- ---- Quizzes ----
INSERT INTO quizzes (id, workspace_id, document_id, title, description, is_ai_generated, created_at, updated_at) VALUES
  ('eeeeeeee-0000-0000-0000-000000000001', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000001',
   'Database Design Fundamentals Quiz',
   'Test your understanding of core database design concepts including keys, normalization, and the relational model.',
   true, NOW() - INTERVAL '45 days', NOW() - INTERVAL '45 days'),

  ('eeeeeeee-0000-0000-0000-000000000002', 'cccccccc-0000-0000-0000-000000000001', 'dddddddd-0000-0000-0000-000000000002',
   'SQL Basics Quiz',
   'Practice your SQL knowledge with questions on SELECT, JOIN, and filtering.',
   true, NOW() - INTERVAL '40 days', NOW() - INTERVAL '40 days'),

  ('eeeeeeee-0000-0000-0000-000000000003', 'cccccccc-0000-0000-0000-000000000002', 'dddddddd-0000-0000-0000-000000000003',
   'Python Advanced Concepts Quiz',
   'Questions on decorators, generators, and async programming.',
   true, NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),

  ('eeeeeeee-0000-0000-0000-000000000004', 'cccccccc-0000-0000-0000-000000000004', 'dddddddd-0000-0000-0000-000000000004',
   'Machine Learning Basics Quiz',
   'Evaluate your understanding of supervised learning, model evaluation, and overfitting.',
   false, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days')
ON CONFLICT (id) DO NOTHING;

-- ---- Quiz Questions ----
INSERT INTO quiz_questions (id, quiz_id, question_text, question_type, options, correct_answer, points, order_index, created_at) VALUES
  -- Quiz 1: Database Design
  ('55555555-0000-0000-0000-000000000001', 'eeeeeeee-0000-0000-0000-000000000001',
   'What is a primary key?',
   'MULTIPLE_CHOICE',
   '{"A": "A column that can contain duplicate values", "B": "A column or set of columns that uniquely identifies each row", "C": "A column that references another table", "D": "An index on a table"}',
   'B', 1, 1, NOW() - INTERVAL '45 days'),

  ('55555555-0000-0000-0000-000000000002', 'eeeeeeee-0000-0000-0000-000000000001',
   'A table can have multiple primary keys.',
   'TRUE_FALSE', NULL, 'FALSE', 1, 2, NOW() - INTERVAL '45 days'),

  ('55555555-0000-0000-0000-000000000003', 'eeeeeeee-0000-0000-0000-000000000001',
   'What does normalization aim to reduce in a database?',
   'MULTIPLE_CHOICE',
   '{"A": "Query speed", "B": "Data redundancy", "C": "Table count", "D": "Index size"}',
   'B', 1, 3, NOW() - INTERVAL '45 days'),

  ('55555555-0000-0000-0000-000000000004', 'eeeeeeee-0000-0000-0000-000000000001',
   'Briefly explain what a foreign key is.',
   'SHORT_ANSWER', NULL, 'A column that references the primary key of another table', 2, 4, NOW() - INTERVAL '45 days'),

  -- Quiz 2: SQL Basics
  ('55555555-0000-0000-0000-000000000005', 'eeeeeeee-0000-0000-0000-000000000002',
   'Which SQL clause is used to filter rows?',
   'MULTIPLE_CHOICE',
   '{"A": "ORDER BY", "B": "GROUP BY", "C": "WHERE", "D": "HAVING"}',
   'C', 1, 1, NOW() - INTERVAL '40 days'),

  ('55555555-0000-0000-0000-000000000006', 'eeeeeeee-0000-0000-0000-000000000002',
   'INNER JOIN returns all rows from both tables even if there is no match.',
   'TRUE_FALSE', NULL, 'FALSE', 1, 2, NOW() - INTERVAL '40 days'),

  ('55555555-0000-0000-0000-000000000007', 'eeeeeeee-0000-0000-0000-000000000002',
   'Which JOIN type returns all rows from the left table and matched rows from the right?',
   'MULTIPLE_CHOICE',
   '{"A": "INNER JOIN", "B": "RIGHT JOIN", "C": "LEFT JOIN", "D": "FULL JOIN"}',
   'C', 1, 3, NOW() - INTERVAL '40 days'),

  -- Quiz 3: Python Advanced
  ('55555555-0000-0000-0000-000000000008', 'eeeeeeee-0000-0000-0000-000000000003',
   'What keyword is used to create a generator function in Python?',
   'MULTIPLE_CHOICE',
   '{"A": "return", "B": "yield", "C": "async", "D": "generate"}',
   'B', 1, 1, NOW() - INTERVAL '35 days'),

  ('55555555-0000-0000-0000-000000000009', 'eeeeeeee-0000-0000-0000-000000000003',
   'Decorators can only be applied to functions, not to classes.',
   'TRUE_FALSE', NULL, 'FALSE', 1, 2, NOW() - INTERVAL '35 days'),

  -- Quiz 4: Machine Learning
  ('55555555-0000-0000-0000-000000000010', 'eeeeeeee-0000-0000-0000-000000000004',
   'Which of the following is a supervised learning algorithm?',
   'MULTIPLE_CHOICE',
   '{"A": "K-Means Clustering", "B": "PCA", "C": "Linear Regression", "D": "DBSCAN"}',
   'C', 1, 1, NOW() - INTERVAL '30 days'),

  ('55555555-0000-0000-0000-000000000011', 'eeeeeeee-0000-0000-0000-000000000004',
   'Overfitting occurs when a model performs well on training data but poorly on new data.',
   'TRUE_FALSE', NULL, 'TRUE', 1, 2, NOW() - INTERVAL '30 days'),

  ('55555555-0000-0000-0000-000000000012', 'eeeeeeee-0000-0000-0000-000000000004',
   'Name two techniques to prevent overfitting in machine learning.',
   'SHORT_ANSWER', NULL, 'Regularization and cross-validation', 2, 3, NOW() - INTERVAL '30 days')
ON CONFLICT (id) DO NOTHING;



INSERT INTO quiz_attempts (id, quiz_id, student_id, score, total_points, earned_points, started_at, completed_at) VALUES
  -- John Doe attempts Quiz 1
  ('66666666-0000-0000-0000-000000000001', 'eeeeeeee-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004',
   80.00, 5, 4, NOW() - INTERVAL '43 days', NOW() - INTERVAL '43 days' + INTERVAL '20 minutes'),

  -- John Doe attempts Quiz 2
  ('66666666-0000-0000-0000-000000000002', 'eeeeeeee-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000004',
   100.00, 3, 3, NOW() - INTERVAL '38 days', NOW() - INTERVAL '38 days' + INTERVAL '15 minutes'),

  -- Alice Johnson attempts Quiz 1
  ('66666666-0000-0000-0000-000000000003', 'eeeeeeee-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000005',
   60.00, 5, 3, NOW() - INTERVAL '33 days', NOW() - INTERVAL '33 days' + INTERVAL '25 minutes'),

  -- Alice Johnson attempts Quiz 4
  ('66666666-0000-0000-0000-000000000004', 'eeeeeeee-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000005',
   75.00, 4, 3, NOW() - INTERVAL '28 days', NOW() - INTERVAL '28 days' + INTERVAL '18 minutes'),

  -- Sara Lee attempts Quiz 2
  ('66666666-0000-0000-0000-000000000005', 'eeeeeeee-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000007',
   66.67, 3, 2, NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days' + INTERVAL '12 minutes')
ON CONFLICT (id) DO NOTHING;


INSERT INTO quiz_attempt_answers (id, attempt_id, question_id, answer, is_correct, points_earned, answered_at) VALUES
  -- John Doe, Quiz 1 attempt (score 80% = 4/5)
  ('77777777-0000-0000-0000-000000000001', '66666666-0000-0000-0000-000000000001', '55555555-0000-0000-0000-000000000001', 'B', true,  1, NOW() - INTERVAL '43 days'),
  ('77777777-0000-0000-0000-000000000002', '66666666-0000-0000-0000-000000000001', '55555555-0000-0000-0000-000000000002', 'FALSE', true, 1, NOW() - INTERVAL '43 days'),
  ('77777777-0000-0000-0000-000000000003', '66666666-0000-0000-0000-000000000001', '55555555-0000-0000-0000-000000000003', 'B', true,  1, NOW() - INTERVAL '43 days'),
  ('77777777-0000-0000-0000-000000000004', '66666666-0000-0000-0000-000000000001', '55555555-0000-0000-0000-000000000004', 'A column that links two tables', false, 0, NOW() - INTERVAL '43 days'),

  -- John Doe, Quiz 2 attempt (score 100% = 3/3)
  ('77777777-0000-0000-0000-000000000005', '66666666-0000-0000-0000-000000000002', '55555555-0000-0000-0000-000000000005', 'C', true, 1, NOW() - INTERVAL '38 days'),
  ('77777777-0000-0000-0000-000000000006', '66666666-0000-0000-0000-000000000002', '55555555-0000-0000-0000-000000000006', 'FALSE', true, 1, NOW() - INTERVAL '38 days'),
  ('77777777-0000-0000-0000-000000000007', '66666666-0000-0000-0000-000000000002', '55555555-0000-0000-0000-000000000007', 'C', true, 1, NOW() - INTERVAL '38 days'),

  -- Alice Johnson, Quiz 1 attempt (score 60% = 3/5)
  ('77777777-0000-0000-0000-000000000008', '66666666-0000-0000-0000-000000000003', '55555555-0000-0000-0000-000000000001', 'A', false, 0, NOW() - INTERVAL '33 days'),
  ('77777777-0000-0000-0000-000000000009', '66666666-0000-0000-0000-000000000003', '55555555-0000-0000-0000-000000000002', 'FALSE', true, 1, NOW() - INTERVAL '33 days'),
  ('77777777-0000-0000-0000-000000000010', '66666666-0000-0000-0000-000000000003', '55555555-0000-0000-0000-000000000003', 'B', true, 1, NOW() - INTERVAL '33 days'),
  ('77777777-0000-0000-0000-000000000011', '66666666-0000-0000-0000-000000000003', '55555555-0000-0000-0000-000000000004', 'A column that references another table primary key', true, 1, NOW() - INTERVAL '33 days'),

  -- Alice Johnson, Quiz 4 attempt (score 75% = 3/4)
  ('77777777-0000-0000-0000-000000000012', '66666666-0000-0000-0000-000000000004', '55555555-0000-0000-0000-000000000010', 'C', true,  1, NOW() - INTERVAL '28 days'),
  ('77777777-0000-0000-0000-000000000013', '66666666-0000-0000-0000-000000000004', '55555555-0000-0000-0000-000000000011', 'TRUE', true, 1, NOW() - INTERVAL '28 days'),
  ('77777777-0000-0000-0000-000000000014', '66666666-0000-0000-0000-000000000004', '55555555-0000-0000-0000-000000000012', 'Regularization and more data', false, 0, NOW() - INTERVAL '28 days'),

  -- Sara Lee, Quiz 2 attempt (score 66.67% = 2/3)
  ('77777777-0000-0000-0000-000000000015', '66666666-0000-0000-0000-000000000005', '55555555-0000-0000-0000-000000000005', 'C', true,  1, NOW() - INTERVAL '20 days'),
  ('77777777-0000-0000-0000-000000000016', '66666666-0000-0000-0000-000000000005', '55555555-0000-0000-0000-000000000006', 'TRUE', false, 0, NOW() - INTERVAL '20 days'),
  ('77777777-0000-0000-0000-000000000017', '66666666-0000-0000-0000-000000000005', '55555555-0000-0000-0000-000000000007', 'C', true,  1, NOW() - INTERVAL '20 days')
ON CONFLICT (id) DO NOTHING;

