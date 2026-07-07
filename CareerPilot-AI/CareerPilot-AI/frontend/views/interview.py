import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"

TYPES = {
    "🧑‍💼  HR / Behavioral": ("hr", "#4f8bf9",
        "Use the STAR method — Situation, Task, Action, Result. Be specific and concise."),
    "💻  Technical": ("technical", "#22c55e",
        "Think out loud. Explain your reasoning and discuss trade-offs."),
    "📂  Project-Based": ("project", "#f59e0b",
        "Walk through your problem-solving process and what you learned."),
}

SPEAKING_GUIDE = """
### 🎙️ How to Speak Well in Interviews

**Structure your answer:**
- **S** — Situation: Set the context briefly
- **T** — Task: What was your responsibility?
- **A** — Action: What did YOU specifically do?
- **R** — Result: What was the outcome? (use numbers if possible)

**Delivery tips:**
- 🕐 Keep answers to **1-2 minutes**
- 👁️ Maintain eye contact (look at camera for video)
- 🐢 Speak at a **moderate pace** — not too fast
- ⏸️ It's okay to **pause and think** before answering
- 💪 Use **confident, positive language**
- 🚫 Avoid filler words: "um", "like", "you know"
"""


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def _is_gemini_error(msg: str) -> bool:
    return any(k in msg.upper() for k in ["API KEY", "GEMINI", "API_KEY_INVALID", "QUOTA", "429"])


def _score_color(score: int) -> str:
    if score >= 8: return "#22c55e"
    if score >= 6: return "#f59e0b"
    return "#ef4444"


