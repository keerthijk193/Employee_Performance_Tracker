import pytest

import employee_manager as em
from exceptions import DuplicateEmailError, EmployeeNotFoundError, ValidationError


def test_add_and_get_employee(employee):
    emp = em.get_employee_by_id(employee)
    assert emp["first_name"] == "Asha"
    assert emp["email"] == "asha@example.com"


def test_duplicate_email_raises(employee):
    with pytest.raises(DuplicateEmailError):
        em.add_employee("X", "Y", "ASHA@example.com", "2023-02-02", "HR")  # case-insensitive


def test_get_missing_employee():
    with pytest.raises(EmployeeNotFoundError):
        em.get_employee_by_id(999)


def test_list_all_employees(employee):
    em.add_employee("Ravi", "Kumar", "ravi@example.com", "2022-06-01", "QA")
    assert len(em.list_all_employees()) == 2


def test_list_empty():
    assert em.list_all_employees() == []


@pytest.mark.parametrize(
    "args",
    [
        ("", "Rao", "a@b.com", "2023-01-01", "IT"),
        ("A", "Rao", "not-an-email", "2023-01-01", "IT"),
        ("A", "Rao", "a@b.com", "01-01-2023", "IT"),
        ("A", "Rao", "a@b.com", "2023-13-45", "IT"),
        ("A", "Rao", "a@b.com", "2023-01-01", "  "),
    ],
)
def test_invalid_input(args):
    with pytest.raises(ValidationError):
        em.add_employee(*args)
