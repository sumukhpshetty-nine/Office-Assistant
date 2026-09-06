from src.tools.employee_tool import get_employee, search_employee
from src.tools.leave_tool import get_leave_balance
from src.tools.expense_tool import get_expenses_by_category
from src.tools.it_tool import get_it_assets
from src.tools.office_tool import get_office_details


print("\n===== EMPLOYEE LOOKUP =====")
print(get_employee("EMP001"))

print("\n===== EMPLOYEE SEARCH =====")
print(search_employee("Rahul"))

print("\n===== LEAVE BALANCE =====")
print(get_leave_balance("EMP001"))

print("\n===== TRAVEL EXPENSES =====")
print(get_expenses_by_category("EMP001", "Travel"))

print("\n===== IT ASSETS =====")
print(get_it_assets("EMP001"))

print("\n===== OFFICE DETAILS =====")
print(get_office_details("Bangalore"))