import streamlit as st
import os
import pandas as pd
from health_backend import run_analysis
from PIL import Image

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

import certifi
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

from deep_translator import GoogleTranslator

def translate_to_gujarati(text):
    try:
        if not text or text.strip() == "":
            return text
        return GoogleTranslator(source='auto', target='gu').translate(text)
    except:
        return text

def translate_bulk(text_list):
    try:
        full_text = "\n".join(text_list)
        translated = GoogleTranslator(source='auto', target='gu').translate(full_text)
        return translated.split("\n")
    except:
        return text_list


def translate_text(text):
    try:
        if language == "Gujarati":
            return GoogleTranslator(source='auto', target='gu').translate(str(text))
        return text
    except:
        return text


def t(text):
    if language == "Gujarati":
        return translate_to_gujarati(text)
    return text


def render_ai_html(content):
    if not content:
        return
    content = str(content)
    content = content.replace("```html", "")
    content = content.replace("```HTML", "")
    content = content.replace("```", "")
    content = content.strip()
    st.markdown(content, unsafe_allow_html=True)

favicon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "health-report.png")
try:
    favicon = Image.open(favicon_path)
except Exception:
    favicon = "🏥"

st.set_page_config(page_title="Health Advisor AI", page_icon=favicon, layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: linear-gradient(135deg, #f5f3e6 0%, #e4dec2 100%) !important;
    }
    
    /* Ensure high contrast dark text on headings, labels, paragraphs and list elements */
    h1, h2, h3, h4, h5, h6, label, p, li, th, td, [data-testid="stWidgetLabel"] p, .stMarkdown p {
        color: #1a1d13 !important;
    }
    
    /* Hide Streamlit default sidebar and header elements */
    [data-testid="stSidebar"] {
        display: none;
    }
    header {
        visibility: hidden;
    }
    
    /* Main wrapper container */
    .main-app-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 35px;
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 28px;
        border: 1px solid rgba(213, 198, 141, 0.35);
        box-shadow: 0 20px 50px rgba(156, 166, 131, 0.08);
        margin-bottom: 50px;
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
    
    .stFileUploader label, .stSelectbox label {
        color: #1a1d13 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Feature & Tip Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(213, 198, 141, 0.4);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.05);
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.75);
        box-shadow: 0 15px 35px rgba(156, 166, 131, 0.12);
        border-color: rgba(156, 166, 131, 0.4);
    }
    .feature-icon {
        font-size: 56px;
        margin-bottom: 16px;
        display: inline-block;
    }
    
    /* Metric & Overview Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.65);
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
        color: #1a1d13;
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
        color: #1a1d13;
        margin-bottom: 10px;
    }
    .section-header p {
        color: #2b2e22;
        font-size: 17px;
    }
    
    /* Global Navigation Bar */
    .navbar {
        background: rgba(255, 255, 255, 0.65);
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
    .navbar-links {
        display: flex;
        gap: 25px;
        align-items: center;
    }
    
    .info-card {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(8px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(213, 198, 141, 0.3);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.04);
        transition: all 0.3s ease;
        text-align: center;
    }
    .info-card:hover {
        background: rgba(255, 255, 255, 0.75);
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
        <div class="navbar-links">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Open main wrapper container
st.markdown('<div class="main-app-container">', unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])
with col1:
    language = st.selectbox("🌐 Select Language", ["English", "Gujarati"])
with col2:
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

st.markdown("---")
st.markdown("""
    <div class='section-header'>
        <h1>🏥 AI Medical Report Analyzer</h1>
        <p>Get instant health insights from your medical reports</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

st.markdown("## 📋 Let's Get Started")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("""
        <div class="feature-card" style="padding: 25px;">
            <div class="feature-icon">📤</div>
            <h3 style="font-size: 22px; font-weight: 800; color: #1f2937; margin-bottom: 15px;">Upload Your Report</h3>
        </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        t("Select a file (PDF, JPG, PNG)"),
        type=["pdf", "jpg", "png"],
        help="Upload your medical report for analysis"
    )
    gender = st.selectbox(
        t("👤 Patient Gender"),
        ["Male", "Female", "General"]
    )
    gender_map = {"Male": "male", "Female": "female", "General": "general"}
    st.markdown("### ")
    analyze_clicked = st.button(t("🔍 Analyze Report Now"), use_container_width=True)

with right_col:
    st.markdown("""
        <div class="feature-card" style="padding: 25px;">
            <div class="feature-icon">💡</div>
            <h3 style="font-size: 22px; font-weight: 800; color: #1f2937; margin-bottom: 15px;">Quick Tips</h3>
        </div>
    """, unsafe_allow_html=True)
    st.info("✅ Supported formats: PDF, JPG, PNG")
    st.warning("📄 Make sure the report is clear and readable")
    st.success("🔒 Your data stays local and secure")

if analyze_clicked:

    if uploaded_file is None:
        st.warning(t("⚠️ Please upload a file first"))

    else:
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner(t("Analyzing your report...")):

            analysis_result = run_analysis(
                file_path,
                gender=gender_map[gender]
            )

            results = analysis_result['results']
            summary = analysis_result['summary']
            interpretation = analysis_result['interpretation']
            info = analysis_result['patient_info']
            ai_summary = analysis_result.get('ai_summary')

            st.session_state["results"] = results
            st.session_state["summary"] = summary
            st.session_state["interpretation"] = interpretation
            st.session_state["info"] = info
            st.session_state["ai_summary"] = ai_summary
            st.session_state.analysis_done = True

        st.success(t("✅ Analysis Completed"))


if st.session_state.analysis_done:

    results = st.session_state.get("results", [])
    summary = st.session_state.get("summary", "")
    info = st.session_state.get("info", {})
    ai_summary = st.session_state.get("ai_summary", None)
    
    # Calculate metrics for cards
    total_params = len(results)
    normal_params = len([r for r in results if r["status"] == "NORMAL"])
    high_params = len([r for r in results if "HIGH" in r["status"]])
    low_params = len([r for r in results if "LOW" in r["status"]])

    # Helper function to generate visual range meter
    def generate_custom_table_html(results, t, language):
        html = f"""
        <div style="overflow-x: auto; border-radius: 16px; border: 1px solid rgba(213, 198, 141, 0.4); box-shadow: 0 4px 20px rgba(156, 166, 131, 0.05); margin-bottom: 30px;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);">
                <thead>
                    <tr style="background: rgba(156, 166, 131, 0.15); border-bottom: 2px solid rgba(156, 166, 131, 0.3);">
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Parameter')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Value')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Status')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px; min-width: 260px;">{t('Visual Range (Low - High)')}</th>
                    </tr>
                </thead>
                <tbody>
        """
        for r in results:
            param = t(r["parameter"])
            val_str = f"{r['value']} {r['unit']}"
            status = t(r["status"])
            
            # Determine status colors
            if "HIGH" in r["status"]:
                bg_color = "rgba(239, 68, 68, 0.15)"
                text_color = "#b91c1c"
                badge_color = "#ef4444"
            elif "LOW" in r["status"]:
                bg_color = "rgba(245, 158, 11, 0.15)"
                text_color = "#b45309"
                badge_color = "#f59e0b"
            else:
                bg_color = "rgba(16, 185, 129, 0.15)"
                text_color = "#047857"
                badge_color = "#10b981"
                
            # Range meter calculation
            try:
                val_f = float(r["value"])
                low_f = float(r["low"])
                high_f = float(r["high"])
                if high_f == low_f:
                    percent = 50
                else:
                    percent = ((val_f - low_f) / (high_f - low_f)) * 100
                    percent = max(0, min(100, percent))
            except:
                percent = 50
                
            meter_html = f"""
            <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <span style="font-size: 11px; color: #1a1d13; width: 35px; text-align: right; font-weight: 500;">{r['low']}</span>
                <div style="flex-grow: 1; height: 6px; background-color: rgba(156, 166, 131, 0.2); border-radius: 3px; position: relative;">
                    <div style="position: absolute; left: 25%; right: 25%; top: 0; bottom: 0; background: rgba(16, 185, 129, 0.12); border-radius: 3px;"></div>
                    <div style="position: absolute; left: {percent}%; top: 50%; transform: translate(-50%, -50%); width: 12px; height: 12px; border-radius: 50%; background-color: {badge_color}; border: 2px solid #f5f3e6; box-shadow: 0 2px 4px rgba(0,0,0,0.15);"></div>
                </div>
                <span style="font-size: 11px; color: #1a1d13; width: 35px; font-weight: 500;">{r['high']}</span>
            </div>
            """
            
            html += f"""
            <tr style="border-bottom: 1px solid rgba(213, 198, 141, 0.25);">
                <td style="padding: 14px 20px; font-weight: 600; color: #1a1d13; font-size: 14px;">{param}</td>
                <td style="padding: 14px 20px; font-weight: 700; color: #1a1d13; font-size: 14px;">{val_str}</td>
                <td style="padding: 14px 20px;">
                    <span style="display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 700; text-align: center; color: {text_color}; background-color: {bg_color}; border: 1px solid {text_color}22;">{status}</span>
                </td>
                <td style="padding: 14px 20px;">{meter_html}</td>
            </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
        import textwrap
        return textwrap.dedent(html)

    def generate_interpretation_table_html(table_data, t):
        html = f"""
        <div style="overflow-x: auto; border-radius: 16px; border: 1px solid rgba(213, 198, 141, 0.4); box-shadow: 0 4px 20px rgba(156, 166, 131, 0.05); margin-bottom: 30px;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);">
                <thead>
                    <tr style="background: rgba(156, 166, 131, 0.15); border-bottom: 2px solid rgba(156, 166, 131, 0.3);">
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Parameter')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Value')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Status')}</th>
                        <th style="padding: 16px 20px; font-weight: 700; color: #1a1d13; font-size: 15px;">{t('Possible Reasons')}</th>
                    </tr>
                </thead>
                <tbody>
        """
        for row in table_data:
            param = row["Parameter"]
            val = row["Value"]
            status = row["Status"]
            reasons = row["Possible Reasons"]
            
            # Simple check for raw status
            raw_status = row.get("raw_status", "")
            if "HIGH" in raw_status or "High" in status or "ઊંચો" in status:
                bg_color = "rgba(239, 68, 68, 0.15)"
                text_color = "#b91c1c"
            elif "LOW" in raw_status or "Low" in status or "ઓછું" in status:
                bg_color = "rgba(245, 158, 11, 0.15)"
                text_color = "#b45309"
            else:
                bg_color = "rgba(16, 185, 129, 0.15)"
                text_color = "#047857"
                
            html += f"""
            <tr style="border-bottom: 1px solid rgba(213, 198, 141, 0.25);">
                <td style="padding: 14px 20px; font-weight: 600; color: #1a1d13; font-size: 14px;">{param}</td>
                <td style="padding: 14px 20px; font-weight: 700; color: #1a1d13; font-size: 14px;">{val}</td>
                <td style="padding: 14px 20px;">
                    <span style="display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 700; text-align: center; color: {text_color}; background-color: {bg_color}; border: 1px solid {text_color}22;">{status}</span>
                </td>
                <td style="padding: 14px 20px; color: #1a1d13; font-size: 14px; line-height: 1.5;">{reasons}</td>
            </tr>
            """
        html += """
                </tbody>
            </table>
        </div>
        """
        import textwrap
        return textwrap.dedent(html)

    st.markdown("---")
    st.markdown(f"""
        <div class='section-header' style='margin-bottom: 25px;'>
            <h2 style='font-size: 28px; color: #4a4e3b;'>👤 {t('Patient Information')}</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="info-card" style="border-left: 5px solid #9ca683;">
                <div style="font-size: 32px; margin-bottom: 8px;">👤</div>
                <div style="font-size: 15px; font-weight: 700; color: #606450; text-transform: uppercase; letter-spacing: 0.5px;">{t('Name')}</div>
                <div style="font-size: 22px; font-weight: 800; color: #4a4e3b; margin-top: 8px;">{info.get('name', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="info-card" style="border-left: 5px solid #9ca683;">
                <div style="font-size: 32px; margin-bottom: 8px;">🎂</div>
                <div style="font-size: 15px; font-weight: 700; color: #606450; text-transform: uppercase; letter-spacing: 0.5px;">{t('Age')}</div>
                <div style="font-size: 22px; font-weight: 800; color: #4a4e3b; margin-top: 8px;">{info.get('age', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="info-card" style="border-left: 5px solid #9ca683;">
                <div style="font-size: 32px; margin-bottom: 8px;">📅</div>
                <div style="font-size: 15px; font-weight: 700; color: #606450; text-transform: uppercase; letter-spacing: 0.5px;">{t('Date')}</div>
                <div style="font-size: 22px; font-weight: 800; color: #4a4e3b; margin-top: 8px;">{info.get('date', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
        <div class='section-header' style='margin-bottom: 25px;'>
            <h2 style='font-size: 28px; color: #4a4e3b;'>📌 {t('Quick Overview')}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-bottom: 4px solid #9ca683;">
                <div class="metric-value">{total_params}</div>
                <div class="metric-label">{t('Total Parameters')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-bottom: 4px solid #10b981;">
                <div class="metric-value" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{normal_params}</div>
                <div class="metric-label">{t('Normal')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-bottom: 4px solid #f59e0b;">
                <div class="metric-value" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{low_params}</div>
                <div class="metric-label">{t('Low')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-bottom: 4px solid #ef4444;">
                <div class="metric-value" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{high_params}</div>
                <div class="metric-label">{t('High')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # Beautifully styled Interactive Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 " + t("Parameters & Metrics"),
        "🩺 " + t("Clinical Analysis & Advice"),
        "📝 " + t("Rule-Based Summary"),
        "🤖 " + t("AI Health Insights")
    ])

    with tab1:
        st.markdown("<h3 style='color: #4a4e3b; margin-top: 15px; margin-bottom: 15px;'>📊 " + t("Medical Parameters") + "</h3>", unsafe_allow_html=True)
        if results:
            st.markdown(generate_custom_table_html(results, t, language), unsafe_allow_html=True)
        else:
            st.warning(t("No parameters detected"))

    with tab2:
        st.markdown("<h3 style='color: #4a4e3b; margin-top: 15px; margin-bottom: 15px;'>🩺 " + t("Clinical Analysis & Advice") + "</h3>", unsafe_allow_html=True)
        
        left_tab_col, right_tab_col = st.columns(2)
        
        with left_tab_col:
            st.markdown(f"""
                <div style="background: rgba(245, 243, 230, 0.7); border: 1px solid rgba(213, 198, 141, 0.4); padding: 25px; border-radius: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <h4 style="margin-top:0; color:#b91c1c; font-size:18px; display:flex; align-items:center; gap:8px;">⚠️ {t('KEY FINDINGS (ABNORMALITIES)')}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            abnormal = [r for r in results if "HIGH" in r['status'] or "LOW" in r['status']]
            if abnormal:
                display_list = [f"• **{r['parameter']}**: {r['value']} {r['unit']} → {r['status']}" for r in abnormal]
                if language == "Gujarati":
                    display_list = translate_bulk(display_list)
                for item in display_list:
                    st.markdown(f"<div style='padding: 6px 12px; background: rgba(239, 68, 68, 0.05); border-left: 3px solid #ef4444; border-radius: 4px; margin-bottom: 8px;'>{item}</div>", unsafe_allow_html=True)
            else:
                st.success(t("✅ All parameters are normal"))
                
        with right_tab_col:
            st.markdown(f"""
                <div style="background: rgba(245, 243, 230, 0.7); border: 1px solid rgba(213, 198, 141, 0.4); padding: 25px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); height: 100%;">
                    <h4 style="margin-top:0; color:#4a4e3b; font-size:18px; display:flex; align-items:center; gap:8px;">💡 {t('CLINICAL INTERPRETATION & ADVICE')}</h4>
                    <div style="margin-top: 15px;">
            """, unsafe_allow_html=True)
            
            params_low = {r['parameter'] for r in results if "LOW" in r['status']}
            params_high = {r['parameter'] for r in results if "HIGH" in r['status']}
            
            has_advice = False
            if "Hemoglobin" in params_low:
                st.markdown(f"**Interpretation:** {t('Low Hemoglobin indicates possible anemia.')}")
                st.markdown(f"**Recommendation:** {t('Increase iron-rich diet (spinach, dates, jaggery)')}")
                st.markdown("---")
                has_advice = True
            if "WBC" in params_high:
                st.markdown(f"**Interpretation:** {t('High WBC may indicate infection.')}")
                st.markdown(f"**Recommendation:** {t('Consult doctor for infection check')}")
                st.markdown("---")
                has_advice = True
                
            st.markdown(f"*{t('Maintain healthy lifestyle')}*")
            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("<h3 style='color: #4a4e3b; margin-top: 15px; margin-bottom: 15px;'>📝 " + t("Rule-Based Summary") + "</h3>", unsafe_allow_html=True)
        
        # Summary Card
        st.markdown(f"""
            <div style="background: rgba(245, 243, 230, 0.8); border: 1px solid rgba(156, 166, 131, 0.3); padding: 30px; border-radius: 24px; box-shadow: 0 8px 32px rgba(156, 166, 131, 0.05); line-height: 1.7; color: #4a4e3b; font-size: 16px; margin-bottom: 30px;">
                <div style="font-weight: 800; font-size: 18px; margin-bottom: 15px; color: #9ca683; display: flex; align-items: center; gap: 8px;">
                    🧬 {t('RULE-BASED SUMMARY')}
                </div>
                {t(summary)}
            </div>
        """, unsafe_allow_html=True)
        
        # Table of abnormalities with reasons
        st.markdown("<h4 style='color: #4a4e3b; margin-bottom: 15px;'>" + t("Overall Interpretation (Table View)") + "</h4>", unsafe_allow_html=True)
        
        table_data = []
        for r in results:
            if r["status"] != "NORMAL":
                table_data.append({
                    "Parameter": translate_text(r["parameter"]),
                    "Value": translate_text(f"{r['value']} {r['unit']}"),
                    "Status": translate_text(r["status"]),
                    "Possible Reasons": translate_text(", ".join(r.get("reasons", []))),
                    "raw_status": r["status"]
                })

        if table_data:
            st.markdown(generate_interpretation_table_html(table_data, t), unsafe_allow_html=True)
        else:
            st.success(t("✅ All parameters are normal"))

    with tab4:
        st.markdown("<h3 style='color: #4a4e3b; margin-top: 15px; margin-bottom: 15px;'>🤖 " + t("AI Health Insights") + "</h3>", unsafe_allow_html=True)
        from services.gemini_service import is_gemini_available
        if not is_gemini_available():
            st.warning(t("⚠️ Gemini AI is currently unavailable. Please check your API configuration and try again."))
        elif not ai_summary:
            st.warning(t("⚠️ No AI summary generated. Please analyze a medical report first."))
        elif isinstance(ai_summary, dict) and "error" in ai_summary:
            st.error(f"⚠️ {ai_summary['error']}")
        else:
            if isinstance(ai_summary, dict):
                # Overview
                st.markdown(f"#### 📋 {t('Report Overview')}")
                render_ai_html(ai_summary.get("report_overview", ""))
                
                # Normal & Abnormal
                col_normal, col_abnormal = st.columns(2)
                with col_normal:
                    st.markdown(f"#### 🟢 {t('Normal Results')}")
                    render_ai_html(ai_summary.get("normal_results", ""))
                with col_abnormal:
                    st.markdown(f"#### 🟠 {t('Abnormal Results')}")
                    render_ai_html(ai_summary.get("abnormal_results", ""))
                
                # Easy Explanation
                st.markdown(f"#### 🧠 {t('Easy Explanation')}")
                render_ai_html(ai_summary.get("easy_explanation", ""))
                
                # Overall Insight & Next Step
                col_insight, col_step = st.columns(2)
                with col_insight:
                    st.markdown(f"#### 💡 {t('Overall Insight')}")
                    render_ai_html(ai_summary.get("overall_insight", ""))
                with col_step:
                    st.markdown(f"#### 👨‍⚕️ {t('Suggested Next Step')}")
                    render_ai_html(ai_summary.get("suggested_next_step", ""))
                
                # Gujarati Explanation
                st.markdown(f"#### 🇮🇳 {t('Gujarati Explanation')}")
                render_ai_html(ai_summary.get("gujarati_explanation", ""))
            else:
                render_ai_html(ai_summary)
            
            # Disclaimer
            st.markdown("---")
            st.warning(f"⚠️ **{t('Medical Disclaimer')}:** {t('This AI-generated information is for educational purposes only and does not replace professional medical advice, diagnosis, or treatment.')}")

    st.markdown("---")
    st.markdown(f"""
        <div class='section-header' style='margin-bottom: 25px;'>
            <h2 style='font-size: 28px; color: #4a4e3b;'>🔗 {t('Quick Actions')}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("📊 View Dashboard"), use_container_width=True):
            st.switch_page("pages/dashboard.py")
    with col2:
        if st.button(t("💬 Open Health Assistant"), use_container_width=True):
            st.switch_page("pages/chatbot.py")

st.markdown("---")
st.caption(t("⚕️ AI-based health assistant | For educational use only"))

# Close main wrapper container
st.markdown('</div>', unsafe_allow_html=True)
