# components/summary_view.py
"""
Generalized, schema-agnostic renderer for AI call-summary dicts.

Works for ANY incident_type (cyber fraud, medical emergency, domestic
violence, fire, etc.) because it never hardcodes field names like
"bank_name" or "account_number". Instead it buckets whatever keys are
present into semantic groups using pattern matching, then renders only
the groups that actually have data.

Pipeline:
    raw_llm_output -> parse_llm_summary() -> dict -> render_summary_tab(dict)
"""

import json
import re
import streamlit as st


# ---------------------------------------------------------------------------
# 1. FIELD CLASSIFICATION CONFIG
#    Each bucket = (bucket_key, display_title, icon, accent_color, key_patterns)
#    key_patterns are regexes matched against the snake_case field name.
#    Order matters: first match wins. Anything unmatched -> "other".
# ---------------------------------------------------------------------------
BUCKETS = [
    {
        "key": "overview",
        "title": "Incident Overview",
        "icon": "🧾",
        "color": "#DC2626",
        "bg": "#FEF2F2",
        # concept keywords (single tokens) — matched against each key's
        # split words, e.g. "previous_phone_number" -> {previous, phone, number}
        "keywords": {
            "incident", "type", "subtype", "category", "severity", "priority",
            "urgency", "caller", "name", "location", "address", "district",
            "state", "police", "station", "thana", "phone", "mobile", "contact",
        },
    },
    {
        "key": "financial",
        "title": "Financial Information",
        "icon": "💰",
        "color": "#16A34A",
        "bg": "#F0FDF4",
        "keywords": {
            "bank", "account", "amount", "transaction", "payment", "balance",
            "upi", "card", "loan", "currency", "rupee", "rupees", "inr", "fund",
            "funds", "transfer", "transferred", "credit", "debit", "sum",
        },
    },
    {
        "key": "medical",
        "title": "Medical Information",
        "icon": "🩺",
        "color": "#0891B2",
        "bg": "#ECFEFF",
        "keywords": {
            "patient", "injury", "injuries", "symptom", "symptoms", "medical",
            "hospital", "ambulance", "vital", "vitals", "condition", "health",
        },
    },
    {
        "key": "key_facts",
        "title": "Key Facts",
        "icon": "📌",
        "color": "#2563EB",
        "bg": "#EFF6FF",
        "keywords": {"facts", "fact", "observations", "observation", "highlights"},
    },
    {
        "key": "actions",
        "title": "Dispatcher / Operator Actions",
        "icon": "🛠️",
        "color": "#D97706",
        "bg": "#FFFBEB",
        "keywords": {"dispatcher", "operator", "action", "actions", "step", "steps", "response"},
    },
    {
        "key": "entities",
        "title": "Important Entities",
        "icon": "🔎",
        "color": "#7C3AED",
        "bg": "#F5F3FF",
        "keywords": {"entities", "entity"},
    },
    {
        "key": "summary",
        "title": "Final Summary",
        "icon": "📄",
        "color": "#1D4ED8",
        "bg": "#EFF6FF",
        "keywords": {"summary", "narrative", "overview_text", "conclusion"},
    },
]

# Concept keywords used to find "the severity field" and "the incident type
# field" for the banner, regardless of what the LLM actually named them.
SEVERITY_ALIASES = {"severity", "priority", "priority_level", "urgency"}
INCIDENT_TYPE_ALIASES = {"incident_type", "type", "category", "incident_category"}

# Fields we deliberately never show as raw rows (already handled specially)
HIDDEN_KEYS = {"call_id", "audio_file"}

SEVERITY_STYLES = {
    "high": {"bg": "#FEF2F2", "border": "#DC2626", "text": "#DC2626", "label": "HIGH"},
    "medium": {"bg": "#FFFBEB", "border": "#D97706", "text": "#D97706", "label": "MEDIUM"},
    "low": {"bg": "#F0FDF4", "border": "#16A34A", "text": "#16A34A", "label": "LOW"},
}


def _humanize(key: str) -> str:
    """snake_case / camelCase -> Title Case label."""
    key = re.sub(r"_inr$", " (INR)", key, flags=re.IGNORECASE)
    key = key.replace("_", " ")
    key = re.sub(r"(?<!^)(?=[A-Z])", " ", key)  # camelCase split
    return key.strip().title()


