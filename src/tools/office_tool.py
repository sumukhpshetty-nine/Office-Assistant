import pandas as pd

from src.paths import OFFICE_FILE


def get_office_details(location):
    """Return information about a TechNova office."""

    df = pd.read_csv(OFFICE_FILE)

    office = df[
        df["location"].str.lower() == location.lower()
    ]

    if office.empty:
        return {
            "success": False,
            "message": "Office location not found."
        }

    return {
        "success": True,
        "office": office.iloc[0].to_dict()
    }