import streamlit as st
from UI6translation import TEXT
from api_client import process_audio_file
from components.transcription_tab import render
from Frontend.components.audit_tab import render_audit


def show():
    lang = st.session_state.get('lang', 'en')
    t = TEXT[lang]

    # --- 1. Input Section ---
    with st.container(border=True):
        # 1st Row: Allow the file uploader to stretch across the full width for a cleaner drop zone
        uploaded_file = st.file_uploader(t.get('lbl_upload', "Upload Audio File (.wav, .mp3)"), type=['wav', 'mp3'])
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # 2nd Row: Place the ID and Button beneath the uploader
        col_id, col_btn = st.columns([3, 1], gap="medium")
        
        with col_id:
            taker_id = st.text_input(t.get('lbl_taker_id', "Call Taker ID"), placeholder="e.g. CT-1099")
            
        with col_btn:
            # 1.75rem is the exact height needed to push the button down 
            # so it aligns perfectly with the input box (accounting for the label)
            st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
            analyze_btn = st.button(t.get('lbl_analyze_btn', "Analyze Call"), type="primary", use_container_width=True)

    st.divider()

    # --- 2. Processing & Results Section ---
    if analyze_btn:
        if not uploaded_file:
            st.error(t.get('err_no_file', "Please upload an audio file first."))
        elif not taker_id:
            st.error(t.get('err_no_id', "Please enter a Call Taker ID."))
        else:
            # Display loading spinner
            with st.spinner(t.get('lbl_loading', "AI is processing audio (Transcription, NLP, Auditing)... Please wait.")):
                
                # Send to FastAPI Backend
                result_json = process_audio_file(uploaded_file, taker_id)
                if result_json:
                    st.session_state['analysis_result']=result_json
                    st.success(
                        f"Transcription complete. Call ID: `{result_json.get('call_id')}`. "
                        f"Audit is running in background — check Audit Reports tab shortly."
                    )
                else:
                    st.error("Processing failed. Check backend logs.")
                # Save results to session state so they don't disappear if user changes language
                st.session_state['analysis_result'] = result_json

    # --- 3. Render Tabs if data exists ---
    if 'analysis_result' in st.session_state:
        data = st.session_state['analysis_result']
        if data.get("call_id"):
            st.caption(f"Call ID: `{data['call_id']}`")

        tab_titles = [t.get('tab_trans_sum', "Transcription & Summary"), t.get('tab_audit', "QA Audit")]
        tab1, tab2 = st.tabs(tab_titles)
        
        
        with tab1:
            render_audit(data, t)
            
        with tab2:
            render(data, t)