def _tokenize(key: str) -> set:
    """
    Split a field name into lowercase concept words.
    'previous_phone_number' -> {'previous', 'phone', 'number'}
    'accountStatus'         -> {'account', 'status'}
    """
    spaced = re.sub(r"(?<!^)(?=[A-Z])", "_", key)  # camelCase -> snake_case
    tokens = re.split(r"[_\-\s]+", spaced.lower())
    return {t for t in tokens if t}


def _classify(data: dict) -> dict:
    """
    Bucket every key in `data` by concept-word overlap with each bucket's
    keyword set — NOT by exact key name. This means new/renamed fields the
    LLM invents (e.g. 'caller_mobile', 'sum_involved', 'priority_level')
    still land in the right card as long as they share a recognizable word,
    with zero need to special-case every possible key name.
    """
    buckets = {b["key"]: {} for b in BUCKETS}
    other = {}

    for k, v in data.items():
        if k in HIDDEN_KEYS or v in (None, "", [], {}):
            continue
        tokens = _tokenize(k)
        placed = False
        for b in BUCKETS:
            if tokens & b["keywords"]:
                buckets[b["key"]][k] = v
                placed = True
                break
        if not placed:
            other[k] = v

    return buckets, other


def _find_field_by_alias(data: dict, aliases: set):
    """
    Find a field's value by matching its key's tokens against a concept
    alias set (used for severity / incident_type), instead of requiring
    the exact key name. Returns (key, value) of the first match, or (None, None).
    """
    for k, v in data.items():
        if v in (None, "", [], {}):
            continue
        if _tokenize(k) & aliases:
            return k, v
    return None, None


def _render_field_grid(fields: dict, cols_per_row: int = 3):
    """
    Render a dict of scalar fields as a responsive label/value grid.

    IMPORTANT: every fragment here is built as a single-line string with
    zero embedded newlines or leading whitespace. Multi-line indented
    f-strings look nicer in source code, but the leading whitespace from
    Python's own indentation becomes literal content in the string —
    Streamlit's markdown parser can then misinterpret part of that content
    as an indented code block instead of raw HTML, causing tags to render
    as visible text with a horizontal-scrolling monospace block. Flat,
    single-line HTML avoids that failure mode entirely.
    """
    scalar_fields = {k: v for k, v in fields.items() if not isinstance(v, (list, dict))}
    if not scalar_fields:
        return

    items = list(scalar_fields.items())
    row_blocks = []

    for i in range(0, len(items), cols_per_row):
        row_items = items[i:i + cols_per_row]
        cell_blocks = []
        for k, v in row_items:
            label = _humanize(k)
            cell_html = (
                '<div>'
                f'<div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.03em;margin-bottom:2px;">{label}</div>'
                f'<div style="font-size:13.5px;color:#0F172A;font-weight:600;">{v}</div>'
                '</div>'
            )
            cell_blocks.append(cell_html)

        row_html = (
            f'<div style="display:grid;grid-template-columns:repeat({len(row_items)},1fr);gap:14px;margin-bottom:12px;">'
            + "".join(cell_blocks)
            + '</div>'
        )
        row_blocks.append(row_html)

    st.markdown("".join(row_blocks), unsafe_allow_html=True)


def _render_list_field(label: str, items: list, dot_color: str = "#3B82F6"):
    li_blocks = [
        f'<li style="margin-bottom:6px;font-size:12.5px;color:#334155;line-height:1.5;">'
        f'<span style="color:{dot_color};margin-right:6px;">●</span>{item}</li>'
        for item in items
    ]
    html = '<ul style="list-style:none;padding:0;margin:0;">' + "".join(li_blocks) + '</ul>'
    st.markdown(html, unsafe_allow_html=True)


