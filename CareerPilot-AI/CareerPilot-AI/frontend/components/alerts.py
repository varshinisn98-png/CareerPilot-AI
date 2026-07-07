import streamlit as st


def gemini_key_alert():
    """Show a banner when Gemini API key is missing."""
    st.markdown(
        """
        <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
            border-radius:14px;padding:1rem 1.2rem;margin-bottom:1rem;">
            <div style="display:flex;align-items:flex-start;gap:10px;">
                <span style="font-size:1.3rem;">🔑</span>
                <div>
                    <p style="color:#fca5a5;font-weight:600;margin:0 0 4px 0;">Gemini API Key Required</p>
                    <p style="color:#94a3b8;font-size:0.88rem;margin:0 0 8px 0;">
                        This feature requires a Gemini API key. Get your free key at
                        <a href="https://aistudio.google.com/app/apikey" target="_blank"
                           style="color:#4f8bf9;">aistudio.google.com</a>
                        then add it to <code style="background:rgba(255,255,255,0.08);
                        padding:2px 6px;border-radius:4px;">backend/.env</code>
                    </p>
                    <code style="background:rgba(0,0,0,0.3);color:#86efac;padding:6px 10px;
                        border-radius:6px;font-size:0.82rem;display:block;">
                        GEMINI_API_KEY=your-actual-key-here
                    </code>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("After adding the key, restart the backend with `python -m uvicorn app.main:app --reload --port 8000`")
