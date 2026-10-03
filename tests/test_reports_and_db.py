import sqlite3

import pytest

import db_connections
import performance_reviewer as pr
import project_manager as pm
import reports
from exceptions import DatabaseConnectionError, EmployeeNotFoundError


def test_tables_created_and_idempotent():
    conn = db_connections.get_sql_connection()
    db_connections.create_tables(conn)  # second call must not fail
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"Employees", "Projects", "EmployeeProjects"} <= names
    conn.close()


def test_foreign_keys_enforced():
    conn = db_connections.get_sql_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO EmployeeProjects (employee_id, project_id, role) VALUES (1,1,'x')")
    conn.close()


def test_bad_sqlite_path():
    with pytest.raises(DatabaseConnectionError):
        db_connections.get_sql_connection("/nonexistent_dir/x/y.db")


def test_project_report_empty():
    assert "No employee-project" in reports.generate_employee_project_report()


def test_project_report(employee, project, capsys):
    pm.assign_employee_to_project(employee, project, "Developer")
    text = reports.generate_employee_project_report()
    assert "Asha Rao" in text and "Website" in text and "Developer" in text
    assert "Employee Name" in capsys.readouterr().out


def test_performance_summary(employee):
    pr.submit_performance_review(employee, "M", 4, strengths="A", areas_for_improvement="B")
    pr.submit_performance_review(employee, "M", 5, strengths="C")
    text = reports.generate_employee_performance_summary(employee)
    assert "4.50" in text and "A, C" in text and "B" in text


def test_performance_summary_no_reviews(employee):
    assert "N/A" in reports.generate_employee_performance_summary(employee)


def test_performance_summary_missing_employee():
    with pytest.raises(EmployeeNotFoundError):
        reports.generate_employee_performance_summary(404)
