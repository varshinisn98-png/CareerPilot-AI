import streamlit as st
import httpx

from utils.helpers import API_BASE


from utils.helpers import get_headers

_headers = get_headers


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("## 📝 Cover Letter Generator")
    st.markdown("Generate a personalized, professional cover letter using your resume and job description.")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        st.warning("Please upload a resume first.")
        if st.button("Go to Upload"):
            st.session_state["page"] = "upload_resume"
            st.rerun()
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Job Description")
        jd = st.text_area(
            "Paste the job description",
            height=300,
            placeholder="Paste the full job description here. The more detail, the better the cover letter.",
            key="cover_jd",
        )
        generate = st.button("✨ Generate Cover Letter", type="primary", use_container_width=True)

    with col2:
        st.markdown("### 📄 Generated Cover Letter")

        if generate:
            if not jd.strip():
                st.error("Please paste a job description.")
            else:
                with st.spinner("Crafting your cover letter with AI..."):
                    try:
                        res = httpx.post(
                            f"{API_BASE}/cover-letter/generate",
                            headers=_headers(),
                            json={"resume_id": resume_id, "job_description": jd},
                            timeout=30,
                        )
                        if res.status_code == 200:
                            content = res.json()["content"]
                            st.session_state["cover_letter"] = content
                            st.session_state["cover_edit"] = content  # Overwrite text area state to force update
                            st.session_state.pop("cover_letter_history", None) # clear history cache to force refetch
                            st.success("✅ Cover letter generated!")
                        else:
                            st.error(res.json().get("detail", "Generation failed."))
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend.")

        cover = st.session_state.get("cover_letter", "")
        if cover:
            edited = st.text_area(
                "Edit your cover letter",
                value=cover,
                height=350,
                key="cover_edit",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "⬇️ Download (.txt)",
                    data=edited,
                    file_name="cover_letter.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_b:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.pop("cover_letter", None)
                    st.session_state.pop("cover_edit", None)  # Reset widget state as well
                    st.rerun()
        else:
            st.info("Your cover letter will appear here after generation.")

    st.divider()
    # Cover letter history
    st.markdown("### 📂 Previous Cover Letters")
    if "cover_letter_history" not in st.session_state:
        try:
            res = httpx.get(f"{API_BASE}/cover-letter/history", headers=_headers(), timeout=10)
            if res.status_code == 200:
                st.session_state["cover_letter_history"] = res.json()
            else:
                st.session_state["cover_letter_history"] = []
        except Exception:
            st.session_state["cover_letter_history"] = []

    history = st.session_state.get("cover_letter_history", [])
    if history:
        for i, cl in enumerate(history[:5]):
            with st.expander(f"Cover Letter #{cl['id']} — {cl['created_at'][:10]}"):
                st.text(cl["content"])
    else:
        st.info("No previous cover letters.")
