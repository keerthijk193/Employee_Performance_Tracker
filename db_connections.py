"""All database connectivity lives here.

* SQLite  -> structured data (employees, projects, assignments)
* MongoDB -> flexible data (performance reviews)

Settings come from environment variables (or a .env file) so that no
passwords are ever hard-coded.
"""
import os
import sqlite3

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from exceptions import DatabaseConnectionError

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "company.db")

# --------------------------------------------------------------------------
# SQL (SQLite)
# --------------------------------------------------------------------------
# Rationale for the design is documented in docs/ARCHITECTURE.md
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS Employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    hire_date   TEXT NOT NULL,          -- ISO date: YYYY-MM-DD
    department  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Projects (
    project_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    start_date   TEXT NOT NULL,         -- ISO date
    end_date     TEXT,                  -- NULL = not decided yet
    status       TEXT NOT NULL DEFAULT 'Planning'
                 CHECK (status IN ('Planning','Active','On Hold','Completed','Cancelled')),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS EmployeeProjects (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id   INTEGER NOT NULL,
    project_id    INTEGER NOT NULL,
    role          TEXT NOT NULL,
    assigned_date TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id)  REFERENCES Projects(project_id)   ON DELETE CASCADE,
    UNIQUE (employee_id, project_id)    -- an employee can't be assigned twice
);
"""


def create_tables(conn):
    """Create the tables only if they do not already exist."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def get_sql_connection(db_path=None):
    """Open a SQLite connection (creating tables on first use).

    Rows come back as sqlite3.Row so columns can be read by name.
    Foreign-key checking is OFF by default in SQLite, so we turn it on.
    """
    path = db_path or os.environ.get("EPT_SQLITE_PATH") or DEFAULT_SQLITE_PATH
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        create_tables(conn)
        return conn
    except sqlite3.Error as exc:
        raise DatabaseConnectionError(f"Could not open SQLite database: {exc}") from exc


# --------------------------------------------------------------------------
# NoSQL (MongoDB)
# --------------------------------------------------------------------------
_mongo_client = None


def get_reviews_collection():
    """Return the MongoDB 'reviews' collection (client is created once)."""
    global _mongo_client
    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.environ.get("MONGO_DB_NAME", "performance_reviews_db")
    coll_name = os.environ.get("MONGO_COLLECTION", "reviews")
    try:
        if _mongo_client is None:
            _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            _mongo_client.admin.command("ping")  # fail fast if unreachable
        collection = _mongo_client[db_name][coll_name]
        collection.create_index([("employee_id", ASCENDING)])  # fast lookups
        return collection
    except PyMongoError as exc:
        _mongo_client = None
        raise DatabaseConnectionError(
            "Could not connect to MongoDB. Is it running / is MONGO_URI correct? "
            f"({exc.__class__.__name__})"
        ) from exc
