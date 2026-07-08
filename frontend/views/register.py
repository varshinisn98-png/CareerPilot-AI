import streamlit as st
import httpx

from utils.helpers import API_BASE


def show():
    st.markdown("## 📝 Create Your Account")
    st.markdown("Join CareerPilot AI and supercharge your career.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="Jane Doe")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Min. 8 characters")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submitted:
            if not all([full_name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                with st.spinner("Creating your account..."):
                    try:
                        res = httpx.post(
                            f"{API_BASE}/auth/register",
                            json={"full_name": full_name, "email": email, "password": password},
                            timeout=10,
                        )
                        if res.status_code == 201:
                            st.success("Account created! Please sign in.")
                            st.session_state["page"] = "login"
                            st.rerun()
                        else:
                            try:
                                detail = res.json().get("detail", "Registration failed.")
                            except Exception:
                                detail = f"Server error (status {res.status_code}): {res.text[:300]}"
                            st.error(detail)
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend. Make sure uvicorn is running on port 8000.")

        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Sign In", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
