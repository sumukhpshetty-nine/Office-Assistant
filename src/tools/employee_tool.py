import pandas as pd

from src.paths import EMPLOYEE_FILE


def get_employee(employee_id):
    """Return employee details for a given employee ID."""

    df = pd.read_csv(EMPLOYEE_FILE)

    employee = df[df["employee_id"] == employee_id]

    if employee.empty:
        return {
            "success": False,
            "message": "Employee not found."
        }

    record = employee.iloc[0].to_dict()

    return {
        "success": True,
        "employee": record
    }


def search_employee(name):
    """Search employees by name."""

    df = pd.read_csv(EMPLOYEE_FILE)

    matches = df[
        df["name"].str.contains(
            name,
            case=False,
            na=False
        )
    ]

    if matches.empty:
        return {
            "success": False,
            "message": "No employee found."
        }

    return {
        "success": True,
        "employees": matches.to_dict(orient="records")
    }