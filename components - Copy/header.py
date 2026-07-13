import streamlit as st

def render_simple_header(title, subtitle):
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 15px;">
                <h3 style="margin: 0; color: #12355B; font-size: 20px; font-weight: 700;">{title}</h3>
                <p style="margin: 2px 0 0 0; color: #64748B; font-size: 13px;">{subtitle}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.button("📥 System Logs", use_container_width=True, key="log_btn")