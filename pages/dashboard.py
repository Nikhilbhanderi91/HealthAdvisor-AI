import streamlit as st
import os
import pandas as pd
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Health Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: linear-gradient(135deg, #f5f3e6 0%, #e4dec2 100%) !important;
    }
    
    /* Hide Streamlit default sidebar and header elements */
    [data-testid="stSidebar"] {
        display: none;
    }
    header {
        visibility: hidden;
    }
    
    /* Custom button overrides */
    .stButton>button {
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%) !important;
        color: #f5f3e6 !important;
        border-radius: 16px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(156, 166, 131, 0.25) !important;
        transition: all 0.3s ease !important;
        height: auto !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(156, 166, 131, 0.35) !important;
    }
    
    .stSelectbox label {
        color: #4a4e3b !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Metric & Card Components */
    .metric-card {
        background: rgba(245, 243, 230, 0.85);
        backdrop-filter: blur(12px);
        padding: 25px 20px;
        border-radius: 20px;
        border: 1px solid rgba(213, 198, 141, 0.4);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(156, 166, 131, 0.08);
    }
    .metric-value {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 15px;
        color: #606450;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Section Headers */
    .section-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .section-header h1 {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #4a4e3b 0%, #9ca683 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .section-header h2 {
        font-size: 32px;
        font-weight: 800;
        color: #4a4e3b;
        margin-bottom: 10px;
    }
    .section-header p {
        color: #606450;
        font-size: 17px;
    }
    
    /* Global Navigation Bar */
    .navbar {
        background: rgba(245, 243, 230, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 16px 40px;
        border-radius: 20px;
        border: 1px solid rgba(213, 198, 141, 0.4);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.06);
        margin-bottom: 35px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .navbar-logo {
        font-size: 26px;
        font-weight: 800;
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .info-card {
        background: rgba(245, 243, 230, 0.75);
        backdrop-filter: blur(8px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(213, 198, 141, 0.3);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.04);
        transition: all 0.3s ease;
    }
    .info-card:hover {
        background: rgba(245, 243, 230, 0.9);
        box-shadow: 0 12px 30px rgba(156, 166, 131, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Navbar
st.markdown(
    """
    <div class="navbar">
        <div class="navbar-logo">
            🏥 Health Advisor AI
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([6, 1])
with col1:
    language = st.selectbox("🌐 Select Language", ["English", "Gujarati"])
with col2:
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

st.markdown("---")
st.markdown("""
    <div class='section-header'>
        <h1>📊 Health Dashboard</h1>
        <p>Complete overview of your medical report analysis</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

def t(text):
    try:
        if language == "Gujarati":
            return GoogleTranslator(source='auto', target='gu').translate(text)
        return text
    except:
        return text

# Check if we have data
if "results" not in st.session_state or not st.session_state.get("analysis_done", False):
    st.warning("⚠️ " + t("Please analyze a medical report first!"))
    st.markdown("---")
    st.page_link("pages/analyzer.py", label="🔙 " + t("Back to Report Analyzer"), use_container_width=True)
    st.stop()

results = st.session_state.get("results", [])
info = st.session_state.get("info", {})

# Calculate metrics
total_params = len(results)
normal_params = len([r for r in results if r["status"] == "NORMAL"])
abnormal_params = total_params - normal_params
high_params = len([r for r in results if "HIGH" in r["status"]])
low_params = len([r for r in results if "LOW" in r["status"]])

st.markdown("""
    <div class='section-header'>
        <h2>📌 Quick Overview</h2>
    </div>
""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{total_params}</div>
            <div class="metric-label">{t('Total Parameters')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{normal_params}</div>
            <div class="metric-label">{t('Normal')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{low_params}</div>
            <div class="metric-label">{t('Low')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{high_params}</div>
            <div class="metric-label">{t('High')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Patient Info Section
st.markdown("""
    <div class='section-header'>
        <h2>👤 Patient Information</h2>
    </div>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 32px; margin-bottom: 8px;">👤</div>
            <div style="font-size: 18px; font-weight: 700; color: #1f2937;">{t('Name')}</div>
            <div style="font-size: 20px; font-weight: 600; color: #4f46e5; margin-top: 8px;">{info.get('name', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 32px; margin-bottom: 8px;">🎂</div>
            <div style="font-size: 18px; font-weight: 700; color: #1f2937;">{t('Age')}</div>
            <div style="font-size: 20px; font-weight: 600; color: #4f46e5; margin-top: 8px;">{info.get('age', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 32px; margin-bottom: 8px;">📅</div>
            <div style="font-size: 18px; font-weight: 700; color: #1f2937;">{t('Date')}</div>
            <div style="font-size: 20px; font-weight: 600; color: #4f46e5; margin-top: 8px;">{info.get('date', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Results Table Section
st.markdown("""
    <div class='section-header'>
        <h2>📊 Medical Parameters</h2>
    </div>
""", unsafe_allow_html=True)
if results:
    df = pd.DataFrame([{
        t("Parameter"): t(r["parameter"]),
        t("Value"): f"{r['value']} {r['unit']}",
        t("Normal Range"): f"{r['low']} - {r['high']}",
        t("Status"): t(r["status"])
    } for r in results])
    
    # Style the dataframe
    def color_status(val):
        if "HIGH" in val or "ઊંચો" in val:
            return 'background-color: #fee2e2; color: #991b1b'
        elif "LOW" in val or "ઓછું" in val:
            return 'background-color: #fef3c7; color: #92400e'
        else:
            return 'background-color: #d1fae5; color: #065f46'
    
    st.dataframe(df.style.applymap(color_status, subset=[t("Status")]), width=1000)
else:
    st.warning(t("No parameters detected"))

st.markdown("---")

# Navigation Buttons
st.markdown("""
    <div class='section-header'>
        <h2>🔗 Quick Actions</h2>
    </div>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/analyzer.py", label="🔙 " + t("Back to Report Analyzer"), use_container_width=True)
with col2:
    st.page_link("pages/chatbot.py", label="💬 " + t("Open Health Assistant"), use_container_width=True)

st.markdown("---")
