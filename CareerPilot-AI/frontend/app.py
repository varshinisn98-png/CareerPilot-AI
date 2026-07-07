import streamlit as st

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

token = st.session_state.get("token")
page = st.session_state.get("page", "login")

if not token and page not in ("login", "register"):
    page = "login"
    st.session_state["page"] = "login"

if token:
    from components.sidebar import render_sidebar
    render_sidebar()

if page == "login":
    from views.login import show; show()
elif page == "register":
    from views.register import show; show()
elif page == "dashboard":
    from views.dashboard import show; show()
elif page == "upload_resume":
    from views.upload_resume import show; show()
elif page == "ats":
    from views.ats import show; show()
elif page == "resume_chat":
    from views.resume_chat import show; show()
elif page == "interview":
    from views.interview import show; show()
elif page == "cover_letter":
    from views.cover_letter import show; show()
elif page == "profile":
    from views.profile import show; show()
else:
    st.session_state["page"] = "login"
    st.rerun()
