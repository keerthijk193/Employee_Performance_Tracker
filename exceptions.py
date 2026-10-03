"""Custom exceptions so every module reports problems in a consistent way.

The CLI (main.py) catches TrackerError and prints a friendly message
instead of crashing with a long traceback.
"""


class TrackerError(Exception):
    """Base class for all application-specific errors."""


class ValidationError(TrackerError):
    """User supplied invalid input (bad date, empty name, bad rating...)."""


class DuplicateEmailError(TrackerError):
    """An employee with this email already exists."""


class DuplicateAssignmentError(TrackerError):
    """The employee is already assigned to this project."""


class EmployeeNotFoundError(TrackerError):
    """No employee exists with the given ID."""


class ProjectNotFoundError(TrackerError):
    """No project exists with the given ID."""


class DatabaseConnectionError(TrackerError):
    """Could not talk to MongoDB (or SQLite)."""
