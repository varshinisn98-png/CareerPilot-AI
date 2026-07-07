import streamlit as st
import httpx

from utils.helpers import API_BASE


def show():
    st.markdown("## 🔐 Welcome to CareerPilot AI")
    st.markdown("Sign in to continue your career journey or get started today!")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Signing in..."):
                    try:
                        res = httpx.post(
                            f"{API_BASE}/auth/login",
                            json={"email": email, "password": password},
                            timeout=10,
                        )
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["token"] = data["access_token"]

                            # Fetch user profile
                            profile_res = httpx.get(
                                f"{API_BASE}/user/me",
                                headers={"Authorization": f"Bearer {data['access_token']}"},
                                timeout=10,
                            )
                            if profile_res.status_code == 200:
                                st.session_state["user"] = profile_res.json()

                            # Fetch resume list
                            resume_res = httpx.get(
                                f"{API_BASE}/resume/history",
                                headers={"Authorization": f"Bearer {data['access_token']}"},
                                timeout=10,
                            )
                            if resume_res.status_code == 200:
                                resumes = resume_res.json()
                                st.session_state["resumes"] = resumes
                                if resumes:
                                    st.session_state["current_resume_id"] = resumes[-1]["id"]

                            st.session_state["page"] = "dashboard"
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Login failed."))
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend. Make sure the server is running.")

        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create Account", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()
