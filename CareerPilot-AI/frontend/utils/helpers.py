import streamlit as st

def get_headers():
    h = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    if st.session_state.get("custom_api_key"):
        h["X-Gemini-API-Key"] = st.session_state["custom_api_key"]
    return h
