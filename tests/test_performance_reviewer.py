import pytest

import performance_reviewer as pr
from exceptions import EmployeeNotFoundError, ValidationError


def test_submit_and_get_review(employee):
    rid = pr.submit_performance_review(
        employee, "Meena", 4, strengths="Teamwork, Coding", comments="Good"
    )
    assert rid
    reviews = pr.get_performance_reviews_for_employee(employee)
    assert len(reviews) == 1
    assert reviews[0]["strengths"] == ["Teamwork", "Coding"]
    assert reviews[0]["overall_rating"] == 4.0


def test_extra_fields_are_stored(employee):
    pr.submit_performance_review(employee, "Meena", 5, leadership_score=9)
    assert pr.get_performance_reviews_for_employee(employee)[0]["leadership_score"] == 9


def test_reviews_only_for_that_employee(employee):
    pr.submit_performance_review(employee, "Meena", 3)
    assert pr.get_performance_reviews_for_employee(employee + 1) == []


def test_invalid_reviews(employee):
    with pytest.raises(EmployeeNotFoundError):
        pr.submit_performance_review(999, "Meena", 3)
    with pytest.raises(ValidationError):
        pr.submit_performance_review(employee, "Meena", 9)
    with pytest.raises(ValidationError):
        pr.submit_performance_review(employee, "Meena", "abc")
    with pytest.raises(ValidationError):
        pr.submit_performance_review(employee, "", 3)


def test_list_inputs_and_dates(employee):
    pr.submit_performance_review(
        employee, "M", 3, review_date="2024-05-01", strengths=["A", " "], areas_for_improvement=None
    )
    r = pr.get_performance_reviews_for_employee(employee)[0]
    assert r["strengths"] == ["A"] and r["review_date"] == "2024-05-01"
