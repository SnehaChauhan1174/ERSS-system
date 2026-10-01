import os
import json
import streamlit as st
from datetime import datetime, time
from UI6translation import TEXT
from components.transcription_tab import render
from components.audit_tab import render_audit

AUDIT_DIR      = "../storage/audits"
TRANSCRIPT_DIR = "../storage/transcripts"
AUDIO_DIR      = "../storage/audio"


def parse_audit_dt(audit_raw: dict, filename: str) -> datetime:
    audit_time_str = audit_raw.get("audit_time", "")
    for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(audit_time_str, fmt)
        except Exception:
            continue
    try:
        return datetime.fromtimestamp(os.path.getmtime(os.path.join(AUDIT_DIR, filename)))
    except Exception:
        return datetime.now()


def show():
    lang = st.session_state.get("lang", "en")
    t    = TEXT[lang]

    if not os.path.exists(AUDIT_DIR):
        st.warning("No audit reports found. Run some call analyses first.")
        return

    all_audit_files = sorted(
        [f for f in os.listdir(AUDIT_DIR) if f.endswith(".json")],
        reverse=True
    )

    if not all_audit_files:
        st.info("No audit reports available yet.")
        return

    # ── SECTION 1: date + hour filter ────────────────────────────────────────
    with st.container(border=True):
        st.markdown("**Filter Reports by Date & Time**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            start_date = st.date_input("Start Date", value=datetime(2026, 7, 10))
        with c2:
            hour_options = [f"{h:02d}:00" for h in range(24)]
            start_hour_str = st.selectbox("Start Hour", hour_options, index=0, key="sh")
        with c3:
            end_date = st.date_input("End Date", value=datetime.today())
        with c4:
            end_hour_str = st.selectbox("End Hour", hour_options, index=23, key="eh")

        start_dt = datetime.combine(start_date, time(int(start_hour_str[:2]), 0, 0))
        end_dt   = datetime.combine(end_date,   time(int(end_hour_str[:2]), 59, 59))

        if start_dt > end_dt:
            st.warning("Start date/time cannot be after end date/time.")
            return

    # ── filter audit files by date range ─────────────────────────────────────
    filtered = []
    for fname in all_audit_files:
        try:
            with open(os.path.join(AUDIT_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            dt = parse_audit_dt(data, fname)
            if start_dt <= dt <= end_dt:
                filtered.append({
                    "filename": fname,
                    "call_id":  data.get("call_id", fname.replace(".json", "")),
                    "dt":       dt,
                    "data":     data
                })
        except Exception as e:
            print(f"skipping {fname}: {e}")

    filtered.sort(key=lambda x: x["dt"], reverse=True)

    if not filtered:
        st.info(f"No audit reports found between {start_dt.strftime('%d-%m-%Y %H:%M')} and {end_dt.strftime('%d-%m-%Y %H:%M')}.")
        return

    st.markdown(f"<div style='color:#64748b; font-size:0.8rem; margin: 8px 0;'>Showing {len(filtered)} report(s)</div>", unsafe_allow_html=True)

    # ── SECTION 2: call selector dropdown ────────────────────────────────────
    call_options = {
        f"{rep['call_id']}  —  {rep['dt'].strftime('%d %b %Y  %H:%M')}": rep
        for rep in filtered
    }

    selected_label = st.selectbox("Select Call Report", list(call_options.keys()))
    selected_rep   = call_options[selected_label]
    audit_raw      = selected_rep["data"]
    selected_id    = selected_rep["call_id"]

    st.divider()

    # ── SECTION 3: call metadata row ─────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"**Call ID**\n\n`{selected_id}`")
    col2.markdown(f"**Audit Time**\n\n{audit_raw.get('audit_time', '—')}")
    col3.markdown(f"**Call Taker**\n\n{audit_raw.get('call_taker_id', '—')}")

    audit_report = audit_raw.get("audit_report", audit_raw)
    total_score  = audit_report.get("meta", {}).get("total_weighted_score", "—")
    verdict      = audit_report.get("meta", {}).get("performance_verdict", "—")
    col4.markdown(f"**Score**\n\n{total_score} / 100  —  {verdict[:15]}...")

    # ── SECTION 4: audio player ───────────────────────────────────────────────
    audio_file  = audit_raw.get("audio_file", "")
    audio_found = False

    if audio_file and os.path.exists(AUDIO_DIR):
        # try exact match first
        exact_path = os.path.join(AUDIO_DIR, audio_file)
        if os.path.exists(exact_path):
            st.audio(exact_path, format="audio/wav")
            audio_found = True
        else:
            # search for any file starting with call_id
            for f in os.listdir(AUDIO_DIR):
                if f.startswith(selected_id) or f == audio_file:
                    st.audio(os.path.join(AUDIO_DIR, f), format="audio/wav")
                    audio_found = True
                    break

    if not audio_found:
        st.caption("Audio file not available for playback.")

    st.divider()
    # load transcript/summary data
    summary_data = None
    transcript_path = os.path.join(TRANSCRIPT_DIR, f"{selected_id}.json")
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
        except Exception as e:
            st.warning(f"Could not load transcript: {e}")

    # ── SECTION 5: transcript + audit tabs ───────────────────────────────────
    tab1, tab2 = st.tabs([
        t.get("tab_audit", "Audit"),
        t.get("tab_trans_sum", "Transcription & summary")
    ])

    with tab1:
        render(audit_report, summary_data,t)

    with tab2:
        if summary_data:
            render_audit(summary_data, t)
        else:
            st.warning("No transcript or summary found for this call.")