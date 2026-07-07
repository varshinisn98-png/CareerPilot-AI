import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def _is_gemini_error(msg: str) -> bool:
    return any(k in msg.upper() for k in ["API KEY", "GEMINI", "API_KEY_INVALID", "APIKEY"])


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, info_box, divider

    page_header("Cover Letter Generator", "AI-crafted cover letters personalized to you and the role", "📝")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        info_box("Please upload a resume first.", "⚠️", "#f59e0b")
        if st.button("📤 Upload Resume", type="primary"):
            st.session_state["page"] = "upload_resume"; st.rerun()
        return

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 📋 Job Description")
        st.markdown('<p style="color:#64748b;font-size:0.85rem;margin-bottom:8px;">'
                    'Paste the job description for a personalized letter</p>', unsafe_allow_html=True)
        jd = st.text_area("", height=280,
                           placeholder="Paste the full job description here...",
                           label_visibility="collapsed", key="cl_jd")
        generate = st.button("✨  Generate Cover Letter", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### 📄 Generated Cover Letter")

        if generate:
            if not jd.strip():
                st.error("Please paste a job description.")
            else:
                with st.spinner("✍️ Crafting your cover letter..."):
                    try:
                        res = httpx.post(f"{API_BASE}/cover-letter/generate", headers=_headers(),
                                         json={"resume_id": resume_id, "job_description": jd}, timeout=30)
                        if res.status_code == 200:
                            st.session_state["cover_letter"] = res.json()["content"]
                            st.success("✅ Cover letter generated!")
                        else:
                            try: detail = res.json().get("detail", "")
                            except: detail = ""
                            if _is_gemini_error(detail):
                                st.error("🔑 **Gemini API key required.** Add `GEMINI_API_KEY=your-key` to `backend/.env` and restart the backend. Get free key: https://aistudio.google.com/app/apikey")
                            else:
                                st.error(detail or "Generation failed.")
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend.")
                    except Exception as e:
                        st.error(f"Error: {e}")

        cl = st.session_state.get("cover_letter", "")
        if cl:
            edited = st.text_area("Edit your cover letter:", value=cl, height=280, key="cl_edit")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Download .txt", data=edited,
                                   file_name="cover_letter.txt", mime="text/plain",
                                   use_container_width=True)
            with c2:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.pop("cover_letter", None); st.rerun()
        else:
            st.markdown(
                '<div style="text-align:center;padding:3rem;color:#475569;">'
                '<div style="font-size:3rem;margin-bottom:1rem;">📝</div>'
                '<p>Your cover letter will appear here</p></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    divider()
    st.markdown("##### 📂 Previous Cover Letters")
    try:
        res = httpx.get(f"{API_BASE}/cover-letter/history", headers=_headers(), timeout=10)
        if res.status_code == 200:
            history = res.json()
            if history:
                for cl in history[:5]:
                    with st.expander(f"📄 Cover Letter — {cl['created_at'][:10]}"):
                        st.text_area("", value=cl["content"], height=200,
                                     key=f"hist_{cl['id']}", disabled=True,
                                     label_visibility="collapsed")
                        st.download_button("⬇️ Download", data=cl["content"],
                                           file_name=f"cover_letter_{cl['id']}.txt",
                                           key=f"dl_{cl['id']}")
            else:
                st.markdown('<p style="color:#475569;">No previous cover letters yet.</p>',
                            unsafe_allow_html=True)
    except Exception:
        pass
