import os
import json
from enum import Enum

from dotenv import load_dotenv
from google import genai


load_dotenv()


class Intent(Enum):
    POLICY_QUERY = "policy_query"
    LEAVE_BALANCE = "leave_balance"
    EXPENSE_QUERY = "expense_query"
    IT_ASSET_QUERY = "it_asset_query"
    OFFICE_LOCATION = "office_location"
    GENERAL_QUERY = "general_query"


class IntentAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        self.client = genai.Client(api_key=api_key)

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

    def classify(
        self,
        query,
        history=None,
        previous_intent=None
    ):

        history = history or []

        history_text = ""

        if history:
            history_text = "\nPrevious conversation:\n"

            for message in history[-5:]:
                history_text += (
                    f"{message['role']}: "
                    f"{message['content']}\n"
                )

        previous_intent_text = previous_intent or "NONE"

        prompt = f"""
You are an intent classification agent for an enterprise employee assistant.

Your job is ONLY to identify what the employee is asking for.

Classify the employee query into exactly ONE of these intents:

POLICY_QUERY
LEAVE_BALANCE
EXPENSE_QUERY
IT_ASSET_QUERY
OFFICE_LOCATION
GENERAL_QUERY

Intent definitions:

POLICY_QUERY:
Questions about company policies, rules, limits, eligibility,
or procedures.

Examples:
- What is the work from home policy?
- What is the travel reimbursement limit?
- How many WFH days are allowed?

LEAVE_BALANCE:
Questions about the employee's own leave balance,
remaining leaves, or available leave.

Examples:
- How many leaves do I have?
- How many casual leaves are remaining?
- What is my leave balance?
- What about sick leave?
- How many earned leaves are left?

EXPENSE_QUERY:
Questions about the employee's own expenses,
reimbursements, submitted expenses, or expense status.

Examples:
- Show my expenses.
- What is the status of my reimbursement?
- Which expenses have I submitted?

IT_ASSET_QUERY:
Questions about the employee's assigned IT equipment.

Examples:
- Which laptop is assigned to me?
- What monitor do I have?
- Show my IT assets.

OFFICE_LOCATION:
Questions about office locations, addresses,
buildings, or where an office/team is located.

Examples:
- Where is the Chennai office?
- What is the Bangalore office address?
- Where is the HR team located?

GENERAL_QUERY:
General questions that do not belong to the above categories.

Examples:
- What can you help me with?
- Hello
- Who are you?

Important rules:

- Consider the previous conversation.
- Consider the previous intent.
- Follow-up questions should inherit the previous intent
  when the current query depends on the previous answer.
- "What about sick leave?" after "What is my leave balance?"
  MUST be classified as LEAVE_BALANCE.
- "And earned leave?" after a leave question is LEAVE_BALANCE.
- "How much is remaining?" after a leave question is LEAVE_BALANCE.
- "What about that?" should use the previous intent.
- Do not classify a short follow-up as GENERAL_QUERY
  merely because it contains only a few words.
- Return ONLY valid JSON.
- The intent value MUST be one of:
  POLICY_QUERY, LEAVE_BALANCE, EXPENSE_QUERY,
  IT_ASSET_QUERY, OFFICE_LOCATION, GENERAL_QUERY.
- Confidence must be a number between 0 and 1.

Previous intent:
{previous_intent_text}

Employee query:
{query}

{history_text}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "intent": {
                                "type": "STRING"
                            },
                            "confidence": {
                                "type": "NUMBER"
                            }
                        },
                        "required": [
                            "intent",
                            "confidence"
                        ]
                    }
                }
            )

            result = json.loads(response.text)

            intent = result.get(
                "intent",
                "GENERAL_QUERY"
            ).strip().upper()

            confidence = float(
                result.get("confidence", 0)
            )

            print(
                f"Gemini raw intent: {intent} "
                f"| Confidence: {confidence}"
            )

            return {
                "intent": intent,
                "confidence": confidence
            }

        except Exception as error:
            print(
                f"Gemini classification error: {error}"
            )

            # If Gemini is temporarily unavailable, preserve
            # the previous successful intent.
            if previous_intent:
                print(
                    "Using previous intent because "
                    f"classification failed: {previous_intent}"
                )

                return {
                    "intent": previous_intent,
                    "confidence": 0.0,
                    "fallback": True
                }

            return {
                "intent": "GENERAL_QUERY",
                "confidence": 0.0,
                "fallback": True
            }