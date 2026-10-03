"""Performance reviews (NoSQL / MongoDB).

Each review is one document. Only employee_id, review_date, reviewer_name
and overall_rating are required - everything else is optional and you can
add brand-new fields (see **extra_fields) without changing any schema.
"""
from pymongo.errors import PyMongoError

import db_connections as db
from employee_manager import get_employee_by_id
from exceptions import DatabaseConnectionError, ValidationError
from utils import require_text, today, validate_date


def _as_list(value):
    """Allow 'a, b' strings or lists; always store a clean list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    return [str(v).strip() for v in value if str(v).strip()]


def submit_performance_review(
    employee_id,
    reviewer_name,
    overall_rating,
    review_date=None,
    strengths=None,
    areas_for_improvement=None,
    comments="",
    goals_for_next_period=None,
    **extra_fields,
):
    """Insert one review document and return its id (as a string)."""
    get_employee_by_id(employee_id)  # make sure the employee exists in SQL
    reviewer_name = require_text(reviewer_name, "Reviewer name")
    try:
        rating = float(overall_rating)
    except (TypeError, ValueError):
        raise ValidationError("Overall rating must be a number between 1 and 5.") from None
    if not 1 <= rating <= 5:
        raise ValidationError("Overall rating must be between 1 and 5.")
    review_date = validate_date(review_date, "Review date") if review_date else today()

    document = {
        "employee_id": employee_id,
        "review_date": review_date,
        "reviewer_name": reviewer_name,
        "overall_rating": rating,
        "strengths": _as_list(strengths),
        "areas_for_improvement": _as_list(areas_for_improvement),
        "comments": (comments or "").strip(),
        "goals_for_next_period": _as_list(goals_for_next_period),
    }
    # Flexible part: any additional fields are stored as-is.
    for key, value in extra_fields.items():
        document.setdefault(key, value)

    try:
        result = db.get_reviews_collection().insert_one(document)
    except PyMongoError as exc:
        raise DatabaseConnectionError(f"Could not save review: {exc}") from exc
    return str(result.inserted_id)


def get_performance_reviews_for_employee(employee_id):
    """Return all reviews for an employee, oldest first (list of dicts)."""
    try:
        cursor = db.get_reviews_collection().find({"employee_id": employee_id}).sort(
            "review_date", 1
        )
        reviews = list(cursor)
    except PyMongoError as exc:
        raise DatabaseConnectionError(f"Could not read reviews: {exc}") from exc
    for review in reviews:
        review["_id"] = str(review["_id"])  # make it printable / JSON friendly
    return reviews
