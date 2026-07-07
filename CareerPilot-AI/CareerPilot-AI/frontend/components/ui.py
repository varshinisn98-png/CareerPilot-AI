"""Reusable UI components for CareerPilot AI."""
import streamlit as st


def gradient_text(text: str, size: str = "2.2rem", gradient: str = "linear-gradient(135deg, #4f8bf9, #7c3aed)"):
    st.markdown(
        f'<h1 style="background:{gradient};-webkit-background-clip:text;'
        f'-webkit-text-fill-color:transparent;font-size:{size};font-weight:700;margin:0;">{text}</h1>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(
        f"""
        <div style="padding:1.5rem 0 1rem 0;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
                <span style="font-size:2rem;">{icon}</span>
                <h1 style="background:linear-gradient(135deg,#4f8bf9,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-size:2rem;font-weight:700;margin:0;">{title}</h1>
            </div>
            <p style="color:#64748b;font-size:1rem;margin:0;padding-left:52px;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(content_fn, padding: str = "1.5rem", bg: str = "rgba(255,255,255,0.03)",
         border: str = "rgba(255,255,255,0.08)"):
    """Wrap content in a styled card."""
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:16px;'
        f'padding:{padding};margin-bottom:1rem;">',
        unsafe_allow_html=True,
    )
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def stat_card(label: str, value, icon: str, color: str = "#4f8bf9", delta: str = ""):
    st.markdown(
        f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
            border-radius:16px;padding:1.2rem;border-left:3px solid {color};">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <p style="color:#64748b;font-size:0.8rem;font-weight:500;
                        text-transform:uppercase;letter-spacing:0.05em;margin:0 0 8px 0;">{label}</p>
                    <h2 style="color:{color};font-size:2rem;font-weight:700;margin:0;">{value}</h2>
                    {f'<p style="color:#22c55e;font-size:0.8rem;margin:4px 0 0 0;">{delta}</p>' if delta else ''}
                </div>
                <span style="font-size:2rem;opacity:0.7;">{icon}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ats_score_ring(score: float):
    if score >= 80:
        color, label, bg = "#22c55e", "Excellent", "#052e16"
    elif score >= 60:
        color, label, bg = "#f59e0b", "Good", "#1c1400"
    elif score >= 40:
        color, label, bg = "#f97316", "Fair", "#1c0a00"
    else:
        color, label, bg = "#ef4444", "Needs Work", "#1c0000"

    pct = score / 100
    circumference = 2 * 3.14159 * 54
    dash = pct * circumference

    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:1rem;">
            <div style="position:relative;width:140px;height:140px;">
                <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="54" fill="none"
                        stroke="rgba(255,255,255,0.06)" stroke-width="12"/>
                    <circle cx="70" cy="70" r="54" fill="none"
                        stroke="{color}" stroke-width="12"
                        stroke-dasharray="{dash:.1f} {circumference:.1f}"
                        stroke-dashoffset="{circumference/4:.1f}"
                        stroke-linecap="round"/>
                </svg>
                <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                    text-align:center;">
                    <div style="color:{color};font-size:1.8rem;font-weight:700;line-height:1;">{score:.0f}</div>
                    <div style="color:#64748b;font-size:0.7rem;">/100</div>
                </div>
            </div>
            <div style="background:{bg};border:1px solid {color}33;border-radius:20px;
                padding:4px 16px;margin-top:8px;">
                <span style="color:{color};font-size:0.85rem;font-weight:600;">{label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skill_chips(skills: list, color: str = "#4f8bf9"):
    if not skills:
        st.markdown('<p style="color:#475569;font-style:italic;">None found</p>', unsafe_allow_html=True)
        return
    chips = "".join(
        f'<span style="background:{color}15;color:{color};border:1px solid {color}40;'
        f'border-radius:20px;padding:4px 12px;font-size:0.82rem;font-weight:500;'
        f'display:inline-block;margin:3px;">{s}</span>'
        for s in skills
    )
    st.markdown(f'<div style="line-height:2.5;">{chips}</div>', unsafe_allow_html=True)


def divider():
    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:1rem 0;">',
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = "#4f8bf9"):
    st.markdown(
        f'<span style="background:{color}20;color:{color};border:1px solid {color}40;'
        f'border-radius:6px;padding:2px 10px;font-size:0.78rem;font-weight:600;">{text}</span>',
        unsafe_allow_html=True,
    )


def info_box(text: str, icon: str = "💡", color: str = "#4f8bf9"):
    st.markdown(
        f"""
        <div style="background:{color}10;border:1px solid {color}30;border-radius:12px;
            padding:1rem 1.2rem;display:flex;gap:12px;align-items:flex-start;">
            <span style="font-size:1.2rem;">{icon}</span>
            <p style="color:#cbd5e1;margin:0;font-size:0.9rem;line-height:1.6;">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label: str, value: float, color: str = "#4f8bf9"):
    st.markdown(
        f"""
        <div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#94a3b8;font-size:0.85rem;">{label}</span>
                <span style="color:{color};font-size:0.85rem;font-weight:600;">{value:.0f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.06);border-radius:99px;height:8px;">
                <div style="background:linear-gradient(90deg,{color},{color}99);
                    width:{min(value,100):.1f}%;height:8px;border-radius:99px;
                    transition:width 0.5s ease;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
