import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"

TYPES = {
    "🧑‍💼 HR / Behavioral": ("hr", "#4f8bf9",
        "Use the STAR method — Situation, Task, Action, Result. Be specific and concise."),
    "💻 Technical": ("technical", "#22c55e",
        "Think out loud. Explain your reasoning and discuss trade-offs."),
    "📂 Project-Based": ("project", "#f59e0b",
        "Walk through your problem-solving process and what you learned."),
}


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, info_box, divider

    page_header("Interview Prep", "AI-generated questions tailored to your resume and experience", "🎤")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        info_box("Please upload a resume first.", "⚠️", "#f59e0b")
        if st.button("📤 Upload Resume", type="primary"):
            st.session_state["page"] = "upload_resume"; st.rerun()
        return

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### ⚙️ Settings")
        selected = st.radio("Question Type", list(TYPES.keys()), label_visibility="collapsed")
        q_key, color, tip = TYPES[selected]

        num = st.slider("Number of Questions", 5, 20, 10)

        st.markdown(
            f'<div style="background:{color}10;border:1px solid {color}30;border-radius:10px;'
            f'padding:10px 12px;margin-top:0.8rem;">'
            f'<p style="color:#94a3b8;font-size:0.82rem;margin:0;line-height:1.6;">💡 {tip}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        generate = st.button("🎯  Generate Questions", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        if generate:
            with st.spinner("🤖 Generating questions..."):
                try:
                    res = httpx.post(f"{API_BASE}/interview/generate", headers=_headers(),
                                     json={"resume_id": resume_id, "question_type": q_key}, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["interview_qs"] = data.get("questions", [])
                        st.session_state["interview_type"] = selected
                        st.session_state["interview_color"] = color
                        st.success(f"✅ Generated {len(data.get('questions',[]))} questions!")
                    else:
                        try: msg = res.json().get("detail", "Failed.")
                        except: msg = f"Error {res.status_code}"
                        st.error(msg)
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")
                except Exception as e:
                    st.error(f"Error: {e}")

        questions = st.session_state.get("interview_qs", [])
        q_color = st.session_state.get("interview_color", "#4f8bf9")
        q_type_label = st.session_state.get("interview_type", selected)

        if questions:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">'
                f'<span style="background:{q_color}20;color:{q_color};border:1px solid {q_color}40;'
                f'border-radius:20px;padding:4px 14px;font-size:0.85rem;font-weight:600;">'
                f'{q_type_label}</span>'
                f'<span style="color:#64748b;font-size:0.85rem;">{len(questions)} questions</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            for i, q in enumerate(questions, 1):
                with st.expander(f"**Q{i}.** {q[:90]}{'...' if len(q) > 90 else ''}"):
                    st.markdown(f'<p style="color:#f1f5f9;font-size:0.95rem;">{q}</p>',
                                unsafe_allow_html=True)
                    st.text_area("📝 Your Answer (practice here)",
                                 key=f"ans_{i}", height=100,
                                 placeholder="Type your practice answer...")

            divider()
            dl_text = "\n\n".join(f"Q{i+1}: {q}" for i, q in enumerate(questions))
            st.download_button(
                "⬇️ Download Questions as .txt",
                data=dl_text,
                file_name=f"interview_{q_key}_questions.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.markdown(
                """
                <div style="text-align:center;padding:3rem;color:#475569;">
                    <div style="font-size:3rem;margin-bottom:1rem;">🎤</div>
                    <p>Select a question type and click Generate to get started</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
