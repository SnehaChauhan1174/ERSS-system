import os
import json
import re
import streamlit as st
from datetime import datetime, time

# Robust directory paths to handle running from project root or inside Frontend directory
AUDIT_FOLDER_PATHS = ["storage/audits", "../storage/audits", "Backend/audits", "audits"]
TRANSCRIPT_FOLDER_PATHS = ["storage/transcripts", "../storage/transcripts", "transcripts"]
AUDIO_FOLDER_PATHS = ["storage/audio", "../storage/audio", "Backend/uploaded_audios", "uploaded_audios", "audio"]

def get_valid_directory(paths):
    """Locates the first folder path that actually exists in the runtime environment."""
    for path in paths:
        if os.path.exists(path):
            return path, True
    return paths[0], False

def parse_audit_timestamp(file_path, file_name, json_data) -> datetime:
    """
    Robust datetime parser for audit records.
    Parses 'audit_time' key inside JSON or falls back to filename date regex.
    """
    if json_data and isinstance(json_data, dict):
        audit_time_str = json_data.get("audit_time") or json_data.get("meta", {}).get("audit_time")
        if audit_time_str:
            for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                try:
                    return datetime.strptime(str(audit_time_str), fmt)
                except ValueError:
                    continue

    # Filename fallback matching CALL_dd-mm-yyyy_xxxx format
    match = re.search(r'(\d{2}-\d{2}-\d{4})', file_name)
    if match:
        try:
            return datetime.strptime(match.group(1), "%d-%m-%Y")
        except ValueError:
            pass
            
    try:
        mtime = os.path.getmtime(os.path.join(file_path, file_name))
        return datetime.fromtimestamp(mtime)
    except Exception:
        return datetime.now()


def render_audio_player(t, mode="aggregate"):
    """
    Renders date-time filter range controls.
    Drives both Batch Dashboard and Single Call Browser strictly using 
    saved JSON audit reports inside storage/audits.
    """
    audit_dir, audit_dir_exists = get_valid_directory(AUDIT_FOLDER_PATHS)
    transcript_dir, transcript_dir_exists = get_valid_directory(TRANSCRIPT_FOLDER_PATHS)
    audio_dir, audio_dir_exists = get_valid_directory(AUDIO_FOLDER_PATHS)

    # ---------------------------------------------------------
    # SHARED FILTER USER INTERFACE
    # ---------------------------------------------------------
    st.markdown(
        """
        <style>
        .filter-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='filter-title'>Filter Processed Audit Reports</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Default to July 13, 2026
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2026, 7, 13))
    with col2:
        end_date = st.date_input("End Date", value=datetime(2026, 7, 13))

    hour_options = [f"{h:02d}:00" for h in range(24)]

    with col3:
        start_hour_str = st.selectbox("Start Hour", options=hour_options, index=0)
    with col4:
        end_hour_str = st.selectbox("End Hour", options=hour_options, index=23)

    start_hour = int(start_hour_str.split(":")[0])
    end_hour = int(end_hour_str.split(":")[0])

    start_dt = datetime.combine(start_date, time(start_hour, 0, 0))
    end_dt = datetime.combine(end_date, time(end_hour, 59, 59))

    if start_dt > end_dt:
        st.warning(t.get('audio_invalid_range', "Start date/time cannot be after end date/time."))
        return None

    # Load and filter JSON audit files dynamically
    filtered_reports = []
    
    if audit_dir_exists:
        for file_name in os.listdir(audit_dir):
            if file_name.endswith(".json"):
                try:
                    file_full_path = os.path.join(audit_dir, file_name)
                    with open(file_full_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)

                    audit_dt = parse_audit_timestamp(audit_dir, file_name, json_data)

                    if start_dt <= audit_dt <= end_dt:
                        filtered_reports.append({
                            "dt": audit_dt,
                            "filename": file_name,
                            "call_id": json_data.get("call_id") or file_name.replace(".json", ""),
                            "audio_file": json_data.get("audio_file") or file_name.replace(".json", ".wav"),
                            "data": json_data
                        })
                except Exception as parse_err:
                    print(f"Skipping malformed audit report '{file_name}': {parse_err}")

    # Sort matching files chronologically
    filtered_reports = sorted(filtered_reports, key=lambda x: x["dt"])

    # ---------------------------------------------------------
    # AGGREGATE DASHBOARD MODE OUTPUT
    # ---------------------------------------------------------
    if mode == "aggregate":
        if not filtered_reports:
            st.info(t.get("lbl_no_dashboard_data", "No audit reports found for the selected timeframe. Adjust filters to generate dashboard."))
            return None
        return {
            "reports": filtered_reports,
            "start_dt": start_dt,
            "end_dt": end_dt
        }

    # ---------------------------------------------------------
    # SINGLE RECORD BROWSER NAVIGATION MODE
    # ---------------------------------------------------------
    elif mode == "browser":
        if not filtered_reports:
            st.info(t.get('audio_no_files_range', "No audit reports found within this selected time range."))
            return None

        # Dropdown to select specific Audit ID
        call_options = {rep["call_id"]: rep for rep in filtered_reports}
        selected_call_id = st.selectbox(t.get('audio_select_label', "Select Audit Report"), list(call_options.keys()))
        
        selected_rep = call_options[selected_call_id]
        
        # Check for optional audio file playback
        audio_filename = selected_rep["audio_file"]
        possible_audio_path = os.path.join(audio_dir, audio_filename)
        
        if not os.path.exists(possible_audio_path) and audio_dir_exists:
            for f in os.listdir(audio_dir):
                if f.startswith(selected_call_id) and f.endswith(".wav"):
                    possible_audio_path = os.path.join(audio_dir, f)
                    break

        if os.path.exists(possible_audio_path):
            st.audio(possible_audio_path, format="audio/wav")
        else:
            st.info("ℹ️ Audit report loaded. (No corresponding audio file found.)")

        # Initialize the payload to send back to UI5reports.py
        combined_report = {
            "summary_data": None,
            "audit_data": selected_rep["data"]
        }

        # Load corresponding Transcript Summary if available
        summary_filename = f"{selected_call_id}.json"
        summary_file_path = os.path.join(transcript_dir, summary_filename)

        if os.path.exists(summary_file_path):
            try:
                with open(summary_file_path, 'r', encoding='utf-8') as f:
                    combined_report["summary_data"] = json.load(f)
            except Exception as e:
                st.error(f"Error reading transcript summary: {e}")
        else:
            combined_report["summary_data"] = {
                "call_id": selected_call_id,
                "transcript": selected_rep["data"].get("audit_report", {}).get("transcript_context", [])
            }

        return combined_report

    return None