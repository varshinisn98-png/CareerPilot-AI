import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"

SUGGESTED_QUESTIONS = [
    "What are my key strengths?",
    "What skills am I missing?",
    "Suggest 3 projects I can build.",
    "What certifications should I pursue?",
    "What roles am I best suited for?",
    "How can I improve my resume?",
]


from utils.helpers import get_headers

_headers = get_headers


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("## 💬 Chat with Your Resume")
    st.markdown("Ask anything about your resume. Powered by RAG + Gemini AI.")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        st.warning("Please upload a resume first.")
        if st.button("Go to Upload"):
            st.session_state["page"] = "upload_resume"
            st.rerun()
        return

    # Initialize chat history in session
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    # Load history from backend on first render
    if not st.session_state["chat_messages"]:
        try:
            res = httpx.get(
                f"{API_BASE}/chat/history/{resume_id}", headers=_headers(), timeout=10
            )
            if res.status_code == 200:
                for msg in res.json():
                    st.session_state["chat_messages"].append(
                        {"role": msg["role"], "content": msg["message"]}
                    )
        except Exception:
            pass

    # Render chat messages
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Suggested questions
    if not st.session_state["chat_messages"]:
        st.markdown("**💡 Try asking:**")
        cols = st.columns(3)
        for i, q in enumerate(SUGGESTED_QUESTIONS):
            with cols[i % 3]:
                if st.button(q, key=f"suggest_{i}", use_container_width=True):
                    st.session_state["pending_message"] = q
                    st.rerun()

    # Check for pending message (from suggested buttons)
    pending = st.session_state.pop("pending_message", None)

    # Chat input
    user_input = st.chat_input("Ask about your resume...") or pending

    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = httpx.post(
                        f"{API_BASE}/chat/ask",
                        headers=_headers(),
                        json={"resume_id": resume_id, "message": user_input},
                        timeout=30,
                    )
                    if res.status_code == 200:
                        reply = res.json()["reply"]
                        st.write(reply)
                        st.session_state["chat_messages"].append(
                            {"role": "assistant", "content": reply}
                        )
                    else:
                        err = res.json().get("detail", "Error getting response.")
                        st.error(err)
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")

    # Clear chat button
    if st.session_state["chat_messages"]:
        if st.button("🗑️ Clear Chat History"):
            try:
                httpx.delete(
                    f"{API_BASE}/chat/history/{resume_id}", headers=_headers(), timeout=10
                )
            except Exception:
                pass
            st.session_state["chat_messages"] = []
            st.rerun()
