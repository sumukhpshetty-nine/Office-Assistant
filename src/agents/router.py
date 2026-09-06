from .intent_agent import Intent


class Router:

    CONFIDENCE_THRESHOLD = 0.70

    def route(self, intent_result, query, employee_id=None):

        intent = intent_result["intent"].lower()
        confidence = float(intent_result.get("confidence", 0))

        # Handle low-confidence predictions
        if confidence < self.CONFIDENCE_THRESHOLD:
            return {
                "action": "CLARIFY",
                "source": "INTENT_AGENT",
                "query": query,
                "confidence": confidence,
                "message": (
                    "I'm not completely sure what you're asking. "
                    "Could you please provide a little more detail?"
                )
            }

        # Route high-confidence intents
        if intent == Intent.POLICY_QUERY.value:
            return {
                "action": "SEARCH_POLICY",
                "source": "RAG",
                "query": query,
                "confidence": confidence
            }

        elif intent == Intent.LEAVE_BALANCE.value:
            return {
                "action": "GET_LEAVE_BALANCE",
                "source": "EMPLOYEE_DATA",
                "employee_id": employee_id,
                "confidence": confidence
            }

        elif intent == Intent.EXPENSE_QUERY.value:
            return {
                "action": "GET_EXPENSES",
                "source": "EMPLOYEE_DATA",
                "employee_id": employee_id,
                "confidence": confidence
            }

        elif intent == Intent.IT_ASSET_QUERY.value:
            return {
                "action": "GET_IT_ASSET",
                "source": "EMPLOYEE_DATA",
                "employee_id": employee_id,
                "confidence": confidence
            }

        elif intent == Intent.OFFICE_LOCATION.value:
            return {
                "action": "GET_OFFICE_LOCATION",
                "source": "OFFICE_DATA",
                "query": query,
                "confidence": confidence
            }

        else:
            return {
                "action": "GENERAL_RESPONSE",
                "source": "LLM",
                "query": query,
                "confidence": confidence
            }


def process_request(query, employee_id=None, history=None):

    from .intent_agent import IntentAgent

    agent = IntentAgent()
    router = Router()

    # Gemini is called once to understand the request
    intent_result = agent.classify(
        query,
        history=history
    )

    # Routing happens locally
    route = router.route(
        intent_result,
        query,
        employee_id
    )

    return {
        "query": query,
        "intent": intent_result,
        "route": route
    }
