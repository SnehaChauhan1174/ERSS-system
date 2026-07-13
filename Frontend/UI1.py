import streamlit as st

# Import the navigation bar and the page files
from UI2nav import render_topbar
import UI3home
import UI4calls
import UI5reports
import UI9batchaudit

# 1. Page Configuration
st.set_page_config(
    page_title="ERSS App", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Render Topbar Navigation
selected_page = render_topbar()

# 3. Page Routing
if selected_page == "Home":
    UI3home.show()
    
elif selected_page == "Call Analysis":
    UI4calls.show()
    
elif selected_page == "Reports":
    UI5reports.show()

elif selected_page == "Audit":
    UI9batchaudit.show()