import json

import streamlit as st
from UI6translation import TEXT
from UI8audio import render_audio_player
from components.transcription_tab import render
from Frontend.components.audit_tab import render_audit
import os

AUDIT_DIR      = "../storage/audits"
TRANSCRIPT_DIR = "../storage/transcripts"

def show():
    lang = st.session_state.get('lang', 'en')
    t = TEXT[lang]

    if not os.path.exists(AUDIT_DIR):
        st.warning("No audit reports found.")
        return
    
    audit_files=sorted(
        [f for f in os.listdir(AUDIT_DIR) if f.endswith(".json")],
        reverse=True
    )
    if not audit_files:
        st.info("No audit reports available yet.")
        return

    # dropdown — call id selector
    call_ids     = [f.replace(".json", "") for f in audit_files]
    selected_id  = st.selectbox("Select Call", call_ids)

    st.divider()
    if not selected_id:
        return
    
    audit_path=os.path.join(AUDIT_DIR,f"{selected_id}.json")
    try:
        with open(audit_path,"r",encoding="utf-8") as f:
            audit_raw=json.load(f)
        audit_data=audit_raw
    except Exception as e:
        st.error(f"could not load audit:{e}")
        return

    transcript_path=os.path.join(TRANSCRIPT_DIR,f"{selected_id}.json")
    summary_data=None
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path,"r",encoding="utf-8") as f:
                summary_data=json.load(f)
        except Exception as e:
            st.warning(f"Could not load transcript:{e}")
    col1,col2,col3=st.columns(3)
    col1.markdown(f"**Call ID:** `{selected_id}`")
    col2.markdown(f"**Audit Time:** {audit_raw.get('audit_time', '—')}")
    col3.markdown(f"**Call Taker:** {audit_raw.get('call_taker_id', '—')}")

    st.divider()

    # two tabs — transcript+summary | audit
    tab1, tab2 = st.tabs([
        t.get('tab_trans_sum', "Transcription & Summary"),
        t.get('tab_audit', "Audit")
    ])

    with tab1:
        if summary_data:
            render_audit(summary_data, t)
        else:
            st.warning("No transcript/summary found for this call.")

    with tab2:
        render(audit_data, t)

   