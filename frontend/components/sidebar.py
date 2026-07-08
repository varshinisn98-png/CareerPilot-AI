import streamlit as st


NAV_ITEMS = [
    ("🏠 Dashboard", "dashboard"),
    ("📄 Upload Resume", "upload_resume"),
    ("💬 Resume Chat", "resume_chat"),
    ("🎤 Interview Prep", "interview"),
    ("📝 Cover Letter", "cover_letter"),
]


def render_sidebar():
    """Render the navigation sidebar. Only shown when user is logged in."""
    if not st.session_state.get("token"):
        return

    with st.sidebar:
        st.markdown("## 🚀 CareerPilot AI")
        st.divider()

        current_page = st.session_state.get("page", "dashboard")

        for label, page_key in NAV_ITEMS:
            is_active = current_page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["page"] = page_key
                st.rerun()

        st.divider()

        # Resume selector
        resumes = st.session_state.get("resumes", [])
        if resumes:
            st.markdown("**Select Resume**")
            options = {r["filename"]: r["id"] for r in resumes}
            
            # Synchronize index based on current_resume_id
            current_resume_id = st.session_state.get("current_resume_id")
            default_index = 0
            if current_resume_id:
                for idx, r in enumerate(resumes):
                    if r["id"] == current_resume_id:
                        default_index = idx
                        break

            # Use dynamic key based on resume IDs to prevent Streamlit cache out-of-bounds crash on deletion
            selectbox_key = f"active_res_{'_'.join(str(r['id']) for r in resumes)}"
            selected = st.selectbox(
                "Active Resume",
                list(options.keys()),
                index=default_index,
                key=selectbox_key,
                label_visibility="collapsed",
            )
            if selected:
                st.session_state["current_resume_id"] = options[selected]

        st.divider()
        st.markdown("**⚙️ AI Config**")
        custom_key = st.text_input(
            "Custom Gemini API Key",
            value=st.session_state.get("custom_api_key", ""),
            type="password",
            placeholder="Paste new free key...",
            help="If your daily free limit is exhausted, get a new free API key at: https://aistudio.google.com/app/apikey"
        )
        if custom_key != st.session_state.get("custom_api_key", ""):
            st.session_state["custom_api_key"] = custom_key
            st.success("API key updated!")
            st.rerun()

        st.divider()
        st.caption("CareerPilot AI v1.0")
