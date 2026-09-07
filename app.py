import streamlit as st

from src.agents.router import process_request


# ==================================================
# Page configuration
# ==================================================

st.set_page_config(
    page_title="Office Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# Session state
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "employee_id" not in st.session_state:
    st.session_state.employee_id = "EMP001"


# ==================================================
# Helper function
# ==================================================

def clean_response(response):
    """
    Removes Markdown code fences if the model returns
    HTML wrapped inside ```html ... ```.
    """

    if response is None:
        return ""

    response = str(response).strip()

    if response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()

        if response.lower().startswith("html"):
            response = response[4:].strip()

    return response


# ==================================================
# Custom CSS
# ==================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f6f8fb;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e6eaf0;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    .app-header {
        background: linear-gradient(
            135deg,
            #173b67 0%,
            #2563a6 100%
        );
        padding: 2rem 2.2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(23, 59, 103, 0.12);
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .app-subtitle {
        font-size: 0.98rem;
        margin-top: 0.5rem;
        opacity: 0.88;
    }

    .status-pill {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.16);
        font-size: 0.8rem;
    }

    .welcome-card {
        background: white;
        border: 1px solid #e7ebf1;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 3px 12px rgba(20, 35, 60, 0.04);
    }

    .welcome-title {
        color: #173b67;
        font-size: 1.1rem;
        font-weight: 650;
        margin-bottom: 0.35rem;
    }

    .welcome-text {
        color: #667085;
        font-size: 0.92rem;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #e7ebf1;
        box-shadow: 0 3px 12px rgba(20, 35, 60, 0.035);
    }

    div[data-testid="stChatMessage"]:has(
        div[data-testid="chatAvatarIcon-assistant"]
    ) {
        background: #ffffff;
    }

    div[data-testid="stChatMessage"]:has(
        div[data-testid="chatAvatarIcon-user"]
    ) {
        background: #edf5ff;
        border-color: #d7e8fb;
    }

    div[data-testid="stChatMessage"] p {
        line-height: 1.65;
        color: #243447;
    }

    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3 {
        color: #173b67;
        margin-top: 0.25rem;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stChatMessage"] ul {
        padding-left: 1.3rem;
    }

    div[data-testid="stChatMessage"] li {
        margin-bottom: 0.35rem;
    }

    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #173b67;
        margin-bottom: 0.2rem;
    }

    .sidebar-subtitle {
        color: #667085;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }

    .sidebar-section {
        color: #344054;
        font-size: 0.9rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 0.65rem;
    }

    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #dbe4ef;
        background: white;
        color: #344054;
        text-align: left;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #2563a6;
        color: #2563a6;
        background: #f4f8fd;
    }

    div.stButton > button[kind="secondary"] {
        width: 100%;
    }

    div[data-testid="stChatInput"] {
        border-radius: 16px;
    }

    .app-footer {
        text-align: center;
        color: #98a2b3;
        font-size: 0.78rem;
        margin-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# Sidebar
# ==================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">🏢 Office Assistant</div>
        <div class="sidebar-subtitle">
            Internal employee support portal
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Employee Details</div>',
        unsafe_allow_html=True,
    )

    employee_id = st.text_input(
        "Employee ID",
        value=st.session_state.employee_id,
        placeholder="Enter employee ID",
        label_visibility="collapsed",
    )

    st.session_state.employee_id = (
        employee_id.strip().upper()
    )

    st.markdown(
        '<div class="sidebar-section">Quick Questions</div>',
        unsafe_allow_html=True,
    )

    quick_questions = [
        "What is my employee information?",
        "How many earned leave days do I have?",
        "Show my expenses",
        "What laptop is assigned to me?",
        "What is the leave policy?",
        "Where is the Chennai office?",
    ]

    for question in quick_questions:

        if st.button(
            question,
            key=f"quick_{question}",
            use_container_width=True,
        ):
            st.session_state.pending_question = question
            st.rerun()

    st.markdown(
        '<div class="sidebar-section">Conversation</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
        type="secondary",
    ):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# Main header
# ==================================================

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">🏢 Office Assistant</div>
        <div class="app-subtitle">
            Your intelligent workplace companion for employee information,
            leave, expenses, IT assets, office details, and company policies.
        </div>
        <div class="status-pill">● Assistant online</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# Welcome card
# ==================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-title">
                Welcome to your workplace assistant
            </div>
            <div class="welcome-text">
                Ask a question using the message box below, or select a
                quick question from the sidebar to get started.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# Display chat history
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=(
            "👤"
            if message["role"] == "user"
            else "🤖"
        ),
    ):

        st.markdown(
            clean_response(message["content"]),
            unsafe_allow_html=True,
        )


# ==================================================
# Handle quick questions
# ==================================================

pending_question = st.session_state.pop(
    "pending_question",
    None,
)


# ==================================================
# Chat input
# ==================================================

user_query = st.chat_input(
    "Ask something about your office..."
)

query_to_process = user_query or pending_question


# ==================================================
# Process user query
# ==================================================

if query_to_process:

    query_to_process = query_to_process.strip()

    if not query_to_process:
        st.warning("Please enter a question.")
        st.stop()

    if not st.session_state.employee_id:
        st.warning(
            "Please enter your employee ID in the sidebar."
        )
        st.stop()

    # --------------------------------------------------
    # Save and display the user message
    # --------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query_to_process,
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(query_to_process)

    # --------------------------------------------------
    # Prepare conversation history for Gemini
    # --------------------------------------------------

    # The current question is already saved.
    # Therefore, send only the earlier messages.
    chat_history = st.session_state.messages[:-1]

    # Keep only the latest 10 messages.
    chat_history = chat_history[-10:]

    # --------------------------------------------------
    # Generate and display assistant response
    # --------------------------------------------------

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner(
            "Finding the right information..."
        ):

            result = process_request(
                query=query_to_process,
                employee_id=st.session_state.employee_id,
                chat_history=chat_history,
            )

        # The router returns:
        # (response, detected_intent)

        if isinstance(result, tuple):
            response, detected_intent = result
        else:
            response = result

        response = clean_response(response)

        st.markdown(
            response,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # Save assistant response
    # --------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


# ==================================================
# Footer
# ==================================================

st.markdown(
    """
    <div class="app-footer">
        TechNova Office Assistant · Internal Use Only
    </div>
    """,
    unsafe_allow_html=True,
)