"""Project and assignment operations (SQL / SQLite)."""
import sqlite3

import db_connections as db
from employee_manager import get_employee_by_id
from exceptions import (
    DuplicateAssignmentError,
    ProjectNotFoundError,
    ValidationError,
)
from utils import require_text, today, validate_date

VALID_STATUSES = ("Planning", "Active", "On Hold", "Completed", "Cancelled")


def _normalise_status(status):
    """Accept any capitalisation, e.g. 'active' -> 'Active'."""
    status = require_text(status, "Status")
    for valid in VALID_STATUSES:
        if status.lower() == valid.lower():
            return valid
    raise ValidationError(f"Status must be one of: {', '.join(VALID_STATUSES)}.")


def add_project(project_name, start_date, end_date=None, status="Planning"):
    """Insert a project and return its project_id."""
    project_name = require_text(project_name, "Project name")
    start_date = validate_date(start_date, "Start date")
    if end_date:
        end_date = validate_date(end_date, "End date")
        if end_date < start_date:
            raise ValidationError("End date cannot be before the start date.")
    else:
        end_date = None
    status = _normalise_status(status)

    conn = db.get_sql_connection()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO Projects (project_name, start_date, end_date, status) "
                "VALUES (?, ?, ?, ?)",
                (project_name, start_date, end_date, status),
            )
            return cur.lastrowid
    finally:
        conn.close()


def get_project_by_id(project_id):
    """Return one project as a dict, or raise ProjectNotFoundError."""
    conn = db.get_sql_connection()
    try:
        row = conn.execute(
            "SELECT * FROM Projects WHERE project_id = ?", (project_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise ProjectNotFoundError(f"Project ID {project_id} not found.")
    return dict(row)


def list_all_projects():
    """Return all projects as a list of dicts."""
    conn = db.get_sql_connection()
    try:
        rows = conn.execute("SELECT * FROM Projects ORDER BY project_id").fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def assign_employee_to_project(employee_id, project_id, role, assigned_date=None):
    """Link an employee to a project via the EmployeeProjects junction table.

    Returns the new assignment_id.
    """
    role = require_text(role, "Role")
    assigned_date = validate_date(assigned_date, "Assigned date") if assigned_date else today()

    # Check both exist first so the user gets a clear message.
    get_employee_by_id(employee_id)   # raises EmployeeNotFoundError
    get_project_by_id(project_id)     # raises ProjectNotFoundError

    conn = db.get_sql_connection()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO EmployeeProjects (employee_id, project_id, role, assigned_date) "
                "VALUES (?, ?, ?, ?)",
                (employee_id, project_id, role, assigned_date),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise DuplicateAssignmentError(
            f"Employee {employee_id} is already assigned to project {project_id}."
        ) from exc
    finally:
        conn.close()


def get_projects_for_employee(employee_id):
    """Return all projects (with role + assigned date) for one employee.

    Uses a JOIN across EmployeeProjects and Projects.
    """
    get_employee_by_id(employee_id)  # raises EmployeeNotFoundError if missing
    conn = db.get_sql_connection()
    try:
        rows = conn.execute(
            """
            SELECT p.project_id, p.project_name, p.start_date, p.end_date,
                   p.status, ep.role, ep.assigned_date
            FROM EmployeeProjects ep
            JOIN Projects p ON p.project_id = ep.project_id
            WHERE ep.employee_id = ?
            ORDER BY ep.assigned_date, p.project_id
            """,
            (employee_id,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
