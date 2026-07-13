import streamlit as st
from UI6translation import TEXT
from UI7utils import get_formatted_datetime  # Import your new helper function

def render_topbar():
    # Initialize session states
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'lang' not in st.session_state:
        st.session_state.lang = "en" # Default to English

    # Load current language dictionary
    lang = st.session_state.lang
    t = TEXT[lang]

    st.markdown("""
        <style>
            header { visibility: hidden; }
            [data-testid="collapsedControl"] { display: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            
            /* Increased top padding slightly so the new title doesn't hug the very edge of the screen */
            .block-container { padding-top: 1rem !important; } 

            /* Styling for the new brand title at the very top */
            .brand-title {
                font-size: 1.8rem;
                font-weight: 400; /* Changed from 800 (heavy bold) to 400 (normal/sleek) */
                color: #555555; /* Changed from #111111 (black) to a sleek dark grey */
                margin-bottom: -0.5rem; 
                letter-spacing: -0.5px;
            }

            div[data-testid="stHorizontalBlock"] {
                background-color: #ffffff;
                padding: 0;
                gap: 0; 
                margin-bottom: 2rem;
                border-bottom: 1px solid #f0f0f0;
                align-items: center; 
            }

            /* INCREASED SIZES FOR BUTTONS */
            div[data-testid="stHorizontalBlock"] button {
                width: 100% !important;
                border-radius: 0px !important; 
                border: none !important;
                background-color: transparent !important;
                font-size: 1.25rem !important; /* Increased from 1.1rem */
                font-weight: 600 !important;
                padding: 1.4rem 0rem !important; /* Increased vertical padding to make the bar taller */
                box-shadow: none !important;
                transition: all 0.2s ease-in-out;
            }
            
            div[data-testid="stHorizontalBlock"] button:hover {
                color: #000000 !important;
                background-color: rgba(0, 0, 0, 0.03) !important;
            }

            div[data-testid="stHorizontalBlock"] button[kind="primary"] {
                border-bottom: 4px solid #ffe600 !important;
                color: #111111 !important;
            }

            div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
                border-bottom: 4px solid transparent !important;
                color: #888888 !important;
            }
            
            /* INCREASED SIZES FOR DATE/TIME */
            .datetime-display {
                color: #666666;
                font-size: 1.05rem; /* Increased from 0.95rem */
                font-weight: 500;
                text-align: right;
                padding-top: 0.4rem; /* Adjusted to keep it vertically centered with the larger buttons */
                padding-bottom: 1.2rem;
                padding-right: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # Render the Brand Title at the very top (Bilingual support included)
    brand_text = t.get("brand_title", "ERSS Transcript Solution -")
    st.markdown(f"<div class='brand-title'>{brand_text}</div>", unsafe_allow_html=True)

    # Dictionary linking the internal routing name to the translated display label
    pages = {
        "Home": t.get("nav_home", "Home"), 
        "Call Analysis": t.get("nav_analysis", "Call Analysis"), 
        "Reports": t.get("nav_reports", "Reports"),
        "Audit": t.get("nav_audit_page", "Audit") # <-- NEW TAB ADDED HERE
    }
    
    # 7 Columns now: 4 for buttons, 1 dynamic spacer, 1 for datetime, 1 for language dropdown
    cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.0, 4.0, 1.5]) 
    
    # Render Navigation Buttons
    for i, (page_key, page_label) in enumerate(pages.items()):
        with cols[i]:
            button_type = "primary" if st.session_state.current_page == page_key else "secondary"
            if st.button(page_label, key=f"nav_{page_key}", type=button_type, use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

    # Render Date and Time (Shifted to index 5)
    with cols[5]:
        current_dt = get_formatted_datetime(st.session_state.lang)
        st.markdown(f"<div class='datetime-display'>{current_dt}</div>", unsafe_allow_html=True)

    # Render Language Switcher (Shifted to index 6)
    with cols[6]:
        st.markdown("<div style='padding-top: 0.7rem; padding-right: 1rem;'>", unsafe_allow_html=True)
        
        lang_options = {"en": "English", "hi": "हिंदी"}
        current_index = list(lang_options.keys()).index(st.session_state.lang)
        
        selected_lang_label = st.selectbox(
            "Language",
            options=list(lang_options.values()),
            index=current_index,
            label_visibility="collapsed",
            key="lang_selector"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        new_lang_key = [k for k, v in lang_options.items() if v == selected_lang_label][0]
        if new_lang_key != st.session_state.lang:
            st.session_state.lang = new_lang_key
            st.rerun()
                
    return st.session_state.current_page