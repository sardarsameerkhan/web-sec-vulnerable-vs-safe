DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS comments;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student'
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    comment TEXT NOT NULL
);

-- Seed Team Members & Admin Users
INSERT INTO users (username, full_name, password, email, role) VALUES 
('sardar_sameer', 'Sardar Sameer', 'SameerPass2026!', 'sardar.sameer@flex.edu', 'administrator'),
('abdul_rehman', 'Abdul Rehman', 'AbdulPass2026!', 'abdul.rehman@flex.edu', 'student'),
('salman_shafique', 'Salman Shafique', 'SalmanPass2026!', 'salman.shafique@flex.edu', 'student');

-- Seed Initial Discussion Forum & Announcement Data
INSERT INTO comments (username, comment) VALUES 
('sardar_sameer', 'Welcome to FLEX Academic Portal. Course enrollment for Fall 2026 is now active.'),
('abdul_rehman', 'Has the course syllabus for Information Security been updated?'),
('salman_shafique', 'Yes, it is available under the course resources directory.');