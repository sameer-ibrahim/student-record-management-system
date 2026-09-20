# Student Record Management System

A menu-driven console application to manage student records, course enrollments, and scores — built with **Python** and **MySQL**.

## Features
- Add, view, update, and delete student records
- Enroll students into courses and record their scores
- Input validation (roll number format, email format, score range, duplicate checks)
- Analytical queries:
  - Average score per student
  - Top scorers across all courses
  - Number of students enrolled per course

## Database Design
The system uses **three related tables** instead of a single flat table:

- `students` — student personal details
- `courses` — course catalog
- `enrollments` — a many-to-many link between students and courses, storing each student's score per course

This relational structure (with foreign keys and a unique constraint preventing duplicate enrollment) reflects how real student information systems are modeled.

## Tech Stack
- Python 3
- MySQL
- `mysql-connector-python` library

## Setup
1. Install dependencies:
   ```
   pip install mysql-connector-python
   ```
2. Run the schema file in MySQL to create the database and tables:
   ```
   mysql -u root -p < schema.sql
   ```
3. Update the `DB_CONFIG` dictionary in `main.py` with your MySQL username/password.
4. Run the application:
   ```
   python main.py
   ```

## Example Usage
```
========== Student Record Management System ==========
1. Add Student
2. View All Students
3. Update Student Email
4. Delete Student
5. Enroll Student in a Course
6. View Average Score per Student
7. View Top Scorers
8. View Number of Students per Course
9. Exit
=========================================================
Enter your choice (1-9): 1

--- Add New Student ---
Roll Number (e.g. CS101): CS201
Full Name: Aditi Rao
Email: aditi.rao@example.com
Date of Birth (YYYY-MM-DD): 2004-05-12
Student 'Aditi Rao' added successfully.
```
