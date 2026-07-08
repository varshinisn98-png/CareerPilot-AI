import streamlit as st

def page_header(title: str, subtitle: str, icon: str = ""):
    """Render a beautiful page header with gradient styling."""
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem; padding: 1.5rem; background: linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.7)); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px;">
            <h1 style="display: flex; align-items: center; gap: 0.75rem; color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0;">
                <span style="font-size: 2.4rem;">{icon}</span> {title}
            </h1>
            <p style="color: #94a3b8; font-size: 1.05rem; margin: 0; font-weight: 400; line-height: 1.5;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def divider():
    """Render a subtle horizontal divider line."""
    st.markdown(
        """
        <hr style="border: 0; height: 1px; background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.1) 20%, rgba(255, 255, 255, 0.1) 80%, rgba(255, 255, 255, 0)); margin: 2rem 0;">
        """,
        unsafe_allow_html=True
    )


def stat_card(title: str, value: str, icon: str, color: str):
    """Render a premium styled KPI / stat card."""
    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.3); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 16px; padding: 1.25rem; display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="width: 48px; height: 48px; background: {color}15; border: 1px solid {color}30; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: {color}; flex-shrink: 0;">
                {icon}
            </div>
            <div>
                <p style="color: #94a3b8; font-size: 0.8rem; margin: 0 0 2px 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{title}</p>
                <h3 style="color: #f8fafc; font-size: 1.5rem; font-weight: 800; margin: 0; line-height: 1.2;">{value}</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_box(text: str, icon: str = "ℹ️", color: str = "#3b82f6"):
    """Render a premium info box message."""
    st.markdown(
        f"""
        <div style="background: {color}10; border: 1px solid {color}30; border-radius: 12px; padding: 1.2rem; display: flex; gap: 0.75rem; align-items: flex-start; margin-bottom: 1.5rem;">
            <span style="font-size: 1.4rem; color: {color}; line-height: 1;">{icon}</span>
            <p style="color: #f1f5f9; font-size: 0.95rem; margin: 0; line-height: 1.5; font-weight: 450;">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def progress_bar(label: str, percent: float, color: str = "#10b981"):
    """Render a styled progress bar with text description and percentage."""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span style="color: #e2e8f0; font-size: 0.9rem; font-weight: 500;">{label}</span>
                <span style="color: {color}; font-size: 0.9rem; font-weight: 700;">{percent:.0f}%</span>
            </div>
            <div style="width: 100%; height: 8px; background: rgba(255, 255, 255, 0.08); border-radius: 4px; overflow: hidden;">
                <div style="width: {percent}%; height: 100%; background: {color}; border-radius: 4px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def skill_chips(skills: list, color: str = "#3b82f6"):
    """Render skill items as a responsive collection of modern badges."""
    if not skills:
        st.markdown('<p style="color:#64748b; font-size:0.9rem; font-style:italic; margin:0;">No skills extracted.</p>', unsafe_allow_html=True)
        return
    badges = "".join(
        f'<span style="background:{color}15; color:{color}; border:1px solid {color}35; '
        f'border-radius:20px; padding:4px 12px; margin:4px; font-size:0.85em; '
        f'display:inline-block; font-weight:500; letter-spacing:0.02em;">{s}</span>'
        for s in skills
    )
    st.markdown(f'<div style="line-height:2.2; display:flex; flex-wrap:wrap; margin-top: 0.5rem;">{badges}</div>', unsafe_allow_html=True)


def ats_score_ring(score: float):
    """Render a highly styled circular progress dial for the ATS match score."""
    if score >= 80:
        color, label = "#22c55e", "Excellent"
    elif score >= 60:
        color, label = "#3b82f6", "Good"
    elif score >= 40:
        color, label = "#eab308", "Fair"
    else:
        color, label = "#ef4444", "Poor"

    st.markdown(
        f"""
        <div style="text-align:center; padding:1.5rem 0;">
            <div style="
                width:150px; height:150px; border-radius:50%;
                background: conic-gradient({color} {score * 3.6}deg, rgba(255, 255, 255, 0.05) 0deg);
                display:inline-flex; align-items:center; justify-content:center;
                margin: auto;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            ">
                <div style="
                    width:124px; height:124px; border-radius:50%;
                    background:#0f172a; display:flex; align-items:center;
                    justify-content:center; flex-direction:column;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                ">
                    <span style="font-size:2.2rem; font-weight:800; color:{color}; line-height: 1;">{score:.0f}</span>
                    <span style="font-size:0.8rem; color:#64748b; margin-top: 4px; font-weight: 600; letter-spacing: 0.05em;">MATCH</span>
                </div>
            </div>
            <p style="color:{color}; font-weight:700; margin: 12px 0 0 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;">{label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
