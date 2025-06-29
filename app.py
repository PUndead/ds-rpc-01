#pip install streamlit
import streamlit as st
import requests

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="FinSolve",
    page_icon="🤖",
    layout="wide"
)

# --- Sidebar: User Authentication and Role Selection ---
st.sidebar.title("📅 User Panel")
st.sidebar.subheader("Login")

username = st.sidebar.text_input("Username")
role = st.sidebar.selectbox("Select Role", [
    "Employee", "Finance", "Marketing", "HR", "Engineering", "C-Level"
])
authenticate = st.sidebar.button("Login")

# Simulate authentication
session_state = st.session_state
if 'authenticated' not in session_state:
    session_state.authenticated = False
if 'chat_history' not in session_state:
    session_state.chat_history = []

if authenticate:
    if username:
        session_state.authenticated = True
        session_state.username = username
        session_state.role = role
    else:
        st.sidebar.warning("Please enter a username.")

# --- Main Chat Interface ---
st.title("🌐 FinSolve Role-Based AI Chatbot")

if session_state.authenticated:
    st.success(f"Welcome, {session_state.username} ({session_state.role})")

    user_input = st.text_input("Ask a question:", placeholder="e.g., Show me the Q2 financial report...")
    ask_button = st.button("Send")

    chat_area = st.container()

    if ask_button and user_input:
        # Display user query
        session_state.chat_history.append(("user", user_input))

        # --- Simulated Backend Request ---
        with st.spinner("Processing your query..."):
            response = requests.post(
                "http://localhost:8000/query",
                json={
                    "user": session_state.username,
                    "role": session_state.role,
                    "query": user_input
                }
            )

        if response.status_code == 200:
            result = response.json()
            session_state.chat_history.append(("bot", result['response']))
        else:
            session_state.chat_history.append(("bot", "Error fetching response from server."))

    # --- Display Chat History ---
    with chat_area:
        for sender, msg in session_state.chat_history:
            if sender == "user":
                st.markdown(f"**You:** {msg}")
            else:
                st.markdown(f"**Chatbot:** {msg}")

else:
    st.warning("Please log in using the sidebar to access the chatbot.")

# --- Footer ---
st.markdown("---")
st.markdown("Built by FinSolve AI Engineering | © 2025")
# After code is executed,
#streamlit run "path of saved file"
