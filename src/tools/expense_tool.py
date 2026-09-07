import pandas as pd

from src.paths import EXPENSE_FILE


def get_expenses(employee_id):
    """Return all expenses for an employee."""

    df = pd.read_csv(EXPENSE_FILE)

    expenses = df[df["employee_id"] == employee_id]

    if expenses.empty:
        return {
            "success": False,
            "employee_id": employee_id,
            "message": "No expense records found."
        }

    total = expenses["amount"].sum()

    return {
        "success": True,
        "employee_id": employee_id,
        "total_expenses": float(total),
        "expenses": expenses.to_dict(orient="records")
    }


def get_expenses_by_category(employee_id, category):
    """Return expenses for an employee filtered by category."""

    df = pd.read_csv(EXPENSE_FILE)

    expenses = df[
        (df["employee_id"] == employee_id)
        &
        (df["category"].str.lower() == category.lower())
    ]

    if expenses.empty:
        return {
            "success": False,
            "employee_id": employee_id,
            "category": category,
            "total": 0,
            "message": "No expenses found."
        }

    total = expenses["amount"].sum()

    return {
        "success": True,
        "employee_id": employee_id,
        "category": category,
        "total": float(total),
        "records": expenses.to_dict(orient="records")
    }