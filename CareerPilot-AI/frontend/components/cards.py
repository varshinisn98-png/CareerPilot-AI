import streamlit as st


def metric_card(title: str, value, icon: str = "📊", color: str = "#4F8BF9"):
    """Render a styled metric card."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}22, {color}11);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        ">
            <span style="font-size:1.5em;">{icon}</span>
            <p style="margin:4px 0; color:#888; font-size:0.85em;">{title}</p>
            <h2 style="margin:0; color:{color};">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skill_badge(skill: str, color: str = "#4F8BF9"):
    """Return HTML for a skill badge."""
    return (
        f'<span style="background:{color}22; color:{color}; border:1px solid {color}; '
        f'border-radius:16px; padding:3px 10px; margin:3px; font-size:0.85em; '
        f'display:inline-block;">{skill}</span>'
    )


def render_skill_list(skills: list, color: str = "#4F8BF9"):
    """Render a list of skills as inline badges."""
    if not skills:
        st.info("No skills found.")
        return
    badges = " ".join(skill_badge(s, color) for s in skills)
    st.markdown(f'<div style="line-height:2.2;">{badges}</div>', unsafe_allow_html=True)


def ats_gauge(score: float):
    """Render an ATS score with color-coded indicator."""
    if score >= 80:
        color, label = "#28a745", "Excellent"
    elif score >= 60:
        color, label = "#ffc107", "Good"
    elif score >= 40:
        color, label = "#fd7e14", "Fair"
    else:
        color, label = "#dc3545", "Poor"

    st.markdown(
        f"""
        <div style="text-align:center; padding:20px;">
            <div style="
                width:120px; height:120px; border-radius:50%;
                background: conic-gradient({color} {score * 3.6}deg, #e9ecef 0deg);
                display:inline-flex; align-items:center; justify-content:center;
                margin: auto;
            ">
                <div style="
                    width:90px; height:90px; border-radius:50%;
                    background:white; display:flex; align-items:center;
                    justify-content:center; flex-direction:column;
                ">
                    <span style="font-size:1.4em; font-weight:bold; color:{color};">{score:.0f}</span>
                    <span style="font-size:0.7em; color:#888;">/ 100</span>
                </div>
            </div>
            <p style="color:{color}; font-weight:bold; margin-top:8px;">{label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
