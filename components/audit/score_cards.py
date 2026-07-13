import streamlit as st


def render_pillar_card(title, score, max_score, weight, details, critical_gaps=None):
    """
    Renders one QA pillar card (Protocol Adherence, Information Gathering, etc).

    Built as fully flat, single-line HTML fragments joined with plain string
    concatenation — no multi-line indented f-strings. The previous version
    used a multi-line indented f-string with an embedded {gaps_html} block,
    which is exactly the pattern that causes Streamlit's markdown parser to
    misinterpret part of the HTML as an indented code block instead of
    rendering it — showing raw <div>/<span> tag text with a horizontal
    scrollbar (monospace, non-wrapping) instead of a styled card.
    """
    gap_items_html = ""
    if critical_gaps:
        li_blocks = "".join(f"<li>{gap}</li>" for gap in critical_gaps)
        gap_items_html = (
            "<div style='margin-top: auto; padding-top: 10px;'>"
            "<strong style='color:#DC2626; font-size:12px;'>Critical Gaps:</strong>"
            f"<ul style='margin: 4px 0 0 0; padding-left: 16px; color:#475569; font-size:12px;'>{li_blocks}</ul>"
            "</div>"
        )

    html = (
        '<div class="custom-card" style="min-height: 290px; justify-content: flex-start;">'
        '<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
        f'<h4 style="margin: 0; font-size: 16px; color: #1E293B; font-weight: 600;">{title}</h4>'
        '</div>'
        f'<span style="color: #64748B; font-size: 12px; margin-bottom: 12px;">(weight {weight}pts)</span>'
        '<div style="margin: 8px 0 12px 0;">'
        f'<span style="font-size: 24px; font-weight: 700; color: #0F172A;">{score}</span>'
        f'<span style="color: #64748B; font-size: 14px;"> / {max_score}</span>'
        '</div>'
        f'<p style="font-size: 13px; color: #475569; margin: 0; line-height: 1.5;">{details}</p>'
        + gap_items_html +
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)