def _verdict_style(verdict: str):
    styles = {
        "Excellent": ("#22c55e", "🌟"),
        "Good": ("#4f8bf9", "👍"),
        "Needs Improvement": ("#f59e0b", "📈"),
        "Practice More": ("#ef4444", "🔄"),
    }
    return styles.get(verdict, ("#94a3b8", "📝"))


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, info_box, divider

    page_header("Interview Prep", "AI-generated questions + answer coaching tailored to your resume", "🎤")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        info_box("Please upload a resume first.", "⚠️", "#f59e0b")
        if st.button("📤 Upload Resume", type="primary"):
            st.session_state["page"] = "upload_resume"; st.rerun()
        return

    # Main tabs
    tab_gen, tab_guide = st.tabs(["🎯  Practice Questions", "📖  Speaking Guide"])

    with tab_guide:
        st.markdown(SPEAKING_GUIDE)
        st.markdown(
            """
            <div style="background:rgba(79,139,249,0.08);border:1px solid rgba(79,139,249,0.2);
                border-radius:14px;padding:1.2rem;margin-top:1rem;">
                <h4 style="color:#f1f5f9;margin:0 0 8px 0;">💡 STAR Method Example</h4>
                <p style="color:#94a3b8;font-size:0.9rem;line-height:1.8;margin:0;">
                <b style="color:#4f8bf9;">S:</b> "During my final year project..."<br>
                <b style="color:#4f8bf9;">T:</b> "I was responsible for building the backend API..."<br>
                <b style="color:#4f8bf9;">A:</b> "I designed the database schema, wrote REST endpoints using FastAPI..."<br>
                <b style="color:#4f8bf9;">R:</b> "The project scored 95/100 and processed 500+ requests in testing."
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_gen:
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
                with st.spinner("🤖 Generating questions with Gemini AI..."):
                    try:
                        res = httpx.post(f"{API_BASE}/interview/generate", headers=_headers(),
                                         json={"resume_id": resume_id, "question_type": q_key}, timeout=30)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["interview_qs"] = data.get("questions", [])
                            st.session_state["interview_type_key"] = q_key
                            st.session_state["interview_type_label"] = selected
                            st.session_state["interview_color"] = color
                            st.session_state.pop("eval_results", None)
                            st.success(f"✅ Generated {len(data.get('questions', []))} questions!")
                        else:
                            try: detail = res.json().get("detail", "")
                            except: detail = ""
                            if _is_gemini_error(detail):
                                st.error("🔑 Gemini API quota exceeded or key issue. Wait a minute and try again.")
                            else:
                                st.error(detail or "Failed.")
                    except httpx.ConnectError:
                        st.error("Cannot connect to backend.")

            questions = st.session_state.get("interview_qs", [])
            q_color = st.session_state.get("interview_color", "#4f8bf9")
            q_key_stored = st.session_state.get("interview_type_key", "hr")
            q_label = st.session_state.get("interview_type_label", selected)

            if questions:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">'
                    f'<span style="background:{q_color}20;color:{q_color};border:1px solid {q_color}40;'
                    f'border-radius:20px;padding:4px 14px;font-size:0.85rem;font-weight:600;">'
                    f'{q_label.strip()}</span>'
                    f'<span style="color:#64748b;font-size:0.85rem;">{len(questions)} questions</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if "eval_results" not in st.session_state:
                    st.session_state["eval_results"] = {}

                for i, q in enumerate(questions, 1):
                    with st.expander(f"**Q{i}.** {q[:85]}{'...' if len(q) > 85 else ''}"):

                        # Question display
                        st.markdown(
                            f'<div style="background:rgba(79,139,249,0.08);border-left:3px solid #4f8bf9;'
                            f'border-radius:0 10px 10px 0;padding:10px 14px;margin-bottom:12px;">'
                            f'<p style="color:#f1f5f9;font-size:0.95rem;margin:0;">{q}</p></div>',
                            unsafe_allow_html=True,
                        )

                        # Answer input
                        answer_key = f"ans_{i}"
                        answer = st.text_area(
                            "✍️ Your Practice Answer",
                            key=answer_key,
                            height=120,
                            placeholder="Type your answer here using the STAR method...\n\n"
                                        "Situation → Task → Action → Result",
                        )

                        col_btn1, col_btn2, _ = st.columns([1, 1, 2])
                        with col_btn1:
                            check = st.button("🔍 Check My Answer", key=f"check_{i}",
                                              use_container_width=True, type="primary")
                        with col_btn2:
                            if st.button("💡 Get Sample Answer", key=f"sample_{i}",
                                         use_container_width=True):
                                st.session_state[f"show_sample_{i}"] = True

                        # Evaluate answer
                        if check:
                            if not answer.strip():
                                st.warning("Please type your answer first.")
                            else:
                                with st.spinner("🤖 AI is evaluating your answer..."):
                                    try:
                                        res = httpx.post(
                                            f"{API_BASE}/interview/evaluate",
                                            headers=_headers(),
                                            json={
                                                "question": q,
                                                "user_answer": answer,
                                                "question_type": q_key_stored,
                                            },
                                            timeout=30,
                                        )
                                        if res.status_code == 200:
                                            st.session_state["eval_results"][str(i)] = res.json()
                                        else:
                                            try: detail = res.json().get("detail", "")
                                            except: detail = ""
                                            if _is_gemini_error(detail):
                                                st.error("Gemini quota exceeded. Wait a minute and try again.")
                                            else:
                                                st.error(detail or "Evaluation failed.")
                                    except httpx.ConnectError:
                                        st.error("Cannot connect to backend.")

                        # Show evaluation result
                        eval_data = st.session_state.get("eval_results", {}).get(str(i))
                        if eval_data:
                            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                            verdict = eval_data.get("verdict", "Needs Improvement")
                            v_color, v_icon = _verdict_style(verdict)

                            # Overall verdict banner
                            overall = eval_data.get("overall_score", 5)
                            st.markdown(
                                f"""
                                <div style="background:{v_color}15;border:1px solid {v_color}40;
                                    border-radius:14px;padding:1rem 1.2rem;margin-bottom:1rem;
                                    display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <span style="font-size:1.5rem;">{v_icon}</span>
                                        <span style="color:{v_color};font-size:1.1rem;font-weight:700;
                                            margin-left:8px;">{verdict}</span>
                                    </div>
                                    <div style="text-align:right;">
                                        <div style="color:{v_color};font-size:2rem;font-weight:700;
                                            line-height:1;">{overall}/10</div>
                                        <div style="color:#64748b;font-size:0.75rem;">Overall Score</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            # Score breakdown
                            sc1, sc2, sc3 = st.columns(3)
                            for col, label, key in [
                                (sc1, "📝 Content", "content_score"),
                                (sc2, "🏗️ Structure", "structure_score"),
                                (sc3, "💎 Clarity", "clarity_score"),
                            ]:
                                with col:
                                    s = eval_data.get(key, 5)
                                    c = _score_color(s)
                                    st.markdown(
                                        f'<div style="background:rgba(255,255,255,0.03);border:1px solid '
                                        f'rgba(255,255,255,0.08);border-radius:10px;padding:10px;'
                                        f'text-align:center;">'
                                        f'<div style="color:{c};font-size:1.5rem;font-weight:700;">{s}/10</div>'
                                        f'<div style="color:#64748b;font-size:0.78rem;">{label}</div></div>',
                                        unsafe_allow_html=True,
                                    )

                            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

                            # Strengths & improvements
                            fb1, fb2 = st.columns(2)
                            with fb1:
                                st.markdown(
                                    '<div style="background:rgba(34,197,94,0.06);border:1px solid '
                                    'rgba(34,197,94,0.2);border-radius:12px;padding:1rem;">',
                                    unsafe_allow_html=True,
                                )
                                st.markdown("##### ✅ What You Did Well")
                                for s in eval_data.get("strengths", []):
                                    st.markdown(
                                        f'<p style="color:#94a3b8;font-size:0.88rem;margin:4px 0;">'
                                        f'• {s}</p>', unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            with fb2:
                                st.markdown(
                                    '<div style="background:rgba(245,158,11,0.06);border:1px solid '
                                    'rgba(245,158,11,0.2);border-radius:12px;padding:1rem;">',
                                    unsafe_allow_html=True,
                                )
                                st.markdown("##### 📈 How to Improve")
                                for imp in eval_data.get("improvements", []):
                                    st.markdown(
                                        f'<p style="color:#94a3b8;font-size:0.88rem;margin:4px 0;">'
                                        f'• {imp}</p>', unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            # Speaking tips
                            tips = eval_data.get("speaking_tips", [])
                            if tips:
                                st.markdown(
                                    '<div style="background:rgba(79,139,249,0.06);border:1px solid '
                                    'rgba(79,139,249,0.2);border-radius:12px;padding:1rem;margin-top:0.8rem;">',
                                    unsafe_allow_html=True,
                                )
                                st.markdown("##### 🎙️ Speaking & Delivery Tips")
                                for t in tips:
                                    st.markdown(
                                        f'<p style="color:#94a3b8;font-size:0.88rem;margin:4px 0;">'
                                        f'🔹 {t}</p>', unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            # Ideal structure
                            structure = eval_data.get("ideal_answer_structure", "")
                            if structure:
                                st.markdown(
                                    f'<div style="background:rgba(124,58,237,0.06);border:1px solid '
                                    f'rgba(124,58,237,0.2);border-radius:12px;padding:1rem;margin-top:0.8rem;">'
                                    f'<p style="color:#a78bfa;font-weight:600;margin:0 0 6px 0;">'
                                    f'🏗️ Ideal Answer Structure</p>'
                                    f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;margin:0;">'
                                    f'{structure}</p></div>',
                                    unsafe_allow_html=True,
                                )

                            # Sample better answer
                            sample = eval_data.get("sample_better_answer", "")
                            if sample or st.session_state.get(f"show_sample_{i}"):
                                st.markdown(
                                    f'<div style="background:rgba(34,197,94,0.06);border:1px solid '
                                    f'rgba(34,197,94,0.2);border-radius:12px;padding:1rem;margin-top:0.8rem;">'
                                    f'<p style="color:#22c55e;font-weight:600;margin:0 0 6px 0;">'
                                    f'💡 Sample Stronger Answer</p>'
                                    f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;margin:0;">'
                                    f'{sample}</p></div>',
                                    unsafe_allow_html=True,
                                )

                divider()
                dl_text = "\n\n".join(f"Q{i+1}: {q}" for i, q in enumerate(questions))
                st.download_button("⬇️ Download Questions as .txt", data=dl_text,
                                   file_name=f"interview_{q_key_stored}_questions.txt",
                                   mime="text/plain", use_container_width=True)
            else:
                st.markdown(
                    '<div style="text-align:center;padding:3rem;color:#475569;">'
                    '<div style="font-size:3rem;margin-bottom:1rem;">🎤</div>'
                    '<p>Select a question type and click Generate to get started</p></div>',
                    unsafe_allow_html=True,
                )
