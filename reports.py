"""Reports that combine SQL data and MongoDB data."""
import pandas as pd

import db_connections as db
from employee_manager import get_employee_by_id
from performance_reviewer import get_performance_reviews_for_employee


def _table(headers, rows):
    """Format rows into an aligned text table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    sep = "-+-".join("-" * w for w in widths)
    body = [" | ".join(str(c).ljust(w) for c, w in zip(row, widths)) for row in rows]
    return "\n".join([line, sep, *body])


def generate_employee_project_report():
    """Print (and return) 'Employee | Project | Role | Assigned Date' using a JOIN."""
    conn = db.get_sql_connection()
    try:
        rows = conn.execute(
            """
            SELECT e.first_name || ' ' || e.last_name AS employee_name,
                   p.project_name, ep.role, ep.assigned_date
            FROM EmployeeProjects ep
            JOIN Employees e ON e.employee_id = ep.employee_id
            JOIN Projects  p ON p.project_id  = ep.project_id
            ORDER BY employee_name, ep.assigned_date
            """
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        text = "No employee-project assignments found."
    else:
        text = _table(
            ["Employee Name", "Project Name", "Role", "Assigned Date"],
            [tuple(r) for r in rows],
        )
    print("\n=== Employee - Project Report ===")
    print(text)
    return text


def generate_employee_performance_summary(employee_id):
    """Print (and return) a summary: SQL employee info + MongoDB review stats."""
    employee = get_employee_by_id(employee_id)           # 1 SQL query
    reviews = get_performance_reviews_for_employee(employee_id)  # 1 NoSQL query

    lines = [
        f"Employee   : {employee['first_name']} {employee['last_name']} "
        f"(ID {employee['employee_id']})",
        f"Department : {employee['department']}",
        f"Reviews    : {len(reviews)}",
    ]
    if reviews:
        ratings = pd.Series([r["overall_rating"] for r in reviews], dtype=float)
        lines.append(
            f"Avg Rating : {ratings.mean():.2f} / 5  "
            f"(min {ratings.min():.1f}, max {ratings.max():.1f})"
        )
        strengths = sorted({s for r in reviews for s in r.get("strengths", [])})
        areas = sorted({a for r in reviews for a in r.get("areas_for_improvement", [])})
        lines.append("Strengths  : " + (", ".join(strengths) or "-"))
        lines.append("Improve    : " + (", ".join(areas) or "-"))
    else:
        lines.append("Avg Rating : N/A (no reviews yet)")

    text = "\n".join(lines)
    print("\n=== Performance Summary ===")
    print(text)
    return text
