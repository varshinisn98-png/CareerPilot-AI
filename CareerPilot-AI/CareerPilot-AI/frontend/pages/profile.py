import streamlit as st
import httpx

API_BASE = "http://localhost:8000/api"


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def show():
    if not st.session_state.get("token"):
        st.session_state["page"] = "login"; st.rerun()

    from components.ui import page_header, divider, stat_card

    page_header("Profile", "Manage your account and view your career stats", "👤")

    user = st.session_state.get("user", {})

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,rgba(79,139,249,0.15),rgba(124,58,237,0.15));
                border:1px solid rgba(79,139,249,0.3);border-radius:20px;padding:2rem;text-align:center;">
                <div style="width:80px;height:80px;background:linear-gradient(135deg,#4f8bf9,#7c3aed);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 1rem auto;font-size:2rem;">
                    {user.get('full_name','U')[0].upper()}
                </div>
                <h2 style="color:#f1f5f9;font-size:1.2rem;font-weight:700;margin:0 0 4px 0;">
                    {user.get('full_name','')}</h2>
                <p style="color:#64748b;font-size:0.85rem;margin:0;">{user.get('email','')}</p>
                <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);
                    border-radius:20px;padding:3px 12px;margin-top:12px;display:inline-block;">
                    <span style="color:#22c55e;font-size:0.78rem;font-weight:600;">✅ Active Account</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        # Stats
        resumes = st.session_state.get("resumes", [])
        stat_card("Resumes Uploaded", len(resumes), "📄", "#4f8bf9")

    with col_r:
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:16px;padding:1.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### ✏️ Update Profile")

        with st.form("profile_form"):
            new_name = st.text_input("Full Name", value=user.get("full_name", ""))
            new_email = st.text_input("Email", value=user.get("email", ""))
            save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if save:
            with st.spinner("Saving..."):
                try:
                    payload = {}
                    if new_name != user.get("full_name"):
                        payload["full_name"] = new_name
                    if new_email != user.get("email"):
                        payload["email"] = new_email
                    if payload:
                        res = httpx.put(f"{API_BASE}/user/me", headers=_headers(),
                                        json=payload, timeout=10)
                        if res.status_code == 200:
                            st.session_state["user"] = res.json()
                            st.success("✅ Profile updated!")
                            st.rerun()
                        else:
                            try: msg = res.json().get("detail", "Update failed.")
                            except: msg = "Update failed."
                            st.error(msg)
                    else:
                        st.info("No changes to save.")
                except Exception as e:
                    st.error(f"Error: {e}")

        divider()

        st.markdown(
            '<div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);'
            'border-radius:14px;padding:1.2rem;">',
            unsafe_allow_html=True,
        )
        st.markdown("##### ⚠️ Danger Zone")
        st.markdown('<p style="color:#64748b;font-size:0.85rem;">'
                    'Deleting your account is permanent and cannot be undone.</p>',
                    unsafe_allow_html=True)
        if st.button("🗑️ Delete Account", use_container_width=True):
            st.session_state["confirm_delete"] = True

        if st.session_state.get("confirm_delete"):
            st.warning("Are you sure? This will delete all your data permanently.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, Delete", type="primary", use_container_width=True):
                    try:
                        httpx.delete(f"{API_BASE}/user/me", headers=_headers(), timeout=10)
                    except Exception:
                        pass
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.session_state["page"] = "login"
                    st.rerun()
            with c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pop("confirm_delete", None)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
