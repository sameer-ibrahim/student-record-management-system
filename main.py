"""
Student Record Management System
---------------------------------
A menu-driven console application built with Python and MySQL.

Features:
- Add / view / update / delete student records
- Enroll students into courses and record scores
- Input validation (roll number format, duplicate checks, score range)
- Analytical queries: average score per student, top scorers, students per course

Tech: Python, MySQL (via mysql-connector-python)
"""

import re
from datetime import datetime

import mysql.connector
from mysql.connector import Error


# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",   # change this before running
    "database": "student_management",
}


def get_connection():
    """Create and return a new database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Database connection failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_roll_number(roll_number):
    """Roll number must look like ABC123 style: 2-5 letters followed by digits."""
    return bool(re.match(r"^[A-Za-z]{2,5}\d{2,6}$", roll_number))


def is_valid_email(email):
    return bool(re.match(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$", email))


def is_valid_score(score):
    try:
        score = float(score)
        return 0 <= score <= 100
    except ValueError:
        return False


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Student CRUD operations
# ---------------------------------------------------------------------------

def add_student(conn):
    print("\n--- Add New Student ---")
    roll_number = input("Roll Number (e.g. CS101): ").strip()
    if not is_valid_roll_number(roll_number):
        print("Invalid roll number format. Use letters followed by digits, e.g. CS101.")
        return

    name = input("Full Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    email = input("Email: ").strip()
    if not is_valid_email(email):
        print("Invalid email format.")
        return

    dob = input("Date of Birth (YYYY-MM-DD): ").strip()
    if not is_valid_date(dob):
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (roll_number, name, email, date_of_birth) "
            "VALUES (%s, %s, %s, %s)",
            (roll_number, name, email, dob),
        )
        conn.commit()
        print(f"Student '{name}' added successfully.")
    except mysql.connector.IntegrityError:
        print("A student with this roll number or email already exists.")
    finally:
        cursor.close()


def view_students(conn):
    print("\n--- All Students ---")
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, roll_number, name, email, date_of_birth FROM students")
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print("No students found.")
        return

    print(f"{'ID':<5}{'Roll No':<12}{'Name':<20}{'Email':<25}{'DOB'}")
    print("-" * 75)
    for row in rows:
        print(f"{row[0]:<5}{row[1]:<12}{row[2]:<20}{row[3]:<25}{row[4]}")


def update_student(conn):
    print("\n--- Update Student ---")
    roll_number = input("Enter Roll Number of student to update: ").strip()

    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE roll_number = %s", (roll_number,))
    result = cursor.fetchone()
    if not result:
        print("No student found with that roll number.")
        cursor.close()
        return

    new_email = input("New Email (leave blank to skip): ").strip()
    if new_email and not is_valid_email(new_email):
        print("Invalid email format. Update cancelled.")
        cursor.close()
        return

    if new_email:
        cursor.execute(
            "UPDATE students SET email = %s WHERE roll_number = %s",
            (new_email, roll_number),
        )
        conn.commit()
        print("Student record updated.")
    else:
        print("No changes made.")
    cursor.close()


def delete_student(conn):
    print("\n--- Delete Student ---")
    roll_number = input("Enter Roll Number of student to delete: ").strip()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE roll_number = %s", (roll_number,))
    result = cursor.fetchone()
    if not result:
        print("No student found with that roll number.")
        cursor.close()
        return

    confirm = input(f"Delete '{result[0]}'? This also removes their enrollments. (y/n): ")
    if confirm.lower() == "y":
        cursor.execute("DELETE FROM students WHERE roll_number = %s", (roll_number,))
        conn.commit()
        print("Student deleted.")
    else:
        print("Deletion cancelled.")
    cursor.close()


# ---------------------------------------------------------------------------
# Enrollment operations
# ---------------------------------------------------------------------------

def enroll_student(conn):
    print("\n--- Enroll Student in Course ---")
    roll_number = input("Student Roll Number: ").strip()
    course_code = input("Course Code (e.g. CS101): ").strip()

    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE roll_number = %s", (roll_number,))
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        cursor.close()
        return

    cursor.execute("SELECT course_id FROM courses WHERE course_code = %s", (course_code,))
    course = cursor.fetchone()
    if not course:
        print("Course not found.")
        cursor.close()
        return

    score_input = input("Score (0-100, leave blank if not graded yet): ").strip()
    score = None
    if score_input:
        if not is_valid_score(score_input):
            print("Invalid score. Must be between 0 and 100.")
            cursor.close()
            return
        score = float(score_input)

    try:
        cursor.execute(
            "INSERT INTO enrollments (student_id, course_id, score) VALUES (%s, %s, %s)",
            (student[0], course[0], score),
        )
        conn.commit()
        print("Enrollment recorded.")
    except mysql.connector.IntegrityError:
        print("This student is already enrolled in this course.")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Analytical queries
# ---------------------------------------------------------------------------

def average_score_per_student(conn):
    print("\n--- Average Score per Student ---")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.name, ROUND(AVG(e.score), 2) AS avg_score
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        WHERE e.score IS NOT NULL
        GROUP BY s.student_id
        ORDER BY avg_score DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print("No graded enrollments yet.")
        return
    for name, avg_score in rows:
        print(f"{name:<20}{avg_score}")


def top_scorers(conn, limit=3):
    print(f"\n--- Top {limit} Scorers (single best course score) ---")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.name, c.course_name, e.score
        FROM enrollments e
        JOIN students s ON s.student_id = e.student_id
        JOIN courses c ON c.course_id = e.course_id
        WHERE e.score IS NOT NULL
        ORDER BY e.score DESC
        LIMIT %s
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        print("No graded enrollments yet.")
        return
    for name, course_name, score in rows:
        print(f"{name:<20}{course_name:<30}{score}")


def students_per_course(conn):
    print("\n--- Number of Students per Course ---")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.course_name, COUNT(e.student_id) AS total_students
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id = e.course_id
        GROUP BY c.course_id
        ORDER BY total_students DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()

    for course_name, total in rows:
        print(f"{course_name:<35}{total}")


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def main_menu():
    conn = get_connection()
    if conn is None:
        print("Could not connect to the database. Check DB_CONFIG and try again.")
        return

    menu = """
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
"""

    while True:
        print(menu)
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_student(conn)
        elif choice == "2":
            view_students(conn)
        elif choice == "3":
            update_student(conn)
        elif choice == "4":
            delete_student(conn)
        elif choice == "5":
            enroll_student(conn)
        elif choice == "6":
            average_score_per_student(conn)
        elif choice == "7":
            top_scorers(conn)
        elif choice == "8":
            students_per_course(conn)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

    conn.close()


if __name__ == "__main__":
    main_menu()
