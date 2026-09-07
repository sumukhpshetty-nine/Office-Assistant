from pathlib import Path

# Project root = Office-Assistant/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "employee_data"

EMPLOYEE_FILE = DATA_DIR / "employees.csv"
LEAVE_FILE = DATA_DIR / "leave_balance.csv"
EXPENSE_FILE = DATA_DIR / "expense_records.csv"
IT_FILE = DATA_DIR / "IT_assets.csv"
OFFICE_FILE = DATA_DIR / "office_locations.csv"