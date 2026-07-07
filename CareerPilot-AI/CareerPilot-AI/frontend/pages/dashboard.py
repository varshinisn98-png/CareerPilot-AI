import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    from components.ui import page_header, stat_card, ats_score_ring, skill_chips, divider, info_box, progress_bar

    user = st.session_state.get("user", {})
    resume_id = st.session_state.get("current_resume_id")

    page_header("Dashboard", f"Welcome back, {user.get('full_name', 'User')}! 👋", "🏠")

    # Fetch ATS data
    ats = None
    if resume_id:
        try:
            r = httpx.get(f"{API_BASE}/ats/result/{resume_id}", headers=_headers(), timeout=10)
            if r.status_code == 200:
                ats = r.json()
        except Exception:
            pass

    if not ats:
        # Empty state
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,rgba(79,139,249,0.1),rgba(124,58,237,0.1));
                border:1px solid rgba(79,139,249,0.2);border-radius:20px;padding:3rem;text-align:center;">
                <div style="font-size:4rem;margin-bottom:1rem;">📄</div>
                <h2 style="color:#f1f5f9;font-size:1.5rem;font-weight:600;margin:0 0 0.5rem 0;">
                    Upload Your Resume to Get Started</h2>
                <p style="color:#64748b;font-size:0.95rem;margin:0 0 1.5rem 0;">
                    Get your ATS score, skill analysis, and AI-powered career insights</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("📤 Upload Resume", use_container_width=True, type="primary"):
                st.session_state["page"] = "upload_resume"
                st.rerun()
        with col2:
            if st.button("🎤 Interview Prep", use_container_width=True):
                st.session_state["page"] = "interview"
                st.rerun()
        with col3:
            if st.button("📝 Cover Letter", use_container_width=True):
                st.session_state["page"] = "cover_letter"
                st.rerun()

        divider()
        st.markdown("### ✨ What CareerPilot AI Can Do")
        features = [
            ("🎯", "ATS Score", "Get a detailed ATS compatibility score for any job"),
            ("🛠️", "Skill Analysis", "Extract skills and find gaps vs job requirements"),
            ("💬", "Resume Chat", "Ask AI anything about your resume using RAG"),
            ("🎤", "Interview Prep", "Get tailored HR, Technical & Project questions"),
            ("📝", "Cover Letter", "Generate personalized cover letters in seconds"),
            ("💼", "JD Matching", "See how well your resume matches any job posting"),
        ]
        cols = st.columns(3)
        for i, (icon, title, desc) in enumerate(features):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                        border-radius:14px;padding:1.2rem;margin-bottom:0.8rem;height:120px;">
                        <div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>
                        <div style="color:#f1f5f9;font-weight:600;font-size:0.9rem;">{title}</div>
                        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        return

    # ── Dashboard with data ────────────────────────────────────────────────────
    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("ATS Score", f"{ats['ats_score']:.0f}/100", "🎯", "#4f8bf9")
    with c2:
        stat_card("JD Match", f"{ats.get('jd_match_percent', 0):.0f}%", "💼", "#22c55e")
    with c3:
        stat_card("Skills Found", len(ats.get("extracted_skills", [])), "🛠️", "#f59e0b")
    with c4:
        stat_card("Gaps Found", len(ats.get("missing_skills", [])), "⚠️", "#ef4444")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 🎯 ATS Score")
        ats_score_ring(ats["ats_score"])
        if ats.get("jd_match_percent"):
            progress_bar("JD Match", ats["jd_match_percent"], "#22c55e")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        # Strengths
        st.markdown(
            '<div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.2);'
            'border-radius:16px;padding:1.2rem;margin-bottom:0.8rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💪 Strengths")
        st.markdown(
            f'<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;margin:0;">'
            f'{ats.get("strengths", "Run ATS analysis to see strengths.")}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Suggestions
        st.markdown(
            '<div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.2);'
            'border-radius:16px;padding:1.2rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💡 AI Suggestions")
        st.markdown(
            f'<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;margin:0;">'
            f'{ats.get("suggestions", "—")}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    divider()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.2rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### ✅ Extracted Skills")
        skill_chips(ats.get("extracted_skills", []), "#22c55e")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s2:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.2rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### ❌ Missing Skills")
        skill_chips(ats.get("missing_skills", []), "#ef4444")
        st.markdown("</div>", unsafe_allow_html=True)

    divider()

    # Quick actions
    st.markdown("##### ⚡ Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("🔍 Re-analyze", use_container_width=True):
            st.session_state["page"] = "ats"
            st.rerun()
    with q2:
        if st.button("💬 Chat with Resume", use_container_width=True):
            st.session_state["page"] = "resume_chat"
            st.rerun()
    with q3:
        if st.button("🎤 Practice Interview", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()
    with q4:
        if st.button("📝 Generate Cover Letter", use_container_width=True):
            st.session_state["page"] = "cover_letter"
            st.rerun()
