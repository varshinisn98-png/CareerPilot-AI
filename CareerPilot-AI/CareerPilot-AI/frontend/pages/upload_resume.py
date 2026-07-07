import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, divider, info_box

    page_header("Resume Manager", "Upload, manage and download your resumes", "📄")

    tab1, tab2 = st.tabs(["📤  Upload New Resume", "📂  My Resumes"])

    with tab1:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        info_box("Upload your resume as a PDF. We'll parse it, extract skills, and build an AI index for chat.", "💡")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            st.markdown(
                f"""
                <div style="background:rgba(79,139,249,0.08);border:1px solid rgba(79,139,249,0.2);
                    border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
                    <span style="font-size:1.5rem;">📄</span>
                    <div>
                        <div style="color:#f1f5f9;font-weight:600;">{uploaded.name}</div>
                        <div style="color:#64748b;font-size:0.8rem;">{len(uploaded.getvalue())/1024:.1f} KB</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            if st.button("⬆️  Upload Resume", type="primary", use_container_width=True):
                with st.spinner("Uploading and parsing your resume..."):
                    try:
                        files = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
                        res = httpx.post(f"{API_BASE}/resume/upload",
                                         headers=_headers(), files=files, timeout=30)
                        if res.status_code == 201:
                            data = res.json()
                            st.success(f"✅ **{data['filename']}** uploaded successfully!")
                            st.session_state["current_resume_id"] = data["id"]
                            r = httpx.get(f"{API_BASE}/resume/history", headers=_headers(), timeout=10)
                            if r.status_code == 200:
                                st.session_state["resumes"] = r.json()
                            st.balloons()
                            import time; time.sleep(1)
                            st.rerun()
                        else:
                            try: msg = res.json().get("detail", "Upload failed.")
                            except: msg = f"Error {res.status_code}"
                            st.error(msg)
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend.")

    with tab2:
        resumes = st.session_state.get("resumes", [])
        if not resumes:
            st.markdown(
                """
                <div style="text-align:center;padding:3rem;color:#475569;">
                    <div style="font-size:3rem;margin-bottom:1rem;">📭</div>
                    <p>No resumes uploaded yet. Upload your first resume above!</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for r in resumes:
                is_active = st.session_state.get("current_resume_id") == r["id"]
                border = "rgba(79,139,249,0.4)" if is_active else "rgba(255,255,255,0.08)"
                bg = "rgba(79,139,249,0.06)" if is_active else "rgba(255,255,255,0.02)"

                st.markdown(
                    f"""
                    <div style="background:{bg};border:1px solid {border};border-radius:14px;
                        padding:1rem 1.2rem;margin-bottom:0.6rem;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:1.5rem;">📄</span>
                            <div style="flex:1;">
                                <div style="color:#f1f5f9;font-weight:600;">{r['filename']}</div>
                                <div style="color:#475569;font-size:0.8rem;">
                                    Uploaded: {r['uploaded_at'][:10]}
                                    {'  ✅ Active' if is_active else ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col2:
                    if st.button("✅ Set Active", key=f"sel_{r['id']}", use_container_width=True):
                        st.session_state["current_resume_id"] = r["id"]
                        st.rerun()
                with col3:
                    dl = httpx.get(f"{API_BASE}/resume/{r['id']}/download",
                                   headers=_headers(), timeout=10)
                    if dl.status_code == 200:
                        st.download_button("⬇️ Download", data=dl.content,
                                           file_name=r["filename"], mime="application/pdf",
                                           key=f"dl_{r['id']}", use_container_width=True)
                with col4:
                    if st.button("🗑️ Delete", key=f"del_{r['id']}", use_container_width=True):
                        d = httpx.delete(f"{API_BASE}/resume/{r['id']}",
                                         headers=_headers(), timeout=10)
                        if d.status_code == 204:
                            st.success("Deleted.")
                            rr = httpx.get(f"{API_BASE}/resume/history",
                                           headers=_headers(), timeout=10)
                            if rr.status_code == 200:
                                st.session_state["resumes"] = rr.json()
                            if st.session_state.get("current_resume_id") == r["id"]:
                                st.session_state.pop("current_resume_id", None)
                            st.rerun()

                divider()
