import streamlit as st
import httpx

from utils.helpers import API_BASE


from utils.helpers import get_headers

_headers = get_headers


def _is_gemini_error(msg: str) -> bool:
    return any(k in msg.upper() for k in ["API KEY", "GEMINI", "API_KEY_INVALID", "APIKEY"])


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, ats_score_ring, skill_chips, divider, info_box, progress_bar, stat_card

    page_header("ATS Analysis", "Check your resume's ATS compatibility and get AI-powered feedback", "🎯")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        info_box("Please upload a resume first to run ATS analysis.", "⚠️", "#f59e0b")
        if st.button("📤 Upload Resume", type="primary"):
            st.session_state["page"] = "upload_resume"; st.rerun()
        return

    # Load ATS result cache once per resume
    if f"ats_cache_{resume_id}" not in st.session_state:
        try:
            res = httpx.get(f"{API_BASE}/ats/result/{resume_id}", headers=_headers(), timeout=10)
            if res.status_code == 200:
                st.session_state[f"ats_cache_{resume_id}"] = res.json()
            else:
                st.session_state[f"ats_cache_{resume_id}"] = None
        except Exception:
            st.session_state[f"ats_cache_{resume_id}"] = None

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💼 Job Description *(optional)*")
        st.markdown('<p style="color:#64748b;font-size:0.85rem;">Paste a JD for targeted JD-match scoring</p>',
                    unsafe_allow_html=True)
        jd = st.text_area("", height=220, placeholder="Paste job description here...",
                          label_visibility="collapsed", key="ats_jd")
        analyze = st.button("🔍  Run ATS Analysis", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 📊 Score")
        d = st.session_state.get(f"ats_cache_{resume_id}")
        if d:
            ats_score_ring(d["ats_score"])
            if d.get("jd_match_percent"):
                progress_bar("JD Match", d["jd_match_percent"], "#22c55e")
        else:
            st.markdown('<p style="color:#475569;text-align:center;padding:2rem;">No analysis yet — run one!</p>',
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze:
        with st.spinner("🤖 Analyzing with AI... this may take 10-30 seconds..."):
            try:
                payload = {"resume_id": resume_id}
                if jd.strip():
                    payload["job_description"] = jd
                res = httpx.post(f"{API_BASE}/ats/analyze", headers=_headers(),
                                 json=payload, timeout=60)
                if res.status_code == 200:
                    st.session_state[f"ats_cache_{resume_id}"] = res.json()
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    try: detail = res.json().get("detail", "")
                    except: detail = ""
                    if _is_gemini_error(detail):
                        st.warning("⚠️ AI enrichment unavailable (no Gemini key). Showing local ATS score only.")
                    else:
                        st.error(detail or "Analysis failed.")
            except httpx.ConnectError:
                st.error("Cannot connect to backend.")
            except Exception as e:
                st.error(f"Error: {e}")

    result = st.session_state.get(f"ats_cache_{resume_id}")

    if result:
        divider()
        st.markdown("### 📋 Full Analysis Report")

        c1, c2, c3, c4 = st.columns(4)
        with c1: stat_card("ATS Score", f"{result['ats_score']:.0f}", "🎯", "#4f8bf9")
        with c2: stat_card("JD Match", f"{result.get('jd_match_percent',0):.0f}%", "💼", "#22c55e")
        with c3: stat_card("Skills Found", len(result.get("extracted_skills", [])), "🛠️", "#f59e0b")
        with c4: stat_card("Skill Gaps", len(result.get("missing_skills", [])), "⚠️", "#ef4444")

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        t1, t2, t3 = st.columns(3)
        for col, label, content, color in [
            (t1, "💪 Strengths", result.get("strengths", "—"), "34,197,94"),
            (t2, "⚠️ Weaknesses", result.get("weaknesses", "—"), "239,68,68"),
            (t3, "💡 Suggestions", result.get("suggestions", "—"), "245,158,11"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:rgba({color},0.05);border:1px solid rgba({color},0.2);'
                    f'border-radius:14px;padding:1.2rem;min-height:180px;">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"##### {label}")
                st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">{content}</p>',
                            unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
                'border-radius:14px;padding:1.2rem;">',
                unsafe_allow_html=True,
            )
            st.markdown("##### ✅ Skills Found")
            skill_chips(result.get("extracted_skills", []), "#22c55e")
            st.markdown("</div>", unsafe_allow_html=True)

        with sc2:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
                'border-radius:14px;padding:1.2rem;">',
                unsafe_allow_html=True,
            )
            st.markdown("##### ❌ Missing Skills")
            skill_chips(result.get("missing_skills", []), "#ef4444")
            st.markdown("</div>", unsafe_allow_html=True)
