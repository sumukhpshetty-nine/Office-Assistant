from src.tools.employee_tool import get_employee
from src.tools.leave_tool import get_leave_balance
from src.tools.expense_tool import get_expenses
from src.tools.it_tool import get_it_assets
from src.tools.office_tool import get_office_details

def classify_query(query):
    """
    Classify the user's query using keyword-based routing.

    Policy questions are checked before personal leave-balance
    questions because both may contain words such as 'leave'
    or 'available'.
    """
    query_lower = query.lower().strip()

    # Policy questions
    policy_keywords = [
        "leave policy",
        "earned leave policy",
        "casual leave policy",
        "sick leave policy",
        "leave rules",
        "leave approval",
        "carry forward",
        "how many leave days do employees receive",
        "how many earned leave days are provided",
        "company policy",
        "policy",
        "guidelines",
        "handbook",
    ]

    if any(keyword in query_lower for keyword in policy_keywords):
        return "policy"

    # Personal leave-balance questions
    balance_keywords = [
        "my leave balance",
        "my remaining leave",
        "how much leave do i have",
        "how many leaves do i have",
        "remaining earned leave",
        "available leave balance",
    ]

    if any(keyword in query_lower for keyword in balance_keywords):
        return "leave"

    # Expense-related questions
    expense_keywords = [
        "expense",
        "reimbursement",
        "claim",
        "travel expense",
        "expense status",
    ]

    if any(keyword in query_lower for keyword in expense_keywords):
        return "expense"

    # IT-related questions
    it_keywords = [
        "laptop",
        "asset",
        "computer",
        "device",
        "it support",
        "software",
        "hardware",
    ]

    if any(keyword in query_lower for keyword in it_keywords):
        return "it"

    # Office-location questions
    office_keywords = [
        "office location",
        "office address",
        "where is the office",
        "office in",
    ]

    if any(keyword in query_lower for keyword in office_keywords):
        return "office"

    # Employee-information questions
    employee_keywords = [
        "employee",
        "manager",
        "department",
        "designation",
        "employee details",
    ]

    if any(keyword in query_lower for keyword in employee_keywords):
        return "employee"

    return "general"

def classify_query(query):
    query_lower = query.lower()

    if any(word in query_lower for word in [
        "policy",
        "guideline",
        "guidelines",
        "rule",
        "rules",
        "handbook",
    ]):
        return "policy"

    if any(word in query_lower for word in [
        "leave",
        "casual leave",
        "earned leave",
        "sick leave",
        "leave balance",
        "holiday balance",
    ]):
        return "leave"

    if any(word in query_lower for word in [
        "expense", "expenses", "reimbursement",
        "spending", "spent"
    ]):
        return "expense"

    if any(word in query_lower for word in [
        "laptop", "computer", "monitor", "asset",
        "it asset", "equipment", "device"
    ]):
        return "it_asset"

    if any(word in query_lower for word in [
        "office", "location", "address",
        "working hours", "facilities"
    ]):
        return "office"

    if any(word in query_lower for word in [
        "employee", "manager", "department",
        "designation", "role", "name"
    ]):
        return "employee"

    return "unknown"


def format_leave_response(result):
    if not result.get("success"):
        return result.get("message", "Leave details not found.")

    return (
        f"Leave balance for {result['employee_id']}:\n"
        f"- Casual leave: {result['casual_leave']}\n"
        f"- Earned leave: {result['earned_leave']}\n"
        f"- Sick leave: {result['sick_leave']}"
    )


def format_expense_response(result):
    if not result.get("success"):
        return result.get("message", "Expense details not found.")

    response = (
        f"Total expenses for {result['employee_id']}: "
        f"₹{result['total_expenses']:.2f}\n\n"
        "Expense records:"
    )

    for expense in result.get("expenses", []):
        response += (
            f"\n- {expense['date']} | "
            f"{expense['category']} | "
            f"{expense['description']} | "
            f"₹{expense['amount']} | "
            f"{expense['status']}"
        )

    return response


def format_it_response(result):
    if not result.get("success"):
        return result.get("message", "No IT assets found.")

    response = f"IT assets assigned to {result['employee_id']}:\n"

    for asset in result.get("assets", []):
        response += (
            f"- {asset['asset_type']}: {asset['asset_name']}\n"
            f"  Serial number: {asset['serial_number']}\n"
            f"  Status: {asset['status']}\n"
            f"  Assigned date: {asset['assigned_date']}\n"
        )

    return response


def format_employee_response(result):
    if not result.get("success"):
        return result.get("message", "Employee details not found.")

    employee = result.get("employee", result)

    return (
        f"Employee ID: {employee.get('employee_id', 'N/A')}\n"
        f"Name: {employee.get('name', 'N/A')}\n"
        f"Department: {employee.get('department', 'N/A')}\n"
        f"Designation: {employee.get('designation', 'N/A')}\n"
        f"Manager: {employee.get('manager', 'N/A')}"
    )


def extract_office_location(query):
    locations = [
        "Chennai",
        "Bangalore",
        "Bengaluru",
        "Mumbai",
        "Delhi",
        "Hyderabad",
        "Pune",
    ]

    query_lower = query.lower()

    for location in locations:
        if location.lower() in query_lower:
            return location

    return None


# RAG is initialized only when the first policy question is asked.
# This avoids loading the embedding model during ordinary tool queries.
_rag = None

def answer_policy_query(query):
    global _rag

    try:
        from person1.p1_rag import build_rag

        if _rag is None:
            _rag = build_rag()

        result = _rag.search_company_policy(
            query,
            top_k=2,
            generate_llm_answer=False
        )

        results = result.get("results", [])

        if not results:
            return "I could not find relevant information in the company policies."

        response = "Relevant policy information:\n\n"

        for index, item in enumerate(results, start=1):
            text = item.get("text", "").strip()

            if text:
                response += f"{index}. {text}\n\n"

        return response.strip()

    except Exception as error:
        print(f"RAG error: {error}")
        return "Sorry, I could not retrieve the policy information."

def process_request(query, employee_id, chat_history=None):
    if not query or not query.strip():
        return "Please enter a question."

    if not employee_id or not employee_id.strip():
        return "Please enter your employee ID."

    query = query.strip()
    employee_id = employee_id.strip().upper()

    try:
        intent = classify_query(query)

        if intent == "leave":
            result = get_leave_balance(employee_id)
            return format_leave_response(result)

        if intent == "expense":
            result = get_expenses(employee_id)
            return format_expense_response(result)

        if intent == "it_asset":
            result = get_it_assets(employee_id)
            return format_it_response(result)

        if intent == "employee":
            result = get_employee(employee_id)
            return format_employee_response(result)

        if intent == "office":
            location = extract_office_location(query)

            if not location:
                return (
                    "Please mention the office location, for example: "
                    "'What are the office details for Chennai?'"
                )

            result = get_office_details(location)

            if not result.get("success"):
                return result.get("message", "Office details not found.")

            office = result["office"]

            return (
                f"Office: {office['office_name']}\n"
                f"Location: {office['location']}\n"
                f"Address: {office['address']}\n"
                f"Working hours: {office['working_hours']}\n"
                f"Facilities: {office['facilities']}"
            )

        if intent == "policy":
            return answer_policy_query(query)

        return (
            "I could not identify your question. You can ask about "
            "leave balance, expenses, IT assets, employee details, "
            "office locations, or company policies."
        )

    except FileNotFoundError:
        return "The required data file is missing."

    except Exception as error:
        print(f"Router error: {error}")
        return "Sorry, something went wrong while processing your request."