import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def show():
    # Hide sidebar on auth pages
    st.markdown("<style>[data-testid='stSidebar']{display:none}</style>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # Hero
        st.markdown(
            """
            <div style="text-align:center;padding:2rem 0 1.5rem 0;">
                <div style="font-size:3rem;margin-bottom:0.5rem;">🚀</div>
                <h1 style="background:linear-gradient(135deg,#4f8bf9,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-size:2rem;font-weight:700;margin:0;">CareerPilot AI</h1>
                <p style="color:#64748b;margin:6px 0 0 0;font-size:0.95rem;">
                    Your AI-powered career co-pilot</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Card
        st.markdown(
            """
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                border-radius:20px;padding:2rem;">
                <h2 style="color:#f1f5f9;font-size:1.3rem;font-weight:600;margin:0 0 1.5rem 0;
                    text-align:center;">Welcome Back 👋</h2>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="you@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        res = httpx.post(f"{API_BASE}/auth/login",
                                         json={"email": email, "password": password}, timeout=10)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["token"] = data["access_token"]
                            headers = {"Authorization": f"Bearer {data['access_token']}"}

                            profile = httpx.get(f"{API_BASE}/user/me", headers=headers, timeout=10)
                            if profile.status_code == 200:
                                st.session_state["user"] = profile.json()

                            resumes = httpx.get(f"{API_BASE}/resume/history", headers=headers, timeout=10)
                            if resumes.status_code == 200:
                                st.session_state["resumes"] = resumes.json()
                                if resumes.json():
                                    st.session_state["current_resume_id"] = resumes.json()[-1]["id"]

                            st.session_state["page"] = "dashboard"
                            st.rerun()
                        else:
                            try:
                                msg = res.json().get("detail", "Invalid credentials.")
                            except Exception:
                                msg = "Login failed. Please try again."
                            st.error(msg)
                    except httpx.ConnectError:
                        st.error("⚠️ Cannot connect to server. Make sure the backend is running.")

        st.markdown(
            """
            <div style="text-align:center;margin-top:1.5rem;">
                <p style="color:#475569;font-size:0.9rem;margin:0;">Don't have an account?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Create Free Account →", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()

        # Features
        st.markdown(
            """
            <div style="margin-top:2rem;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:rgba(79,139,249,0.06);border:1px solid rgba(79,139,249,0.15);
                    border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.3rem;">🎯</div>
                    <div style="color:#94a3b8;font-size:0.75rem;margin-top:4px;">ATS Scoring</div>
                </div>
                <div style="background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);
                    border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.3rem;">💬</div>
                    <div style="color:#94a3b8;font-size:0.75rem;margin-top:4px;">AI Resume Chat</div>
                </div>
                <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.15);
                    border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.3rem;">🎤</div>
                    <div style="color:#94a3b8;font-size:0.75rem;margin-top:4px;">Interview Prep</div>
                </div>
                <div style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);
                    border-radius:10px;padding:10px;text-align:center;">
                    <div style="font-size:1.3rem;">📝</div>
                    <div style="color:#94a3b8;font-size:0.75rem;margin-top:4px;">Cover Letters</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
