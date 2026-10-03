"""Command-line entry point for the Employee Performance Tracking System.

Run with:  python main.py
"""
import employee_manager as em
import performance_reviewer as pr
import project_manager as pm
import reports
from exceptions import TrackerError

MENU = """
==============================================
  Employee Performance Tracking System
==============================================
 1. Add Employee
 2. Add Project
 3. Assign Employee to Project
 4. Submit Performance Review
 5. View Employee Projects
 6. View Employee Performance
 7. Generate Reports
 8. Exit
"""


def ask(prompt, default=None):
    """Read a line of text; return default when the user just presses Enter."""
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_int(prompt):
    """Read an integer ID; raises ValueError-style TrackerError on bad input."""
    from exceptions import ValidationError

    raw = ask(prompt)
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"'{raw}' is not a valid number.") from None


def add_employee_ui():
    print("\n-- Add Employee --")
    emp_id = em.add_employee(
        ask("First name"),
        ask("Last name"),
        ask("Email"),
        ask("Hire date (YYYY-MM-DD)"),
        ask("Department"),
    )
    print(f"✅ Employee added with ID {emp_id}.")


def add_project_ui():
    print("\n-- Add Project --")
    proj_id = pm.add_project(
        ask("Project name"),
        ask("Start date (YYYY-MM-DD)"),
        ask("End date (YYYY-MM-DD, optional)"),
        ask(f"Status ({'/'.join(pm.VALID_STATUSES)})", "Planning"),
    )
    print(f"✅ Project added with ID {proj_id}.")


def assign_ui():
    print("\n-- Assign Employee to Project --")
    emp_id = ask_int("Employee ID")
    proj_id = ask_int("Project ID")
    role = ask("Role (e.g. Developer, Tester)")
    pm.assign_employee_to_project(emp_id, proj_id, role)
    print("✅ Employee assigned to project.")


def submit_review_ui():
    print("\n-- Submit Performance Review --")
    emp_id = ask_int("Employee ID")
    em.get_employee_by_id(emp_id)  # fail early if the employee doesn't exist
    reviewer = ask("Reviewer name")
    rating = ask("Overall rating (1-5)")
    strengths = ask("Strengths (comma separated)")
    improve = ask("Areas for improvement (comma separated)")
    comments = ask("Comments")
    goals = ask("Goals for next period (comma separated)")
    raw_extra = ask("Extra custom fields? key=value, comma separated (Enter to skip)")
    extras = {}
    if raw_extra:
        for pair in raw_extra.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                if key.strip():
                    extras[key.strip()] = value.strip()
    review_id = pr.submit_performance_review(
        emp_id, reviewer, rating,
        strengths=strengths, areas_for_improvement=improve,
        comments=comments, goals_for_next_period=goals, **extras,
    )
    print(f"✅ Review saved (id: {review_id}).")


def view_projects_ui():
    print("\n-- Employee Projects --")
    emp_id = ask_int("Employee ID")
    employee = em.get_employee_by_id(emp_id)
    projects = pm.get_projects_for_employee(emp_id)
    print(f"\nProjects for {employee['first_name']} {employee['last_name']}:")
    if not projects:
        print("  (none)")
    for p in projects:
        print(f"  [{p['project_id']}] {p['project_name']} | {p['role']} | "
              f"{p['status']} | assigned {p['assigned_date']}")


def view_performance_ui():
    print("\n-- Employee Performance --")
    reports.generate_employee_performance_summary(ask_int("Employee ID"))


def reports_ui():
    print("\n 1. Employee-Project report\n 2. List all employees\n 3. List all projects")
    choice = ask("Choose report")
    if choice == "1":
        reports.generate_employee_project_report()
    elif choice == "2":
        employees = em.list_all_employees()
        print("\n=== Employees ===")
        if not employees:
            print("(none)")
        for e in employees:
            print(f"  [{e['employee_id']}] {e['first_name']} {e['last_name']} | "
                  f"{e['email']} | {e['department']} | hired {e['hire_date']}")
    elif choice == "3":
        projects = pm.list_all_projects()
        print("\n=== Projects ===")
        if not projects:
            print("(none)")
        for p in projects:
            print(f"  [{p['project_id']}] {p['project_name']} | {p['status']} | "
                  f"{p['start_date']} -> {p['end_date'] or 'TBD'}")
    else:
        print("❌ Invalid report choice.")


ACTIONS = {
    "1": add_employee_ui,
    "2": add_project_ui,
    "3": assign_ui,
    "4": submit_review_ui,
    "5": view_projects_ui,
    "6": view_performance_ui,
    "7": reports_ui,
}


def main():
    """Show the menu until the user chooses Exit."""
    while True:
        print(MENU)
        choice = input("Enter your choice (1-8): ").strip()
        if choice == "8":
            print("Goodbye! 👋")
            return
        action = ACTIONS.get(choice)
        if action is None:
            print("❌ Please enter a number from 1 to 8.")
            continue
        try:
            action()
        except TrackerError as exc:       # expected problems -> friendly message
            print(f"❌ {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
        except Exception as exc:          # anything unexpected - don't crash the menu
            print(f"❌ Unexpected error: {exc}")


if __name__ == "__main__":
    main()
