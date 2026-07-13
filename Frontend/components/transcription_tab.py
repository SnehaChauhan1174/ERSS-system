import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Modern SaaS Color Palette
COLORS = {
    "green": "#10b981",  # Emerald 500
    "orange": "#f59e0b", # Amber 500
    "red": "#ef4444",    # Red 500
    "blue": "#3b82f6",   # Blue 500
    "purple": "#8b5cf6", # Violet 500
    "text_main": "#1e293b",
    "text_muted": "#64748b",
    "bg_light": "#f8fafc",
    "border": "#e2e8f0"
}

def get_score_color(score_pct):
    if score_pct >= 80: return COLORS["green"]
    elif score_pct >= 60: return COLORS["orange"]
    return COLORS["red"]

def get_progress_bar_html(label, achieved, total, color):
    """Sleek, thin progress bar with modern typography."""
    pct = min(max((achieved / total) * 100, 0), 100) if total > 0 else 0
    return (
        "<div style='margin-bottom: 16px;'>"
        "<div style='display: flex; justify-content: space-between; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 600;'>"
        f"<span style='color: {COLORS['text_main']};'>{label}</span>"
        f"<span style='color: {COLORS['text_muted']};'>{achieved} / {total}</span>"
        "</div>"
        f"<div style='width: 100%; background-color: {COLORS['bg_light']}; border-radius: 99px; height: 5px;'>"
        f"<div style='width: {pct}%; background-color: {color}; height: 5px; border-radius: 99px;'></div>"
        "</div>"
        "</div>"
    )

def get_badge_html(text, color_type):
    """Pill-shaped badges with soft backgrounds."""
    styles = {
        "good": {"bg": "#d1fae5", "text": "#047857"},
        "ok": {"bg": "#fef3c7", "text": "#b45309"},
        "poor": {"bg": "#fee2e2", "text": "#b91c1c"},
        "default": {"bg": "#f1f5f9", "text": "#475569"}
    }
    s = styles.get(str(color_type).lower(), styles["default"])
    return f"<span style='background-color: {s['bg']}; color: {s['text']}; padding: 4px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{text}</span>"

def get_dots_html(rating_type):
    """Replaces emojis with modern rating dots."""
    if rating_type == 'good': return f"<span style='color:{COLORS['green']}; letter-spacing:2px;'>●●●●</span><span style='color:#e2e8f0'>●</span>"
    if rating_type == 'ok': return f"<span style='color:{COLORS['orange']}; letter-spacing:2px;'>●●●</span><span style='color:#e2e8f0'>●●</span>"
    return f"<span style='color:{COLORS['red']}; letter-spacing:2px;'>●●</span><span style='color:#e2e8f0'>●●●</span>"

