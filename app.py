# app.py
#
# EcoTrack AI – Entry point
#
# This is the ONLY file you run:  streamlit run app.py
#
# What it does:
#   1. Sets the Streamlit page configuration (title, icon, layout)
#   2. Renders the sidebar with project information and credential status
#   3. Creates five tabs and calls the matching page module for each tab
#
# Each tab is a separate Python module inside the pages/ folder.
# This keeps app.py short and easy to read.

import streamlit as st

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION  –  must be the first Streamlit call in the script
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EcoTrack AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# IMPORTS – page modules (one per tab)
# ---------------------------------------------------------------------------

from pages.waste_classifier   import render as render_classifier   # noqa: E402
from pages.csv_analytics      import render as render_analytics    # noqa: E402
from pages.ai_assistant       import render as render_assistant    # noqa: E402
from pages.impact_calculator  import render as render_calculator   # noqa: E402
from pages.responsible_ai     import render as render_responsible  # noqa: E402

# Import the status helpers from the client so the sidebar can show
# whether credentials are configured, without making any API calls
from utils.watsonx_client import is_text_ai_available, is_vision_ai_available  # noqa: E402

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("♻️ EcoTrack AI")
    st.caption("AI-Powered Campus Waste & Sustainability Assistant")
    st.divider()

    st.markdown("**Project**")
    st.markdown(
        "1M1B AI for Sustainability Virtual Internship  \n"
        "IBM SkillsBuild × AICTE  \n"
        "**SDG 12** – Responsible Consumption and Production"
    )
    st.divider()

    # Show live credential status so students can see what is configured
    st.markdown("**AI Service Status**")

    if is_text_ai_available():
        st.success("✅ Text AI (Granite) – configured")
    else:
        st.warning("⚠️ Text AI – not configured  \n_Add credentials to `.env`_")

    if is_vision_ai_available():
        st.success("✅ Vision AI (Granite Vision) – configured")
    else:
        st.info(
            "ℹ️ Vision AI – not configured  \n"
            "_Tab 1 will use Demo Mode_  \n"
            "_(Requires deploy-on-demand endpoint)_"
        )

    st.divider()
    st.caption(
        "Built with IBM watsonx.ai (Granite) · Streamlit · Pandas · Plotly  \n"
        "Powered by IBM Bob"
    )

# ---------------------------------------------------------------------------
# MAIN CONTENT – Tab navigation
# ---------------------------------------------------------------------------

st.markdown("## ♻️ EcoTrack AI — Campus Sustainability Assistant")
st.caption(
    "Helping campus communities reduce waste, understand recycling, and track "
    "sustainability progress. | SDG 12 – Responsible Consumption and Production"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📷 Waste Analyzer",
    "📊 Analytics Dashboard",
    "🤖 AI Assistant",
    "🌱 Impact Calculator",
    "⚖️ Responsible AI",
])

with tab1:
    render_classifier()

with tab2:
    render_analytics()

with tab3:
    render_assistant()

with tab4:
    render_calculator()

with tab5:
    render_responsible()
