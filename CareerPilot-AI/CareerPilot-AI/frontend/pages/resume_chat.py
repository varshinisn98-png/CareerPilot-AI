import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"

SUGGESTED = [
    "What are my key strengths?",
    "What skills am I missing?",
    "Suggest 3 projects I can build",
    "What certifications should I get?",
    "What roles am I suited for?",
    "How can I improve my resume?",
    "Summarize my experience",
    "What is my education background?",
]


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, info_box, divider

    page_header("Resume Chat", "Ask anything about your resume — powered by RAG + Gemini AI", "💬")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        info_box("Please upload a resume first to start chatting.", "⚠️", "#f59e0b")
        if st.button("📤 Upload Resume", type="primary"):
            st.session_state["page"] = "upload_resume"; st.rerun()
        return

    # Init messages
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    # Load history once
    if not st.session_state["chat_messages"] and not st.session_state.get("chat_loaded"):
        try:
            res = httpx.get(f"{API_BASE}/chat/history/{resume_id}", headers=_headers(), timeout=10)
            if res.status_code == 200:
                for m in res.json():
                    st.session_state["chat_messages"].append(
                        {"role": m["role"], "content": m["message"]}
                    )
        except Exception:
            pass
        st.session_state["chat_loaded"] = True

    # Suggested questions (only when empty)
    if not st.session_state["chat_messages"]:
        st.markdown(
            '<div style="background:rgba(79,139,249,0.05);border:1px solid rgba(79,139,249,0.15);'
            'border-radius:14px;padding:1.2rem;margin-bottom:1rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💡 Suggested Questions")
        cols = st.columns(4)
        for i, q in enumerate(SUGGESTED):
            with cols[i % 4]:
                if st.button(q, key=f"sq_{i}", use_container_width=True):
                    st.session_state["pending_q"] = q
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"],
                                 avatar="👤" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])

    # Handle pending suggested question
    pending = st.session_state.pop("pending_q", None)
    user_input = st.chat_input("Ask about your resume...") or pending

    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    res = httpx.post(f"{API_BASE}/chat/ask", headers=_headers(),
                                     json={"resume_id": resume_id, "message": user_input}, timeout=30)
                    if res.status_code == 200:
                        reply = res.json()["reply"]
                        st.markdown(reply)
                        st.session_state["chat_messages"].append(
                            {"role": "assistant", "content": reply}
                        )
                    else:
                        err = "Sorry, I couldn't process that. Please try again."
                        st.error(err)
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Footer actions
    if st.session_state["chat_messages"]:
        divider()
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                try:
                    httpx.delete(f"{API_BASE}/chat/history/{resume_id}",
                                 headers=_headers(), timeout=10)
                except Exception:
                    pass
                st.session_state["chat_messages"] = []
                st.session_state.pop("chat_loaded", None)
                st.rerun()
