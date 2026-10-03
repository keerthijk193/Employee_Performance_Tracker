"""Employee operations (SQL / SQLite)."""
import sqlite3

import db_connections as db
from exceptions import DuplicateEmailError, EmployeeNotFoundError
from utils import require_text, validate_date, validate_email


def add_employee(first_name, last_name, email, hire_date, department):
    """Insert a new employee and return the new employee_id.

    Raises DuplicateEmailError if the email is already used. The UNIQUE
    constraint in the database is the real guard (safe even if two people
    insert at the same time); we just translate the error to a friendly one.
    """
    first_name = require_text(first_name, "First name")
    last_name = require_text(last_name, "Last name")
    email = validate_email(email)
    hire_date = validate_date(hire_date, "Hire date")
    department = require_text(department, "Department")

    conn = db.get_sql_connection()
    try:
        with conn:  # commits on success, rolls back on error
            cur = conn.execute(
                "INSERT INTO Employees (first_name, last_name, email, hire_date, department) "
                "VALUES (?, ?, ?, ?, ?)",
                (first_name, last_name, email, hire_date, department),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmailError(f"An employee with email '{email}' already exists.") from exc
    finally:
        conn.close()


def get_employee_by_id(employee_id):
    """Return one employee as a dict, or raise EmployeeNotFoundError."""
    conn = db.get_sql_connection()
    try:
        row = conn.execute(
            "SELECT * FROM Employees WHERE employee_id = ?", (employee_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise EmployeeNotFoundError(f"Employee ID {employee_id} not found.")
    return dict(row)


def list_all_employees():
    """Return every employee as a list of dicts (empty list if none)."""
    conn = db.get_sql_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM Employees ORDER BY employee_id"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
