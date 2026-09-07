import json
from pathlib import Path

DATA_PATH = "/home/nineleaps/Downloads/Office_Assistant/src/agents/data/employees.json"


def load_employees():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def answer_employee_query(query, employee_id):
    employees = load_employees()

    employee = next(
        (
            emp
            for emp in employees
            if emp["employee_id"].lower() == employee_id.lower()
        ),
        None,
    )

    if employee is None:
        return f"No employee found with ID {employee_id}."

    query_lower = query.lower()

    if "leave" in query_lower:
        return (
            f"{employee['name']} ({employee['employee_id']}) "
            f"has {employee['leave_balance']} leave days remaining."
        )

    if "department" in query_lower:
        return f"Your department is {employee['department']}."

    if "manager" in query_lower:
        return f"Your manager is {employee['manager']}."

    if "designation" in query_lower or "role" in query_lower:
        return f"Your designation is {employee['designation']}."

    if "name" in query_lower or "who am i" in query_lower:
        return f"Your name is {employee['name']}."

    return (
        "I can currently answer questions about your leave balance, "
        "department, manager, designation, and name."
    )