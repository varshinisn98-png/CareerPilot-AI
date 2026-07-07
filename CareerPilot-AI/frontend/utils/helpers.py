import streamlit as st
import os

API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api")

def get_headers():
    h = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
    if st.session_state.get("custom_api_key"):
        h["X-Gemini-API-Key"] = st.session_state["custom_api_key"]
    return h
