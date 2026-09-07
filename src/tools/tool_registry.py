from src.tools.employee_tool import (
    get_employee,
    search_employee
)

from src.tools.leave_tool import (
    get_leave_balance
)

from src.tools.expense_tool import (
    get_expenses,
    get_expenses_by_category
)

from src.tools.it_tool import (
    get_it_assets
)

from src.tools.office_tool import (
    get_office_details
)


EMPLOYEE_TOOLS = {
    "get_employee": get_employee,
    "search_employee": search_employee,
    "get_leave_balance": get_leave_balance,
    "get_expenses": get_expenses,
    "get_expenses_by_category": get_expenses_by_category,
    "get_it_assets": get_it_assets,
    "get_office_details": get_office_details,
}