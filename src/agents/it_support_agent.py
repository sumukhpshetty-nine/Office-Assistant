def answer_it_query(query, employee_id):
    query_lower = query.lower()

    if "password" in query_lower or "reset" in query_lower:
        return (
            "To reset your password, open the company password portal "
            "and follow the reset instructions. If you are unable to reset it, "
            "contact the IT helpdesk."
        )

    if "vpn" in query_lower:
        return (
            "Please check your internet connection, reconnect to the company VPN, "
            "and try again. If the issue continues, contact the IT helpdesk."
        )

    if "laptop" in query_lower or "computer" in query_lower:
        return (
            "Please restart your laptop and check whether the issue persists. "
            "If it does, contact the IT helpdesk with your device details."
        )

    if "email" in query_lower or "outlook" in query_lower:
        return (
            "Please check your internet connection and restart your email application. "
            "If the issue continues, contact the IT helpdesk."
        )

    return (
        "I can currently help with common password, VPN, laptop, "
        "and email-related issues."
    )