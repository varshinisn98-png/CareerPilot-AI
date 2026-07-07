import streamlit as st

NAV_ITEMS = [
    ("🏠", "Dashboard", "dashboard"),
    ("📄", "Upload Resume", "upload_resume"),
    ("🎯", "ATS Analysis", "ats"),
    ("💬", "Resume Chat", "resume_chat"),
    ("🎤", "Interview Prep", "interview"),
    ("📝", "Cover Letter", "cover_letter"),
    ("👤", "Profile", "profile"),
]


def render_sidebar():
    if not st.session_state.get("token"):
        return

    with st.sidebar:
        # Logo
        st.markdown(
            """
            <div style="text-align:center;padding:1rem 0 0.5rem 0;">
                <div style="font-size:2.5rem;">🚀</div>
                <div style="background:linear-gradient(135deg,#4f8bf9,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-size:1.2rem;font-weight:700;">CareerPilot AI</div>
                <div style="color:#475569;font-size:0.75rem;margin-top:2px;">Your Career Co-Pilot</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:0.5rem 0;">',
            unsafe_allow_html=True,
        )

        # User info
        user = st.session_state.get("user", {})
        if user:
            st.markdown(
                f"""
                <div style="background:rgba(79,139,249,0.08);border:1px solid rgba(79,139,249,0.2);
                    border-radius:12px;padding:10px 12px;margin-bottom:12px;">
                    <div style="color:#f1f5f9;font-weight:600;font-size:0.9rem;">
                        👤 {user.get('full_name','User')}</div>
                    <div style="color:#64748b;font-size:0.75rem;margin-top:2px;">
                        {user.get('email','')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Navigation
        st.markdown(
            '<p style="color:#475569;font-size:0.7rem;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.08em;margin:0 0 6px 4px;">Navigation</p>',
            unsafe_allow_html=True,
        )

        current = st.session_state.get("page", "dashboard")
        for icon, label, key in NAV_ITEMS:
            is_active = current == key
            bg = "background:linear-gradient(135deg,rgba(79,139,249,0.2),rgba(124,58,237,0.2));border:1px solid rgba(79,139,249,0.3);" if is_active else "background:transparent;border:1px solid transparent;"
            color = "#f1f5f9" if is_active else "#94a3b8"

            st.markdown(
                f"""
                <div style="{bg}border-radius:10px;padding:0;margin-bottom:2px;">
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:0.8rem 0;">',
            unsafe_allow_html=True,
        )

        # Resume selector
        resumes = st.session_state.get("resumes", [])
        if resumes:
            st.markdown(
                '<p style="color:#475569;font-size:0.7rem;font-weight:600;'
                'text-transform:uppercase;letter-spacing:0.08em;margin:0 0 6px 4px;">Active Resume</p>',
                unsafe_allow_html=True,
            )
            options = {r["filename"]: r["id"] for r in resumes}
            selected = st.selectbox("", list(options.keys()), key="sidebar_resume",
                                    label_visibility="collapsed")
            if selected:
                st.session_state["current_resume_id"] = options[selected]

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

        # Logout
        if st.button("🚪  Sign Out", key="sidebar_logout", use_container_width=True):
            for k in ["token", "user", "current_resume_id", "resumes", "chat_messages"]:
                st.session_state.pop(k, None)
            st.session_state["page"] = "login"
            st.rerun()

        st.markdown(
            '<p style="color:#2d3748;font-size:0.7rem;text-align:center;margin-top:1rem;">'
            'CareerPilot AI v1.0</p>',
            unsafe_allow_html=True,
        )
