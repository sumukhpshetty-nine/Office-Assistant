import pandas as pd

from src.paths import IT_FILE


def get_it_assets(employee_id):
    """Return IT assets assigned to an employee."""

    df = pd.read_csv(IT_FILE)

    assets = df[df["employee_id"] == employee_id]

    if assets.empty:
        return {
            "success": False,
            "employee_id": employee_id,
            "message": "No IT assets assigned."
        }

    return {
        "success": True,
        "employee_id": employee_id,
        "assets": assets.to_dict(orient="records")
    }