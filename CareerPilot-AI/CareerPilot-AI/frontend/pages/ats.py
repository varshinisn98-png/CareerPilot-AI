import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


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

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💼 Job Description *(optional)*")
        st.markdown('<p style="color:#64748b;font-size:0.85rem;">Paste a JD for targeted analysis and JD match score</p>',
                    unsafe_allow_html=True)
        jd = st.text_area("", height=220, placeholder="Paste job description here for JD-based scoring...",
                          label_visibility="collapsed", key="ats_jd")
        analyze = st.button("🔍  Run ATS Analysis", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 📊 Previous Result")
        try:
            prev = httpx.get(f"{API_BASE}/ats/result/{resume_id}", headers=_headers(), timeout=10)
            if prev.status_code == 200:
                d = prev.json()
                ats_score_ring(d["ats_score"])
                if d.get("jd_match_percent"):
                    progress_bar("JD Match", d["jd_match_percent"], "#22c55e")
            else:
                st.markdown('<p style="color:#475569;text-align:center;padding:2rem;">No analysis yet</p>',
                            unsafe_allow_html=True)
        except Exception:
            st.markdown('<p style="color:#475569;text-align:center;">Run analysis to see results</p>',
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
                    data = res.json()
                    st.session_state["ats_result"] = data
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    try: msg = res.json().get("detail", "Analysis failed.")
                    except: msg = f"Error {res.status_code}"
                    st.error(msg)
            except httpx.ConnectError:
                st.error("Cannot connect to backend.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Show results
    result = st.session_state.get("ats_result")
    if not result:
        try:
            prev = httpx.get(f"{API_BASE}/ats/result/{resume_id}", headers=_headers(), timeout=10)
            if prev.status_code == 200:
                result = prev.json()
        except Exception:
            pass

    if result:
        divider()
        st.markdown("### 📋 Full Analysis Report")

        c1, c2, c3, c4 = st.columns(4)
        with c1: stat_card("ATS Score", f"{result['ats_score']:.0f}", "🎯", "#4f8bf9")
        with c2: stat_card("JD Match", f"{result.get('jd_match_percent',0):.0f}%", "💼", "#22c55e")
        with c3: stat_card("Skills", len(result.get("extracted_skills", [])), "🛠️", "#f59e0b")
        with c4: stat_card("Gaps", len(result.get("missing_skills", [])), "⚠️", "#ef4444")

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        t1, t2, t3 = st.columns([1, 1, 1])

        with t1:
            st.markdown(
                '<div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.2);'
                'border-radius:14px;padding:1.2rem;height:200px;overflow-y:auto;">',
                unsafe_allow_html=True,
            )
            st.markdown("##### 💪 Strengths")
            st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">'
                        f'{result.get("strengths","—")}</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with t2:
            st.markdown(
                '<div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);'
                'border-radius:14px;padding:1.2rem;height:200px;overflow-y:auto;">',
                unsafe_allow_html=True,
            )
            st.markdown("##### ⚠️ Weaknesses")
            st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">'
                        f'{result.get("weaknesses","—")}</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with t3:
            st.markdown(
                '<div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.2);'
                'border-radius:14px;padding:1.2rem;height:200px;overflow-y:auto;">',
                unsafe_allow_html=True,
            )
            st.markdown("##### 💡 Suggestions")
            st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;">'
                        f'{result.get("suggestions","—")}</p>', unsafe_allow_html=True)
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
