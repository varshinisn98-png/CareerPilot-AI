import streamlit as st
import httpx

from utils.helpers import API_BASE


from utils.helpers import get_headers

_headers = get_headers


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("## 📄 Resume Upload & ATS Analysis")

    tab1, tab2 = st.tabs(["📤 Upload Resume", "📊 Run ATS Analysis"])

    # ── Tab 1: Upload ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("Upload your resume (PDF only, max 10 MB).")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

        if uploaded_file and st.button("Upload Resume", type="primary"):
            with st.spinner("Uploading and parsing your resume..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    res = httpx.post(
                        f"{API_BASE}/resume/upload",
                        headers=_headers(),
                        files=files,
                        timeout=30,
                    )
                    if res.status_code == 201:
                        data = res.json()
                        st.success(f"✅ Resume '{data['filename']}' uploaded successfully!")
                        st.session_state["current_resume_id"] = data["id"]

                        # Refresh resume list
                        r = httpx.get(f"{API_BASE}/resume/history", headers=_headers(), timeout=10)
                        if r.status_code == 200:
                            st.session_state["resumes"] = r.json()
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Upload failed."))
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")

        st.divider()
        st.markdown("### 📂 Resume History")
        resumes = st.session_state.get("resumes", [])
        if resumes:
            for r in resumes:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {r['filename']}")
                with col2:
                    if st.button("Select", key=f"sel_{r['id']}"):
                        st.session_state["current_resume_id"] = r["id"]
                        st.success(f"Active resume: {r['filename']}")
                with col3:
                    if st.button("Delete", key=f"del_{r['id']}"):
                        with st.spinner("Deleting resume..."):
                            del_res = httpx.delete(
                                f"{API_BASE}/resume/{r['id']}", headers=_headers(), timeout=10
                            )
                            if del_res.status_code == 204:
                                st.success("Resume deleted.")
                                if st.session_state.get("current_resume_id") == r["id"]:
                                    st.session_state["current_resume_id"] = None
                                r2 = httpx.get(f"{API_BASE}/resume/history", headers=_headers(), timeout=10)
                                if r2.status_code == 200:
                                    st.session_state["resumes"] = r2.json()
                                st.rerun()
                            else:
                                try:
                                    detail = del_res.json().get("detail", "Failed to delete resume.")
                                except Exception:
                                    detail = "Failed to delete resume."
                                st.error(detail)
        else:
            st.info("No resumes uploaded yet.")

    # ── Tab 2: ATS Analysis ───────────────────────────────────────────────────
    with tab2:
        resume_id = st.session_state.get("current_resume_id")
        if not resume_id:
            st.warning("Please upload or select a resume first.")
            return

        st.markdown("Optionally paste a job description for JD-based ATS scoring.")
        jd = st.text_area("Job Description (optional)", height=200,
                          placeholder="Paste the job description here...")

        if st.button("🔍 Run ATS Analysis", type="primary"):
            with st.spinner("Analyzing your resume with AI..."):
                try:
                    payload = {"resume_id": resume_id}
                    if jd.strip():
                        payload["job_description"] = jd

                    res = httpx.post(
                        f"{API_BASE}/ats/analyze",
                        headers=_headers(),
                        json=payload,
                        timeout=60,
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ Analysis complete!")

                        from components.cards import ats_gauge, render_skill_list, metric_card
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            ats_gauge(data["ats_score"])
                        with col2:
                            if data.get("jd_match_percent"):
                                st.metric("JD Match", f"{data['jd_match_percent']:.1f}%")
                            st.markdown("**Strengths:**")
                            st.success(data.get("strengths", "—"))
                            st.markdown("**Weaknesses:**")
                            st.error(data.get("weaknesses", "—"))
                            st.markdown("**Suggestions:**")
                            st.warning(data.get("suggestions", "—"))

                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            st.markdown("### ✅ Extracted Skills")
                            render_skill_list(data.get("extracted_skills", []), "#28a745")
                        with col_s2:
                            st.markdown("### ❌ Missing Skills")
                            render_skill_list(data.get("missing_skills", []), "#dc3545")
                    else:
                        st.error(res.json().get("detail", "Analysis failed."))
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")
