# components/audit/score_header.py
import streamlit as st
import os

def render_score_header(title, subtitle):
    # Standard Header layout
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown(f"<h2 style='margin-bottom:0px; color:#12355B;'>{title}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#6B7280; margin-top:2px;'>{subtitle}</p>", unsafe_allow_html=True)
    with col2:
        ec1, ec2 = st.columns(2)
        ec1.button("📥 Export", use_container_width=True, key="audit_export")
        ec2.button("🔄 Share", use_container_width=True, key="audit_share")
        
    st.write("") 

    # DYNAMIC AUDIT DIRECTORY LOOKUP
    audit_dir = "storage/audits"
    available_calls = []
    
    if os.path.exists(audit_dir):
        # Scan folder for files like CALL_04-07-2026_0001.json and clean up extensions
        available_calls = [f.replace(".json", "") for f in os.listdir(audit_dir) if f.endswith(".json")]
    
    # Fallback default items if folder is empty initially
    if not available_calls:
        available_calls = ["No reports available"]

    # Filter Bar UI
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([3, 3, 3, 2])
        with f1:
            ct_id = st.selectbox("Call Taker ID", ["CT-04", "CT-05", "System-Auto"], key="audit_ct_select")
        with f2:
            # Dropdown is now dynamically populated from the local backend folder storage!
            call_id = st.selectbox("Call ID", sorted(available_calls, reverse=True), key="audit_call_select")
        with f3:
            selected_date = st.date_input("Date", key="audit_date_select")
        with f4:
            st.write("") 
            st.write("")
            submit_clicked = st.button("View Report", type="primary", use_container_width=True, key="audit_submit")
            
    return submit_clicked, ct_id, call_id, selected_date