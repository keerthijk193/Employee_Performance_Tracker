"""Optional: fill the databases with demo data (needs MongoDB running).

Run:  python seed_data.py
"""
import employee_manager as em
import performance_reviewer as pr
import project_manager as pm
from exceptions import DuplicateEmailError, TrackerError


def main():
    try:
        a = em.add_employee("Asha", "Rao", "asha@example.com", "2023-01-10", "Engineering")
        b = em.add_employee("Ravi", "Kumar", "ravi@example.com", "2022-06-01", "QA")
        p = pm.add_project("Website Revamp", "2024-01-01", None, "Active")
        pm.assign_employee_to_project(a, p, "Developer")
        pm.assign_employee_to_project(b, p, "Tester")
        pr.submit_performance_review(
            a, "Meena S", 4.5, strengths="Teamwork, Coding",
            areas_for_improvement="Documentation", comments="Great year.",
            goals_for_next_period="Lead a module", leadership_score=8,
        )
        print("Demo data added.")
    except DuplicateEmailError:
        print("Demo data already exists.")
    except TrackerError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