def _card_open(title: str, icon: str, color: str, bg: str):
    html = (
        f'<div class="custom-card" style="padding:16px;border-left:4px solid {color};background:{bg};margin-bottom:16px;">'
        f'<h4 style="margin:0 0 12px 0;font-size:13.5px;color:{color};font-weight:700;">{icon}&nbsp; {title}</h4>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def _render_bucket(bucket_cfg: dict, fields: dict):
    if not fields:
        return
    _card_open(bucket_cfg["title"], bucket_cfg["icon"], bucket_cfg["color"], bucket_cfg["bg"])

    list_fields = {k: v for k, v in fields.items() if isinstance(v, list)}
    scalar_fields = {k: v for k, v in fields.items() if not isinstance(v, (list, dict))}

    if scalar_fields:
        _render_field_grid(scalar_fields)

    for k, v in list_fields.items():
        if len(list_fields) > 1:
            st.markdown(
                f"""<div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;margin:8px 0 4px 0;">{_humanize(k)}</div>""",
                unsafe_allow_html=True,
            )
        _render_list_field(k, v, dot_color=bucket_cfg["color"])

    _card_close()


def _render_severity_banner(severity_value: str, incident_type: str = ""):
    if not severity_value:
        return
    style = SEVERITY_STYLES.get(str(severity_value).strip().lower(), SEVERITY_STYLES["medium"])
    note = f"{incident_type} cases at this severity level may require timely investigation and follow-up." if incident_type else "This case may require timely investigation and follow-up."
    html = (
        f'<div style="background:{style["bg"]};border-left:4px solid {style["border"]};border-radius:6px;padding:12px 16px;margin-top:8px;">'
        f'<div style="color:{style["text"]};font-weight:700;font-size:13px;">⚠️ Severity: {style["label"]}</div>'
        f'<div style="color:#475569;font-size:12px;margin-top:2px;">{note}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _coerce_summary_to_dict(summary_field) -> dict:
    """
    Handles the case where `summary` from your FastAPI backend is a raw
    string (plain text, or a JSON string possibly wrapped in ```json fences)
    instead of an already-parsed dict.
    """
    if isinstance(summary_field, dict):
        return summary_field

    if not summary_field or not isinstance(summary_field, str):
        return {}

    text = summary_field.strip()

    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    if not text.startswith("{"):
        first_brace, last_brace = text.find("{"), text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Not JSON at all — plain prose summary from backend.
        # Fall back to just showing it as the final_summary field.
        return {"final_summary": summary_field.strip()}


def render_call_summary(payload: dict):
    """
    Entry point for views/new_call_analysis.py.

    Pass in the whole st.session_state.analysis_data payload
    (call_id, audio_file, transcript, summary) — this handles unwrapping
    `summary` (str or dict) and merging in call_id/audio_file, then
    delegates to render_summary_tab().
    """
    summary_dict = _coerce_summary_to_dict(payload.get("summary"))
    summary_dict["call_id"] = payload.get("call_id")
    summary_dict["audio_file"] = payload.get("audio_file")
    render_summary_tab(summary_dict)


def render_summary_tab(data: dict):
    """
    Main entry point. Pass in the cleaned dict from parse_llm_summary().
    Renders a card-based layout matching the design shown in the app,
    but adapts automatically to whatever fields exist for this incident_type.
    """
    if not data:
        st.warning("No summary data available for this call.")
        return

    # Optional metadata strip (call_id / audio_file), only if present
    if data.get("call_id") or data.get("audio_file"):
        html = (
            '<div class="custom-card" style="margin-bottom:16px;padding:12px 16px;">'
            '<p style="margin:0 0 6px 0;font-size:13px;font-weight:600;color:#12355B;">Call Identity Metadata</p>'
            '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12px;color:#475569;">'
            f'<div><strong>Call ID:</strong> {data.get("call_id", "N/A")}</div>'
            f'<div><strong>Audio Target:</strong> {data.get("audio_file", "N/A")}</div>'
            '<div><strong>Pipeline Status:</strong> <span style="color:#16A34A;font-weight:600;">COMPLETED</span></div>'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    buckets, other = _classify(data)

    # Render primary buckets two-per-row where sensible (overview/financial/medical
    # pair naturally; key_facts/actions pair naturally; entities/summary pair naturally)
    pair_layout = [
        ["overview", "financial"],
        ["medical"],
        ["key_facts", "actions"],
        ["entities", "summary"],
    ]

    bucket_by_key = {b["key"]: b for b in BUCKETS}

    for row_keys in pair_layout:
        active = [k for k in row_keys if buckets.get(k)]
        if not active:
            continue
        cols = st.columns(len(active)) if len(active) > 1 else [st.container()]
        for col, bkey in zip(cols, active):
            with col:
                _render_bucket(bucket_by_key[bkey], buckets[bkey])

    # Anything that didn't match a known pattern still gets shown
    if other:
        _card_open("Additional Details", "🗂️", "#475569", "#F8FAFC")
        _render_field_grid(other)
        _card_close()

    # Severity banner at the bottom — found by concept, not exact key name,
    # so it still works if the LLM calls it "priority_level" or "urgency"
    _, severity = _find_field_by_alias(data, SEVERITY_ALIASES)
    _, incident_type = _find_field_by_alias(data, INCIDENT_TYPE_ALIASES)
    if severity:
        _render_severity_banner(severity, incident_type or "")