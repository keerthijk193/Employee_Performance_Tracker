import pytest

import project_manager as pm
from exceptions import (
    DuplicateAssignmentError,
    EmployeeNotFoundError,
    ProjectNotFoundError,
    ValidationError,
)


def test_add_project_defaults(project):
    p = pm.get_project_by_id(project)
    assert p["status"] == "Planning"
    assert p["end_date"] is None


def test_status_case_insensitive():
    pid = pm.add_project("P", "2024-01-01", "2024-06-01", "active")
    assert pm.get_project_by_id(pid)["status"] == "Active"


def test_invalid_status_and_dates():
    with pytest.raises(ValidationError):
        pm.add_project("P", "2024-01-01", status="Weird")
    with pytest.raises(ValidationError):
        pm.add_project("P", "2024-05-01", "2024-01-01")
    with pytest.raises(ValidationError):
        pm.add_project("", "2024-01-01")


def test_get_missing_project():
    with pytest.raises(ProjectNotFoundError):
        pm.get_project_by_id(42)


def test_list_projects(project):
    assert len(pm.list_all_projects()) == 1


def test_assign_and_get_projects(employee, project):
    pm.assign_employee_to_project(employee, project, "Developer", "2024-02-01")
    result = pm.get_projects_for_employee(employee)
    assert len(result) == 1
    assert result[0]["role"] == "Developer"
    assert result[0]["assigned_date"] == "2024-02-01"


def test_assign_default_date(employee, project):
    pm.assign_employee_to_project(employee, project, "Dev")
    assert pm.get_projects_for_employee(employee)[0]["assigned_date"]


def test_duplicate_assignment(employee, project):
    pm.assign_employee_to_project(employee, project, "Dev")
    with pytest.raises(DuplicateAssignmentError):
        pm.assign_employee_to_project(employee, project, "Tester")


def test_assign_missing_entities(employee, project):
    with pytest.raises(EmployeeNotFoundError):
        pm.assign_employee_to_project(99, project, "Dev")
    with pytest.raises(ProjectNotFoundError):
        pm.assign_employee_to_project(employee, 99, "Dev")
    with pytest.raises(ValidationError):
        pm.assign_employee_to_project(employee, project, " ")


def test_projects_for_missing_employee():
    with pytest.raises(EmployeeNotFoundError):
        pm.get_projects_for_employee(5)


def test_employee_with_no_projects(employee):
    assert pm.get_projects_for_employee(employee) == []
