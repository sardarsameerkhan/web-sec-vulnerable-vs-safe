DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS comments;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    comment TEXT NOT NULL
);

-- Seed users
INSERT INTO users (username, password, email, role) VALUES 
('admin', 'AdminPass2026!', 'admin@security.lab', 'administrator'),
('john_doe', 'UserPass123!', 'john@security.lab', 'user'),
('jane_smith', 'SecurePass456!', 'jane@security.lab', 'user');

-- Seed comments
INSERT INTO comments (username, comment) VALUES 
('john_doe', 'Welcome to the web security demonstration lab!');