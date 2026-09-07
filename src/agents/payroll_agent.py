import json
from pathlib import Path


DATA_PATH = "/home/nineleaps/Downloads/Office_Assistant/src/agents/data/payroll.json"


def load_payroll():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def answer_payroll_query(query, employee_id):
    payroll_records = load_payroll()

    employee = next(
        (
            record
            for record in payroll_records
            if record["employee_id"].lower() == employee_id.lower()
        ),
        None,
    )

    if employee is None:
        return f"No payroll record found for {employee_id}."

    query_lower = query.lower()

    if "annual" in query_lower or "yearly" in query_lower:
        return (
            f"Your annual salary is "
            f"{employee['currency']} {employee['annual_salary']:,}."
        )

    if "basic" in query_lower:
        return (
            f"Your basic salary is "
            f"{employee['currency']} {employee['basic_salary']:,}."
        )

    if "salary" in query_lower or "monthly" in query_lower:
        return (
            f"Your monthly salary is "
            f"{employee['currency']} {employee['monthly_salary']:,}."
        )

    return (
        "I can currently answer questions about your monthly, "
        "basic, and annual salary."
    )