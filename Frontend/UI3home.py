import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import pandas as pd
import plotly.express as px
from UI6translation import TEXT
from UI8audio import render_audio_player # Import your new reusable widget

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            ext = os.path.splitext(image_path)[1][1:].lower()
            if ext == "jpg": ext = "jpeg"
            mime_type = f"image/{ext}"
            encoded_string = base64.b64encode(img_file.read()).decode()
            return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        return ""

def show():
    # Fetch the current language from session state
    lang = st.session_state.get('lang', 'en')
    t = TEXT[lang]

    # st.title(t.get("home_title", "ERSS AI Operations"))
    # st.markdown(t.get("home_subtitle", "View Overall Performance"))
    # st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. Top Section: Split Carousel (Left), Spacer, and Audio Tool (Right)
    # ---------------------------------------------------------
    # We use a 3-column layout here. The middle column 'spacer_top' is left empty to create distance.
    top_left, spacer_top, top_right = st.columns([12, 1, 10]) 

    with top_left:
        img1_b64 = get_base64_image("assets/image1.jpg") 
        img2_b64 = get_base64_image("assets/image2.jpg")
        img3_b64 = get_base64_image("assets/image3.jpg")

        # Carousel HTML
        carousel_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <style>
                .carousel-caption {{ background: rgba(0, 0, 0, 0.6); border-radius: 10px; padding: 1rem; bottom: 2rem; }}
                .carousel-item img {{ height: 360px; object-fit: cover; border-radius: 10px; }}
                .carousel-inner {{ border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
            </style>
        </head>
        <body>
        <div id="heroCarousel" class="carousel slide" data-bs-ride="carousel" data-bs-interval="4000">
          <div class="carousel-indicators">
            <button type="button" data-bs-target="#heroCarousel" data-bs-slide-to="0" class="active"></button>
            <button type="button" data-bs-target="#heroCarousel" data-bs-slide-to="1"></button>
            <button type="button" data-bs-target="#heroCarousel" data-bs-slide-to="2"></button>
          </div>
          <div class="carousel-inner">
            <div class="carousel-item active">
              <img src="{img1_b64}" class="d-block w-100" alt="Analysis">
              <div class="carousel-caption">
                <h5>{t.get('car_title_1', 'Real-Time Audio Analysis')}</h5>
                <p>{t.get('car_desc_1', 'Our AI processes emergency calls with sub-second latency.')}</p>
              </div>
            </div>
            <div class="carousel-item">
              <img src="{img2_b64}" class="d-block w-100" alt="Data">
              <div class="carousel-caption">
                <h5>{t.get('car_title_2', 'Automated Auditing')}</h5>
                <p>{t.get('car_desc_2', 'Ensure 100% protocol compliance across all dispatchers automatically.')}</p>
              </div>
            </div>
            <div class="carousel-item">
              <img src="{img3_b64}" class="d-block w-100" alt="Reporting">
              <div class="carousel-caption">
                <h5>{t.get('car_title_3', 'Comprehensive Reports')}</h5>
                <p>{t.get('car_desc_3', 'Generate actionable insights from weekly and monthly call volume data.')}</p>
              </div>
            </div>
          </div>
          <button class="carousel-control-prev" type="button" data-bs-target="#heroCarousel" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button class="carousel-control-next" type="button" data-bs-target="#heroCarousel" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
        </div>
        </body>
        </html>
        """
        components.html(carousel_html, height=380)

    with top_right:
        render_audio_player(t)


    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 2. Metric Boxes Layer (Bilingual)
    # ---------------------------------------------------------
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        with st.container(border=True):
            st.metric(label=t.get('metric_1_title', "Total Calls (This Week)"), value="45,230", delta=t.get('metric_1_delta', "5.2% vs last week"))
            
    with col_m2:
        with st.container(border=True):
            st.metric(label=t.get('metric_2_title', "Avg. Compliance Score"), value="88.4 / 100", delta=t.get('metric_2_delta', "1.2% improvement"))
            
    with col_m3:
        with st.container(border=True):
            st.metric(label=t.get('metric_3_title', "High Severity Calls"), value="18.5%", delta=t.get('metric_3_delta', "-2.1%"), delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 3. Bar Graphs Layer (Bilingual + Fixed Graph 2)
    # ---------------------------------------------------------
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        cat_labels = [
            t.get('cat_police', 'Police (112)'), t.get('cat_medical', 'Medical (108)'), 
            t.get('cat_traffic', 'Traffic'), t.get('cat_fire', 'Fire (101)'), 
            t.get('cat_women', 'Women Helpline (1090)'), t.get('cat_other', 'Other')
        ]
        
        df_categories = pd.DataFrame({
            t.get('graph_1_x', "Category"): cat_labels,
            t.get('graph_1_y', "Call Volume"): [18200, 14500, 5200, 4100, 2300, 930]
        })
        fig_bar = px.bar(
            df_categories, x=t.get('graph_1_x', "Category"), y=t.get('graph_1_y', "Call Volume"), 
            title=t.get('graph_1_title', "Calls per Category (Past Week)"), color_discrete_sequence=["#2A3F54"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        agent_prefix = t.get('agent_prefix', 'Agent')
        call_takers = [f"{agent_prefix} {i+1}" for i in range(20)]
        kpi_scores = [82, 85, 88, 91, 95, 78, 89, 92, 87, 84, 96, 79, 88, 90, 83, 86, 94, 81, 85, 89]
        
        df_kpi = pd.DataFrame({
            t.get('graph_2_x', "Call Taker"): call_takers,
            t.get('graph_2_y', "Score (out of 100)"): kpi_scores
        })
        
        fig_kpi_bar = px.bar(
            df_kpi, x=t.get('graph_2_x', "Call Taker"), y=t.get('graph_2_y', "Score (out of 100)"), 
            title=t.get('graph_2_title', "KPI Compliance by Call Taker"), color_discrete_sequence=["#1ABB9C"]
        )
        fig_kpi_bar.update_yaxes(range=[0, 100])
        fig_kpi_bar.update_xaxes(tickangle=-45, tickmode='linear') 
        st.plotly_chart(fig_kpi_bar, use_container_width=True)

    # ---------------------------------------------------------
    # 4. Pie Chart & Area Graph Layer (Bilingual)
    # ---------------------------------------------------------
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        sev_labels = [t.get('sev_low', 'Low'), t.get('sev_med', 'Medium'), t.get('sev_high', 'High')]
        df_severity = pd.DataFrame({
            t.get('graph_3_cat', "Severity"): sev_labels, 
            t.get('graph_3_val', "Percentage"): [45.0, 36.5, 18.5]
        })
        fig_pie = px.pie(
            df_severity, names=t.get('graph_3_cat', "Severity"), values=t.get('graph_3_val', "Percentage"), 
            title=t.get('graph_3_title', "Call Severity Breakdown"), hole=0.4, color=t.get('graph_3_cat', "Severity"),
            color_discrete_map={
                t.get('sev_low', 'Low'): "#2ca02c", t.get('sev_med', 'Medium'): "#ff7f0e", t.get('sev_high', 'High'): "#d62728"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g4:
        hours = list(range(24))
        trend_scores = [92, 93, 93, 94, 95, 94, 91, 88, 85, 83, 82, 84, 86, 85, 84, 87, 89, 88, 86, 88, 90, 91, 92, 92]
        x_label = t.get('graph_4_x', "Hour of Day")
        y_label = t.get('graph_4_y', "Compliance Score")
        
        df_trend = pd.DataFrame({x_label: hours, y_label: trend_scores})
        
        fig_area = px.area(
            df_trend, x=x_label, y=y_label, title=t.get('graph_4_title', "Today's Hourly Compliance Trend"), 
            markers=True, color_discrete_sequence=["#9B59B6"] 
        )
        fig_area.update_yaxes(range=[75, 100])
        fig_area.update_xaxes(tickmode='linear', tick0=0, dtick=3) 
        st.plotly_chart(fig_area, use_container_width=True)