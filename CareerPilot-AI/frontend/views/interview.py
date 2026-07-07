import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"

QUESTION_TYPES = {
    "🧑‍💼 HR / Behavioral": "hr",
    "💻 Technical": "technical",
    "📂 Project-Based": "project",
}

TIPS = {
    "hr": "Use the STAR method (Situation, Task, Action, Result) for behavioral questions.",
    "technical": "Think out loud, explain your reasoning, and discuss trade-offs.",
    "project": "Walk through your problem-solving process and what you learned.",
}


from utils.helpers import get_headers

_headers = get_headers


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("## 🎤 Interview Preparation")
    st.markdown("Generate AI-powered interview questions tailored to your resume.")

    resume_id = st.session_state.get("current_resume_id")
    if not resume_id:
        st.warning("Please upload a resume first.")
        if st.button("Go to Upload"):
            st.session_state["page"] = "upload_resume"
            st.rerun()
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_label = st.radio("Question Type", list(QUESTION_TYPES.keys()))
        question_type = QUESTION_TYPES[selected_label]
        num_questions = st.slider("Number of Questions", 5, 20, 10)

        generate_clicked = st.button("🎯 Generate Questions", type="primary", use_container_width=True)

    with col2:
        st.markdown(f"**💡 Tip:** {TIPS[question_type]}")
        st.divider()

        if generate_clicked:
            with st.spinner("Generating questions with AI..."):
                try:
                    res = httpx.post(
                        f"{API_BASE}/interview/generate",
                        headers=_headers(),
                        json={
                            "resume_id": resume_id,
                            "question_type": question_type,
                            "num_questions": num_questions
                        },
                        timeout=30,
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["interview_questions"] = data.get("questions", [])
                        st.session_state["interview_type"] = data.get("question_type", question_type)
                        st.success(f"✅ Generated {len(data.get('questions', []))} questions!")
                    else:
                        st.error(res.json().get("detail", "Failed to generate questions."))
                except httpx.ConnectError:
                    st.error("Cannot connect to backend.")

        # Display questions
        questions = st.session_state.get("interview_questions", [])
        if questions:
            q_type = st.session_state.get("interview_type", question_type)
            st.markdown(f"### {selected_label} Questions")

            for i, q in enumerate(questions, 1):
                with st.expander(f"Q{i}: {q[:80]}{'...' if len(q) > 80 else ''}"):
                    st.write(q)
                    user_ans = st.text_area(
                        "Your Answer (practice)",
                        key=f"answer_{i}",
                        height=100,
                        placeholder="Type your answer here for practice...",
                    )

                    eval_btn = st.button("🎯 Evaluate Answer", key=f"eval_btn_{i}", use_container_width=True)
                    
                    if eval_btn:
                        if not user_ans.strip():
                            st.error("Please type an answer before requesting evaluation.")
                        else:
                            with st.spinner("Analyzing answer with AI..."):
                                try:
                                    eval_res = httpx.post(
                                        f"{API_BASE}/interview/evaluate",
                                        headers=_headers(),
                                        json={
                                            "question": q,
                                            "user_answer": user_ans,
                                            "question_type": q_type
                                        },
                                        timeout=30
                                    )
                                    if eval_res.status_code == 200:
                                        st.session_state[f"eval_result_{i}"] = eval_res.json()
                                        st.success("✅ Analysis complete!")
                                    else:
                                        st.error(eval_res.json().get("detail", "Evaluation failed."))
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    # Render evaluation feedback if present
                    feedback = st.session_state.get(f"eval_result_{i}")
                    if feedback:
                        st.markdown("---")
                        st.markdown("##### 📊 AI Coach Feedback")
                        
                        score = feedback.get("score", 0)
                        if score >= 80:
                            score_color = "#22c55e"
                        elif score >= 60:
                            score_color = "#eab308"
                        else:
                            score_color = "#ef4444"
                            
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <div style="font-size: 1.8rem; font-weight: 800; color: {score_color};">{score}/100</div>
                                <div style="color: #64748b; font-size: 0.85rem; font-weight: 500; text-transform: uppercase;">Overall Score</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        st.markdown(f"**💪 Strengths:** {feedback.get('strengths', '')}")
                        st.markdown(f"**⚠️ Areas for Improvement:** {feedback.get('weaknesses', '')}")
                        
                        suggestions = feedback.get("suggestions", [])
                        if suggestions:
                            st.markdown("**💡 Key Tips:**")
                            for sug in suggestions:
                                st.markdown(f"- {sug}")
                                
                        improved = feedback.get("improved_answer", "")
                        if improved:
                            st.markdown("**✨ Recommended Response:**")
                            st.info(improved)


            # Download questions
            questions_text = "\n\n".join(f"Q{i+1}: {q}" for i, q in enumerate(questions))
            st.download_button(
                "⬇️ Download Questions",
                data=questions_text,
                file_name=f"interview_questions_{q_type}.txt",
                mime="text/plain",
                use_container_width=True,
            )