def render(data, t):
    audit = data.get("audit_report", data.get("audit", {}))
    summary = data.get("summary_data", data.get("summary", {}))
    transcript = data.get("summary_data", {}).get("transcript", [])
    
    if not audit:
        st.info(t.get('lbl_audit_empty', 'Automated Audit is currently pending.'))
        return

    meta = audit.get("meta", {})
    compliance = audit.get("script_compliance", {})
    soft_skills = audit.get("soft_skills_analysis", {})
    
    total_score = meta.get("total_weighted_score", 0)
    verdict = meta.get("performance_verdict", "Unknown")
    score_color = get_score_color(total_score)

    duration_str = "Unknown"
    if transcript:
        end_time_sec = transcript[-1].get("end", 0)
        duration_str = f"{int(end_time_sec // 60)}m {int(end_time_sec % 60)}s"

    dim_colors = [COLORS["green"], COLORS["blue"], COLORS["orange"], COLORS["purple"], COLORS["red"]]

    # st.markdown(f"<h2 style='margin-top: -10px; margin-bottom: 25px; font-weight: 600; color: #111; letter-spacing: -0.5px;'>{t.get('lbl_audit_title', 'Call Audit Report')}</h2>", unsafe_allow_html=True)

    # ==========================================
    # ROW 1: MASTER OVERVIEW PANEL
    # ==========================================
    # Wrapping everything in one container eliminates the "floating boxes" look.
    with st.container(border=True):
        # col_gauge, col_bars, col_info = st.columns([1.2, 2, 1.2], gap="large")
        col_gauge, spacera, col_bars, spacerb, col_info = st.columns([25, 1, 25, 1, 25])


        with col_gauge:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_score,
                number={'font': {'size': 32, 'color': '#1e293b', 'family': 'sans-serif'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 0, 'visible': False},
                    'bar': {'color': score_color, 'thickness': 0.15},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 60], 'color': '#fee2e2'},
                        {'range': [60, 80], 'color': '#fef3c7'},
                        {'range': [80, 100], 'color': '#d1fae5'}
                    ],
                }
            ))
            fig.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f"<div style='text-align:center; color:{score_color}; font-weight:700; font-size:0.8rem; letter-spacing: 0.5px; margin-top:-20px;'>{verdict.upper()}</div>", unsafe_allow_html=True)

        with col_bars:
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 20px;'>SCORE BREAKDOWN</div>", unsafe_allow_html=True)
            bars_html = ""
            for idx, (key, val) in enumerate(compliance.items()):
                clean_name = key.split('_')[0].replace("_", " ").title() + (" " + key.split('_')[1].title() if len(key.split('_')) > 1 and not key.split('_')[1].isdigit() else "")
                achieved = val.get("weighted_contribution", 0)
                weight = float(str(val.get("weight", "0")).replace("%", ""))
                color = dim_colors[idx % len(dim_colors)]
                bars_html += get_progress_bar_html(clean_name, achieved, weight, color)
            st.markdown(bars_html, unsafe_allow_html=True)

        with col_info:
            # Modern vertical stacking for info grid instead of side-by-side
            st.markdown(
                f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 20px;'>CALL DETAILS</div>"
                "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 0.85rem;'>"
                "<div><div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 4px;'>Call ID</div><div style='font-weight: 600; color: #1e293b;'>" f"{audit.get('call_id', data.get('call_id', 'Unknown'))}" "</div></div>"
                "<div><div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 4px;'>Call Taker</div><div style='font-weight: 600; color: #1e293b;'>CT-Unknown</div></div>"
                "<div><div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 4px;'>Duration</div><div style='font-weight: 600; color: #1e293b;'>" f"{duration_str}" "</div></div>"
                "<div><div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 4px;'>Incident</div><div style='font-weight: 600; color: #1e293b;'>" f"{summary.get('incident_type', 'Unknown')}" "</div></div>"
                "</div>", 
                unsafe_allow_html=True
            )

    # ==========================================
    # ROW 2: Tables & Soft Skills
    # ==========================================
    # col_table, col_soft = st.columns([1.7, 1], gap="large")
    col_table, spacer1, col_soft = st.columns([25, 1, 25])

    with col_table:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 15px;'>DIMENSION SCORES (DETAILED)</div>", unsafe_allow_html=True)
            
            table_html = (
                "<table style='width: 100%; border-collapse: collapse; font-size: 0.85rem;'>"
                f"<tr style='border-bottom: 1px solid {COLORS['border']}; color: {COLORS['text_muted']}; text-align: left; font-size: 0.75rem; text-transform: uppercase;'>"
                "<th style='padding: 12px 8px; font-weight: 600;'>Dimension</th>"
                "<th style='padding: 12px 8px; font-weight: 600;'>Achieved</th>"
                "<th style='padding: 12px 8px; font-weight: 600;'>Weight</th>"
                "<th style='padding: 12px 8px; font-weight: 600;'>Score</th>"
                "</tr>"
            )
            
            for idx, (key, val) in enumerate(compliance.items()):
                clean_name = key.split('_')[0].replace("_", " ").title() + (" " + key.split('_')[1].title() if len(key.split('_')) > 1 and not key.split('_')[1].isdigit() else "")
                achieved = val.get("weighted_contribution", 0)
                weight = float(str(val.get("weight", "0")).replace("%", ""))
                score_pct = (achieved / weight * 100) if weight > 0 else 0
                pct_color = get_score_color(score_pct)
                
                table_html += (
                    f"<tr style='border-bottom: 1px solid {COLORS['bg_light']};'>"
                    f"<td style='padding: 12px 8px; font-weight: 600; color: {COLORS['text_main']};'>{clean_name}</td>"
                    f"<td style='padding: 12px 8px; color: {COLORS['text_muted']};'>{achieved}</td>"
                    f"<td style='padding: 12px 8px; color: {COLORS['text_muted']};'>{weight}</td>"
                    f"<td style='padding: 12px 8px; color: {pct_color}; font-weight: 700;'>{score_pct:.1f}%</td>"
                    "</tr>"
                )
            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)

    with col_soft:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 15px;'>SOFT SKILLS ANALYSIS</div>", unsafe_allow_html=True)
            
            traits = soft_skills.get("soft_skills", {})
            for param, rating in traits.items():
                clean_param = param.replace("_", " ").title()
                badge_type = "good" if "good" in str(rating).lower() or "excellent" in str(rating).lower() else "poor" if "poor" in str(rating).lower() else "ok"
                
                st.markdown(
                    "<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; font-size: 0.85rem;'>"
                    f"<div style='font-weight: 500; color: {COLORS['text_main']};'>{clean_param}</div>"
                    f"<div style='display: flex; align-items: center; gap: 12px;'>"
                    f"<div>{get_badge_html(rating, badge_type)}</div>"
                    f"<div style='font-size: 0.6rem;'>{get_dots_html(badge_type)}</div>"
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown(f"<div style='background-color: {COLORS['bg_light']}; border: 1px solid {COLORS['border']}; padding: 12px; border-radius: 8px; font-size: 0.8rem; color: {COLORS['text_muted']}; margin-top: 20px; line-height: 1.5;'>{soft_skills.get('justification', 'N/A')}</div>", unsafe_allow_html=True)

    # ==========================================
    # ROW 3: Dimension Cards & Recommendations
    # ==========================================
    # col_cards, col_recs = st.columns([1.7, 1], gap="large")
    col_cards, spacer2, col_recs = st.columns([25, 1, 25])
    

    with col_cards:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 15px;'>DIMENSION GUIDELINES</div>", unsafe_allow_html=True)
            keys = list(compliance.keys())[:4] 
            
            # Using a pure HTML grid for the cards makes them look vastly superior and cohesive
            cards_html = f"<div style='display: grid; grid-template-columns: repeat({len(keys)}, 1fr); gap: 15px;'>"
            
            for idx, key in enumerate(keys):
                val = compliance[key]
                clean_name = key.split('_')[0].replace("_", " ").title() + (" " + key.split('_')[1].title() if len(key.split('_')) > 1 and not key.split('_')[1].isdigit() else "")
                achieved = val.get("weighted_contribution", 0)
                weight = float(str(val.get("weight", "0")).replace("%", ""))
                color = dim_colors[idx % len(dim_colors)]
                finding = val.get("finding", "No specific finding recorded.")
                
                cards_html += (
                    f"<div style='background: {COLORS['bg_light']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 12px;'>"
                    f"<div style='color: {color}; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 8px;'>{idx+1}. {clean_name}</div>"
                    f"<div style='font-size: 0.8rem; color: {COLORS['text_muted']}; height: 75px; overflow: hidden; margin-bottom: 12px; line-height: 1.4;'>{finding}</div>"
                    f"<div style='color: {COLORS['text_main']}; font-size: 0.75rem; font-weight: 600; padding-top: 8px; border-top: 1px solid {COLORS['border']};'>Score: {achieved} / {weight}</div>"
                    "</div>"
                )
            
            cards_html += "</div>"
            st.markdown(cards_html, unsafe_allow_html=True)

    with col_recs:
        with st.container(border=True):
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; color: {COLORS['text_muted']}; margin-bottom: 15px;'>PERFORMANCE RECOMMENDATION</div>", unsafe_allow_html=True)
            if total_score >= 80:
                rec_text = "Maintain current performance level. Outstanding adherence to emergency protocols and caller management."
                training = "Advanced Crisis Management"
                hours = "0.0 Hrs"
            elif total_score >= 60:
                rec_text = "Focus on improving Information Gathering and ensuring all critical details (like addresses) are confirmed twice."
                training = "Effective Info Gathering"
                hours = "2.0 Hrs"
            else:
                rec_text = "Immediate remediation required. Review standard operating procedures for emergency handling and managing unnecessary silence."
                training = "Mandatory Protocol Refresh"
                hours = "4.0 Hrs"
                
            # Rendered as a sleek blockquote-style alert
            st.markdown(
                f"<div style='border-left: 3px solid {COLORS['blue']}; padding-left: 15px; margin-top: 5px;'>"
                f"<div style='font-size: 0.85rem; color: {COLORS['text_main']}; line-height: 1.5; margin-bottom: 16px;'>{rec_text}</div>"
                "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>"
                "<div><div style='color: #64748b; font-size: 0.65rem; text-transform: uppercase; margin-bottom: 2px;'>Training</div><div style='font-size: 0.8rem; font-weight: 600;'>" f"{training}</div></div>"
                "<div><div style='color: #64748b; font-size: 0.65rem; text-transform: uppercase; margin-bottom: 2px;'>Time Assigned</div><div style='font-size: 0.8rem; font-weight: 600;'>" f"{hours}</div></div>"
                "<div><div style='color: #64748b; font-size: 0.65rem; text-transform: uppercase; margin-bottom: 2px;'>Target Date</div><div style='font-size: 0.8rem; font-weight: 600;'>" f"{(datetime.now() + timedelta(days=10)).strftime('%d-%m-%Y')}</div></div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )