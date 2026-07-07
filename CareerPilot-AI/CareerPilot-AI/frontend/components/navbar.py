import streamlit as st


def render_navbar():
    st.markdown(
        """
        <div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.8rem 1rem;background:rgba(13,17,23,0.8);
            border-bottom:1px solid rgba(79,139,249,0.15);
            backdrop-filter:blur(10px);margin-bottom:0.5rem;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:1.6rem;">🚀</span>
                <div>
                    <span style="background:linear-gradient(135deg,#4f8bf9,#a78bfa);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        font-size:1.3rem;font-weight:700;">CareerPilot</span>
                    <span style="color:#4f8bf9;font-size:1.3rem;font-weight:700;"> AI</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
