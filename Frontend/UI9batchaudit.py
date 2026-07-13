import streamlit as st
import pandas as pd
import plotly.express as px
from UI6translation import TEXT
from UI8audio import render_audio_player

# Modern SaaS Color Palette
COLORS = {
    "green": "#10b981", "orange": "#f59e0b", "red": "#ef4444", 
    "blue": "#3b82f6", "purple": "#8b5cf6", "teal": "#14b8a6",
    "text_main": "#1e293b", "text_muted": "#64748b", "bg_light": "#f8fafc", "border": "#e2e8f0"
}

def get_verdict_badge(verdict_str, score):
    v = str(verdict_str).upper()
    if score >= 80 or "GOOD" in v or "EXCELLENT" in v:
        return f"<span style='background-color: #d1fae5; color: #047857; padding: 2px 8px; border-radius: 99px; font-size: 0.65rem; font-weight: 700;'>PASS</span>"
    elif score >= 60 or "MARGINAL" in v:
        return f"<span style='background-color: #fef3c7; color: #b45309; padding: 2px 8px; border-radius: 99px; font-size: 0.65rem; font-weight: 700;'>MARGINAL</span>"
    return f"<span style='background-color: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 99px; font-size: 0.65rem; font-weight: 700;'>FAIL</span>"

def show():
    lang = st.session_state.get('lang', 'en')
    t = TEXT[lang]

    # st.title(t.get("audit_page_title", "Global Audit Dashboard"))
    # st.markdown(f"<div style='color: {COLORS['text_muted']}; margin-bottom: 1.5rem;'>{t.get('audit_page_desc', 'View comprehensive metrics and performance overviews across all call takers.')}</div>", unsafe_allow_html=True)

    # 1. Widget in AGGREGATE Mode
    payload = render_audio_player(t, mode="aggregate")
    
    st.divider()

    if not payload or not payload.get("reports"):
        st.info(t.get("lbl_no_dashboard_data", "No audit reports found for the selected timeframe. Adjust filters to generate dashboard."))
        return

    reports = payload["reports"]
    start_dt = payload["start_dt"]
    end_dt = payload["end_dt"]

    # ---------------------------------------------------------
    # AGGREGATION LOGIC
    # ---------------------------------------------------------
    total_calls = len(reports)
    scores = []
    unsatisfactory_count = 0
    
    highest_score = -1
    highest_file = ""
    lowest_score = 101
    lowest_file = ""

    graph_data = []
    dim_sums = {}
    dim_weights = {}
    vocal_sum = 0
    vocal_count = 0

    for rep in reports:
        dt_obj = rep["dt"]
        fname = rep["filename"]
        audit = rep["data"].get("audit_report", rep["data"].get("audit", {}))
        
        meta = audit.get("meta", {})
        score = meta.get("total_weighted_score", 0)
        verdict = meta.get("performance_verdict", "")
        
        scores.append(score)
        graph_data.append({"date": dt_obj, "score": score})
        
        if score > highest_score:
            highest_score = score
            highest_file = fname
        if score < lowest_score:
            lowest_score = score
            lowest_file = fname
            
        if score < 60 or "MARGINAL" in str(verdict).upper() or "UNSATISFACTORY" in str(verdict).upper():
            unsatisfactory_count += 1

        # Soft Skills
        v_score = audit.get("soft_skills_analysis", {}).get("vocal_score")
        if v_score is not None:
            vocal_sum += v_score
            vocal_count += 1

        # Dimensions
        comp = audit.get("script_compliance", {})
        for key, val in comp.items():
            clean_name = key.split('_')[0].replace("_", " ").title() + (" " + key.split('_')[1].title() if len(key.split('_')) > 1 and not key.split('_')[1].isdigit() else "")
            achieved = val.get("weighted_contribution", 0)
            weight = float(str(val.get("weight", "0")).replace("%", ""))
            
            if clean_name not in dim_sums:
                dim_sums[clean_name] = 0
                dim_weights[clean_name] = weight
            dim_sums[clean_name] += achieved

    avg_score = sum(scores) / total_calls if total_calls > 0 else 0
    avg_vocal = vocal_sum / vocal_count if vocal_count > 0 else 0

    # ---------------------------------------------------------
    # ROW 1: TOP METRICS (5 Columns)
    # ---------------------------------------------------------
    m1, m2, m3, m4, m5 = st.columns(5)
    
    def metric_card(col, title, value, subtext="", color=COLORS["text_main"]):
        with col.container(border=True):
            st.markdown(f"<div style='font-size: 0.7rem; font-weight: 700; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 5px;'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 1.6rem; font-weight: 600; color: {color}; margin-bottom: 2px;'>{value}</div>", unsafe_allow_html=True)
            if subtext:
                st.markdown(f"<div style='font-size: 0.65rem; color: {COLORS['text_muted']}; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;'>{subtext}</div>", unsafe_allow_html=True)

    metric_card(m1, "Total Audits", total_calls, "Selected Timeframe")
    metric_card(m2, "Avg Score", f"{avg_score:.1f}", "/ 100", color=COLORS["blue"])
    metric_card(m3, "Highest Score", f"{highest_score:.1f}", f"File: {highest_file}", color=COLORS["green"])
    metric_card(m4, "Lowest Score", f"{lowest_score:.1f}", f"File: {lowest_file}", color=COLORS["red"])
    metric_card(m5, "Unsatisfactory", unsatisfactory_count, f"{(unsatisfactory_count/total_calls)*100:.1f}% of volume", color=COLORS["orange"])

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ROW 2: LINE GRAPH & DIMENSIONS
    # ---------------------------------------------------------
    col_graph, spacer1, col_dims = st.columns([25, 1, 25])

    with col_graph:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; color: {COLORS['text_muted']}; margin-bottom: 10px;'>SCORE TREND</div>", unsafe_allow_html=True)
            
            df = pd.DataFrame(graph_data)
            time_diff = (end_dt - start_dt).total_seconds()
            
            if time_diff <= 86400: # Single day -> Hourly
                df['Time'] = df['date'].dt.strftime('%H:00')
                trend_df = df.groupby('Time')['score'].mean().reset_index()
                fig = px.line(trend_df, x='Time', y='score', markers=True, color_discrete_sequence=[COLORS['blue']])
            else: # Multi-day -> Daily (Last 7 days)
                df['Date'] = df['date'].dt.strftime('%Y-%m-%d')
                trend_df = df.groupby('Date')['score'].mean().reset_index()
                trend_df = trend_df.tail(7) # Enforce 7 days max
                fig = px.line(trend_df, x='Date', y='score', markers=True, color_discrete_sequence=[COLORS['purple']])
                
            fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_range=[0, 100], plot_bgcolor="rgba(0,0,0,0)")
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor=COLORS['border'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_dims:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; color: {COLORS['text_muted']}; margin-bottom: 15px;'>AVERAGE DIMENSIONAL BREAKDOWN</div>", unsafe_allow_html=True)
            
            dim_colors = [COLORS["green"], COLORS["blue"], COLORS["orange"], COLORS["purple"], COLORS["red"]]
            bars_html = ""
            
            for idx, (name, total_achieved) in enumerate(dim_sums.items()):
                avg_achieved = total_achieved / total_calls
                weight = dim_weights[name]
                color = dim_colors[idx % len(dim_colors)]
                pct = min(max((avg_achieved / weight) * 100, 0), 100) if weight > 0 else 0
                
                bars_html += (
                    "<div style='margin-bottom: 14px;'>"
                    "<div style='display: flex; justify-content: space-between; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 6px; font-weight: 600;'>"
                    f"<span style='color: {COLORS['text_main']};'>{name}</span>"
                    f"<span style='color: {COLORS['text_muted']};'>{avg_achieved:.1f} / {weight} avg</span>"
                    "</div>"
                    f"<div style='width: 100%; background-color: {COLORS['bg_light']}; border-radius: 99px; height: 6px;'>"
                    f"<div style='width: {pct}%; background-color: {color}; height: 6px; border-radius: 99px;'></div>"
                    "</div>"
                    "</div>"
                )
            st.markdown(bars_html, unsafe_allow_html=True)
            
            # Soft Skills
            st.markdown(f"<div style='margin-top: 20px; font-size: 0.75rem; font-weight: 700; color: {COLORS['text_muted']};'>AVERAGE VOCAL/SOFT SKILLS</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 1.8rem; font-weight: 600; color: {COLORS['teal']};'>{avg_vocal:.1f} <span style='font-size: 1rem; color: #888;'>/ 10</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ROW 3: SCROLLABLE AUDIT LIST
    # ---------------------------------------------------------
    st.markdown(f"<h4 style='font-weight: 600; color: #111; letter-spacing: -0.5px;'>Processed Audit Logs</h4>", unsafe_allow_html=True)
    
    with st.container(border=True, height=400):
        # Reverse to show newest first
        for rep in reversed(reports):
            dt_formatted = rep["dt"].strftime("%Y-%m-%d | %I:%M %p")
            fname = rep["filename"]
            
            audit = rep["data"].get("audit_report", rep["data"].get("audit", {}))
            score = audit.get("meta", {}).get("total_weighted_score", 0)
            verdict = audit.get("meta", {}).get("performance_verdict", "Unknown")
            badge = get_verdict_badge(verdict, score)
            
            st.markdown(
                f"<div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {COLORS['bg_light']}; padding: 12px 0;'>"
                "<div>"
                f"<div style='font-size: 0.85rem; font-weight: 600; color: {COLORS['text_main']};'>{fname}</div>"
                f"<div style='font-size: 0.7rem; color: {COLORS['text_muted']}; font-family: monospace;'>{dt_formatted}</div>"
                "</div>"
                "<div style='display: flex; align-items: center; gap: 15px;'>"
                f"<div style='font-weight: 700; color: {COLORS['text_main']};'>{score:.1f}/100</div>"
                f"<div>{badge}</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )