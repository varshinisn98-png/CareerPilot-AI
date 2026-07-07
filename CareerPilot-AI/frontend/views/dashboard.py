import streamlit as st
import httpx
import json

API_BASE = "http://localhost:8000/api"


from utils.helpers import get_headers

_headers = get_headers


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    user = st.session_state.get("user", {})
    st.markdown(f"## 👋 Welcome, {user.get('full_name', 'User')}!")
    st.markdown("Here's a snapshot of your career progress.")

    resume_id = st.session_state.get("current_resume_id")

    # Fetch ATS result if resume is available
    ats_data = None
    if resume_id:
        try:
            res = httpx.get(f"{API_BASE}/ats/result/{resume_id}", headers=_headers(), timeout=10)
            if res.status_code == 200:
                ats_data = res.json()
        except Exception:
            pass

    st.divider()

    # ── Metrics Row ────────────────────────────────────────────────────────────
    from components.cards import metric_card, render_skill_list, ats_gauge

    if ats_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("ATS Score", f"{ats_data['ats_score']:.0f}/100", "🎯", "#4F8BF9")
        with col2:
            metric_card("JD Match", f"{ats_data.get('jd_match_percent', 0):.0f}%", "💼", "#28a745")
        with col3:
            metric_card("Skills Found", len(ats_data.get("extracted_skills", [])), "🛠️", "#ffc107")
        with col4:
            metric_card("Missing Skills", len(ats_data.get("missing_skills", [])), "⚠️", "#dc3545")

        st.divider()

        col_l, col_r = st.columns([1, 2])
        with col_l:
            st.markdown("### 🎯 ATS Score")
            ats_gauge(ats_data["ats_score"])

        with col_r:
            st.markdown("### 💪 Strengths")
            st.info(ats_data.get("strengths", "Run ATS analysis to see your strengths."))
            st.markdown("### 🔧 Improvement Suggestions")
            st.warning(ats_data.get("suggestions", "Upload a resume and run analysis."))

        st.divider()
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("### 🛠️ Extracted Skills")
            render_skill_list(ats_data.get("extracted_skills", []), "#28a745")
        with col_s2:
            st.markdown("### ⚠️ Missing Skills")
            if ats_data.get("job_description") and ats_data.get("job_description").strip():
                render_skill_list(ats_data.get("missing_skills", []), "#dc3545")
            else:
                st.info("💡 Paste a job description under 'Run ATS Analysis' to view missing skills.")

    else:
        st.info("📄 Upload a resume and run ATS analysis to see your dashboard.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Upload Resume", use_container_width=True, type="primary"):
                st.session_state["page"] = "upload_resume"
                st.rerun()
        with col2:
            if st.button("🔍 Learn More", use_container_width=True):
                st.markdown("CareerPilot AI helps you optimize your resume for ATS systems.")
