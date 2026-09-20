-- Student Record Management System
-- Database schema: Students, Courses, and Enrollments (many-to-many)

CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    roll_number     VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    date_of_birth   DATE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    course_id       INT AUTO_INCREMENT PRIMARY KEY,
    course_code     VARCHAR(20) NOT NULL UNIQUE,
    course_name     VARCHAR(100) NOT NULL,
    credits         INT NOT NULL DEFAULT 3
);

-- Enrollments table (many-to-many between students and courses)
-- Also stores the grade/score for that student in that course
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    course_id       INT NOT NULL,
    score           DECIMAL(5,2),         -- score out of 100
    enrolled_on     DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id)  -- prevents duplicate enrollment
);

-- Sample seed data (optional, useful for demo/testing)
INSERT INTO courses (course_code, course_name, credits) VALUES
    ('CS101', 'Introduction to Programming', 4),
    ('CS102', 'Database Management Systems', 4),
    ('AI101', 'Artificial Intelligence Fundamentals', 3)
ON DUPLICATE KEY UPDATE course_name = VALUES(course_name);
