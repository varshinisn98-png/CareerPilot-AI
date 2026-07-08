import streamlit as st


def render_navbar():
    """Render the top navigation bar with logo and user info."""
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        try:
            st.image("assets/logo.png", width=60)
        except Exception:
            st.markdown("### 🚀")

    with col2:
        st.markdown(
            "<h2 style='text-align:center; color:#4F8BF9;'>CareerPilot AI</h2>"
            "<p style='text-align:center; color:#888; margin-top:-12px;'>"
            "Your AI-powered career co-pilot</p>",
            unsafe_allow_html=True,
        )

    with col3:
        if st.session_state.get("token"):
            user = st.session_state.get("user", {})
            st.markdown(f"👤 **{user.get('full_name', 'User')}**")
            if st.button("Logout", key="navbar_logout"):
                for key in ["token", "user", "current_resume_id"]:
                    st.session_state.pop(key, None)
                st.session_state["page"] = "login"
                st.rerun()

    st.divider()
