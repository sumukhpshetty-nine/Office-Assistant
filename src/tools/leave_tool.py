import pandas as pd

from src.paths import LEAVE_FILE


def get_leave_balance(employee_id):
    """Return remaining leave balance for an employee."""

    df = pd.read_csv(LEAVE_FILE)

    employee = df[df["employee_id"] == employee_id]

    if employee.empty:
        return {
            "success": False,
            "message": "Employee not found."
        }

    record = employee.iloc[0]

    return {
        "success": True,
        "employee_id": employee_id,
        "casual_leave": int(record["casual_leave"]),
        "earned_leave": int(record["earned_leave"]),
        "sick_leave": int(record["sick_leave"])
    }