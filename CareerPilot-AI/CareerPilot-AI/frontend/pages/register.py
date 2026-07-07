import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def show():
    st.markdown("<style>[data-testid='stSidebar']{display:none}</style>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center;padding:2rem 0 1.5rem 0;">
                <div style="font-size:3rem;margin-bottom:0.5rem;">🚀</div>
                <h1 style="background:linear-gradient(135deg,#4f8bf9,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-size:2rem;font-weight:700;margin:0;">CareerPilot AI</h1>
                <p style="color:#64748b;margin:6px 0 0 0;font-size:0.95rem;">
                    Start your AI-powered career journey</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                border-radius:20px;padding:2rem;">
                <h2 style="color:#f1f5f9;font-size:1.3rem;font-weight:600;margin:0 0 1.5rem 0;
                    text-align:center;">Create Your Account ✨</h2>
            """,
            unsafe_allow_html=True,
        )

        with st.form("register_form"):
            full_name = st.text_input("👤 Full Name", placeholder="Jane Doe")
            email = st.text_input("📧 Email Address", placeholder="you@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Min. 8 characters")
            confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password")
            submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

        st.markdown("</div>", unsafe_allow_html=True)

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
                            st.success("🎉 Account created! Redirecting to login...")
                            import time; time.sleep(1)
                            st.session_state["page"] = "login"
                            st.rerun()
                        else:
                            try:
                                msg = res.json().get("detail", "Registration failed.")
                            except Exception:
                                msg = f"Error {res.status_code}: {res.text[:200]}"
                            st.error(msg)
                    except httpx.ConnectError:
                        st.error("⚠️ Cannot connect to server. Make sure the backend is running.")

        st.markdown(
            '<div style="text-align:center;margin-top:1.5rem;">'
            '<p style="color:#475569;font-size:0.9rem;margin:0;">Already have an account?</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign In →", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
