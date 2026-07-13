import streamlit as st

def render_transcript_tab(transcript_list):
    if not transcript_list:
        st.info("No conversational lines captured.")
        return

    st.markdown("<div style='max-height: 500px; overflow-y: auto; padding-right: 5px;'>", unsafe_allow_html=True)
    
    for row in transcript_list:
        speaker = row.get("speaker", "UNKNOWN")
        text = row.get("text", "")
        start_time = row.get("start", 0.0)
        
        # Style logic to alternate speaker backgrounds
        if speaker == "CALL_TAKER":
            bg_color = "#EFF6FF"   # Soft Blue Tint
            border_color = "#3B82F6"
            label_color = "#1E40AF"
            display_name = "🎧 CALL TAKER (Operator)"
        else:
            bg_color = "#F8FAFC"   # Clean Slate Grey
            border_color = "#94A3B8"
            label_color = "#475569"
            display_name = "👤 CALLER (Citizen)"

        st.markdown(
            f"""
            <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 11px; font-weight: 700; color: {label_color}; letter-spacing: 0.025em;">{display_name}</span>
                    <span style="font-size: 11px; color: #94A3B8;">⏱️ {start_time}s</span>
                </div>
                <p style="margin: 0; font-size: 12.5px; color: #1E293B; line-height: 1.5; font-weight: 400;">{text}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("</div>", unsafe_allow_html=True)