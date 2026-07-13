import streamlit as st
from pathlib import Path
from streamlit_option_menu import option_menu

BASE_DIR = Path(__file__).parent.parent
LOGO = BASE_DIR / "assets" / "erss_logo.png"


def render_sidebar():
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=90)

        st.markdown(
            "<div class='menu-title'>ERSS</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='menu-subtitle'>Emergency Response Support System</div>",
            unsafe_allow_html=True
        )

        page = option_menu(
            menu_title=None,
            
            options=[
                "Dashboard",
                "New Call Analysis",
                "Audit Reports",
                "Analytics"
            ],

            icons=[
                "grid-fill",
                "telephone-fill",
                "clipboard2-check-fill",
                "bar-chart-fill"
            ],

            default_index=0,

            styles={

                "container":{

                    "padding":"0",

                    "background-color":"white"

                },

                "icon":{

                    "color":"#2563EB",

                    "font-size":"18px"

                },

                "nav-link":{

                    "font-size":"16px",

                    "color":"#374151",

                    "padding":"12px",

                    "border-radius":"12px",

                    "--hover-color":"#EEF4FF"

                },

                "nav-link-selected":{

                    "background-color":"#2563EB",

                    "color":"white"

                }

            }

        )

    return page

# from pathlib import Path
# import streamlit as st

# BASE_DIR = Path(__file__).resolve().parent.parent
# LOGO = BASE_DIR / "assets" / "erss_logo.png"

# st.write("BASE_DIR:", BASE_DIR)
# st.write("LOGO:", LOGO)
# st.write("Exists:", LOGO.exists())

# if LOGO.exists():
#     st.image(str(LOGO), width=90)
# else:
#     st.error("Logo not found!")