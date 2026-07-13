import streamlit as st

# Modern SaaS Color Palette
COLORS = {
    "green": "#10b981",  # Emerald 500
    "orange": "#f59e0b", # Amber 500
    "red": "#ef4444",    # Red 500
    "blue": "#3b82f6",   # Blue 500
    "purple": "#8b5cf6", # Violet 500
    "teal": "#14b8a6",   # Teal 500
    "text_main": "#1e293b",
    "text_muted": "#64748b",
    "bg_light": "#f8fafc",
    "border": "#e2e8f0"
}

def get_severity_badge(severity_raw):
    """Returns a sleek pill-shaped badge for severity levels."""
    sev = str(severity_raw).lower()
    if sev == "high":
        return f"<span style='background-color: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{sev}</span>"
    elif sev == "medium":
        return f"<span style='background-color: #fef3c7; color: #b45309; padding: 4px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{sev}</span>"
    return f"<span style='background-color: #d1fae5; color: #047857; padding: 4px 10px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{sev}</span>"

def render_audit(data, t):
    """Renders the transcription and summary UI in a sleek, modern SaaS layout."""
    summary = data.get("summary", {})
    transcript = data.get("transcript", [])
    
    # st.markdown(f"<h2 style='margin-top: -10px; margin-bottom: 20px; font-weight: 600; color: #111; letter-spacing: -0.5px;'>{t.get('lbl_call_summary_title', 'Call Summary').replace('📄 ', '').upper()}</h2>", unsafe_allow_html=True)
    
    # ==========================================
    # ROW 1: Incident Overview & Additional Information
    # ==========================================
    # Changed from [10, 1, 10] to [25, 1, 25] to make the middle spacer column much thinner
    col1, spacer1, col2 = st.columns([25, 1, 25])
    
    with col1:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_incident_overview', 'INCIDENT OVERVIEW').upper()}</div>", unsafe_allow_html=True)
            
            # Increased font sizes to 0.95rem and reduced gap to 12px
            overview_html = (
                "<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; row-gap: 12px; font-size: 0.95rem;'>"
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_incident_type', 'Incident Type')}" "</div>"
                f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{summary.get('incident_type', 'N/A')}</div></div>"
                
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_subtype', 'Subtype')}" "</div>"
                f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{summary.get('incident_subtype', 'N/A')}</div></div>"
                
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_severity', 'Severity')}" "</div>"
                f"<div style='margin-top: 2px;'>{get_severity_badge(summary.get('severity', 'N/A'))}</div></div>"
                
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_caller_name', 'Caller Name')}" "</div>"
                f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{summary.get('caller_name', 'N/A')}</div></div>"
                
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_caller_loc', 'Location')}" "</div>"
                f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{summary.get('caller_location', 'N/A')}</div></div>"
                
                "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{t.get('lbl_district', 'District')}" "</div>"
                f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{summary.get('district', 'N/A')}</div></div>"
                "</div>"
            )
            st.markdown(overview_html, unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_add_info', 'ADDITIONAL INFORMATION').upper()}</div>", unsafe_allow_html=True)
            
            other_info = summary.get("other_information", {})
            if other_info:
                info_html = "<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; row-gap: 12px; font-size: 0.95rem;'>"
                for k, v in other_info.items():
                    clean_key = k.replace("_", " ").title()
                    info_html += (
                        "<div><div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 2px;'>" f"{clean_key}</div>"
                        f"<div style='font-weight: 600; color: {COLORS['text_main']};'>{v}</div></div>"
                    )
                info_html += "</div>"
                st.markdown(info_html, unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='color: {COLORS['text_muted']}; font-size:0.95rem;'>{t.get('lbl_no_data', 'No additional data available.')}</div>", unsafe_allow_html=True)

    # ==========================================
    # ROW 2: Key Facts & Dispatcher Actions
    # ==========================================
    col3, spacer2, col4 = st.columns([25, 1, 25])
    
    with col3:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_key_facts', 'KEY ESTABLISHED FACTS').replace('📌 ', '').upper()}</div>", unsafe_allow_html=True)
            for fact in summary.get("key_facts", []):
                # Reduced margin-bottom and increased font size
                st.markdown(f"<div style='border-left: 3px solid {COLORS['blue']}; padding-left: 10px; margin-bottom: 6px; font-size: 0.95rem; color: {COLORS['text_main']}; line-height: 1.4;'>{fact}</div>", unsafe_allow_html=True)
                
    with col4:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_dispatcher_actions', 'DISPATCHER ACTIONS').replace('✅ ', '').upper()}</div>", unsafe_allow_html=True)
            for action in summary.get("dispatcher_actions", []):
                st.markdown(f"<div style='border-left: 3px solid {COLORS['orange']}; padding-left: 10px; margin-bottom: 6px; font-size: 0.95rem; color: {COLORS['text_main']}; line-height: 1.4;'>{action}</div>", unsafe_allow_html=True)

    # ==========================================
    # ROW 3: Entities & Final Summary
    # ==========================================
    col5, spacer3, col6 = st.columns([25, 1, 25])
    
    with col5:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_entities', 'IMPORTANT ENTITIES').replace('🏢 ', '').upper()}</div>", unsafe_allow_html=True)
            entities = summary.get("important_entities", [])
            
            tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 6px;'>"
            for entity in entities:
                tags_html += f"<span style='background-color: {COLORS['bg_light']}; border: 1px solid {COLORS['border']}; color: {COLORS['text_main']}; padding: 4px 10px; border-radius: 6px; font-size: 0.9rem; font-weight: 500;'>{entity}</span>"
            tags_html += "</div>"
            st.markdown(tags_html, unsafe_allow_html=True)
                
    with col6:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 10px;'>{t.get('lbl_final_summary', 'FINAL SUMMARY').replace('📝 ', '').upper()}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background-color: {COLORS['bg_light']}; padding: 12px; border-radius: 8px; font-size:0.95rem; color: {COLORS['text_main']}; line-height: 1.5; border: 1px solid {COLORS['border']};'>{summary.get('final_summary', 'No summary available.')}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # ROW 4: Diarized Transcript
    # ==========================================
    st.markdown(f"<h4 style='font-weight: 600; color: #111; letter-spacing: -0.5px; margin-bottom: 15px;'>{t.get('lbl_transcript', 'Diarized Transcript').replace('🗣️ ', '')}</h4>", unsafe_allow_html=True)
    
    with st.container(border=True, height=400):
        for line in transcript:
            speaker = line.get('speaker', 'UNKNOWN')
            text = line.get('text', '')
            time_range = f"{line.get('start', 0.0)}s - {line.get('end', 0.0)}s"
            
            is_agent = "CALL_TAKER" in speaker
            spk_color = COLORS['teal'] if is_agent else COLORS['purple']
            bg_color = f"{COLORS['teal']}10" if is_agent else "transparent"
            
            st.markdown(
                f"<div style='margin-bottom: 6px; line-height: 1.5; background-color: {bg_color}; padding: 8px 12px; border-radius: 6px;'>"
                f"<div style='font-size: 0.75rem; color: {COLORS['text_muted']}; font-family: monospace; margin-bottom: 2px;'>{time_range}</div>"
                f"<strong style='color:{spk_color}; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;'>{speaker}</strong><br>"
                f"<span style='font-size: 1rem; color: {COLORS['text_main']};'>{text}</span>"
                "</div>", 
                unsafe_allow_html=True
            )