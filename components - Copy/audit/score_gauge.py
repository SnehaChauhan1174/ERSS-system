import streamlit as st

def render_score_gauge(score, max_score, status="UNSATISFACTORY", breach_text="Severe Protocol Breach"):
    st.markdown(
        f"""
        <div class="custom-card" style="text-align: center; justify-content: center; align-items: center;">
            <p style="margin: 0; font-size: 14px; font-weight: 600; color: #475569; letter-spacing: 0.05em;">TOTAL SCORE</p>
            <div style="margin: 20px 0; position: relative; width: 120px; height: 120px; border: 8px solid #EF4444; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 28px; font-weight: 700; color: #0F172A;">{score}</span>
            </div>
            <h2 style="margin: 0 0 8px 0; color: #0F172A; font-weight: 700;">{score} / {max_score}</h2>
            <div class="badge-unsatisfactory">{status}</div>
            <p style="color: #EF4444; font-size: 13px; margin: 8px 0 0 0; font-weight: 500;">{breach_text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )