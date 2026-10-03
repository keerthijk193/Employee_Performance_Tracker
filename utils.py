"""Small input-validation helpers shared by all modules."""
import re
from datetime import datetime

from exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_FORMAT = "%Y-%m-%d"


def require_text(value, field_name):
    """Return the stripped string, or raise if it is empty / not text."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty.")
    return value.strip()


def validate_email(email):
    """Basic email format check. Stored in lower case."""
    email = require_text(email, "Email")
    if not _EMAIL_RE.match(email):
        raise ValidationError(f"'{email}' is not a valid email address.")
    return email.lower()


def validate_date(value, field_name="Date"):
    """Ensure the date is a real calendar date in YYYY-MM-DD format."""
    value = require_text(value, field_name)
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValidationError(
            f"{field_name} must be a valid date in YYYY-MM-DD format (got '{value}')."
        ) from None
    return value


def today():
    """Today's date as YYYY-MM-DD."""
    return datetime.now().strftime(DATE_FORMAT)
