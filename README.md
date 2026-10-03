# Employee Performance Tracking System

A command-line app (Python 3) that tracks employees, projects, assignments and
performance reviews. **SQLite** stores structured data, **MongoDB** stores flexible review documents.

## Features
- Onboard employees (duplicate email protection)
- Create projects, assign employees with roles
- Submit performance reviews (flexible fields) to MongoDB
- Reports: employee-project table, employee performance summary

## Project structure
| File | Purpose |
|------|---------|
| `main.py` | CLI menu (entry point) |
| `db_connections.py` | SQLite + MongoDB connections, creates tables |
| `employee_manager.py` | Add / get / list employees (SQL) |
| `project_manager.py` | Add projects, assign employees, list projects of employee (SQL) |
| `performance_reviewer.py` | Submit / fetch reviews (MongoDB) |
| `reports.py` | Combined reports (SQL JOIN + MongoDB) |
| `exceptions.py`, `utils.py` | Custom errors, input validation |
| `seed_data.py` | Optional demo data |
| `company.db` | SQLite database (auto-created) |
| `tests/` | Pytest suite (uses temp SQLite + mongomock) |
| `docs/ARCHITECTURE.md` | Architecture diagram and design rationale |

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
```

### MongoDB option A - Atlas (free cloud, easiest)
1. Sign up at https://www.mongodb.com/atlas -> create a free **M0** cluster.
2. *Database Access* -> add a user + password.
3. *Network Access* -> add your IP (or `0.0.0.0/0` for learning only).
4. *Connect -> Drivers* -> copy the connection string.
5. Put it in `.env` as `MONGO_URI=mongodb+srv://USER:PASSWORD@cluster.mongodb.net/`.

### MongoDB option B - Local
Install MongoDB Community Server and start it; the default
`MONGO_URI=mongodb://localhost:27017` works.

The database `reviews_db` and collection `reviews` are created automatically on the first review.

## Run
```bash
python main.py
python seed_data.py     # optional demo data
```

## Test
```bash
pytest --cov=. --cov-report term-missing
```
Tests need **no** real MongoDB (they use `mongomock`) and use a temporary SQLite file.
