import streamlit as st
from deep_translator import GoogleTranslator
from PIL import Image

# ✅ IMPORT DISEASE LOGIC
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from disease_predictor import predict_diseases
from services.gemini_service import chat_with_health_assistant, is_gemini_available

favicon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "health-report.png")
try:
    favicon = Image.open(favicon_path)
except Exception:
    favicon = "💬"

st.set_page_config(page_title="Health Assistant", page_icon=favicon, layout="wide", initial_sidebar_state="collapsed")

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
        <h1>💬 Health Assistant</h1>
        <p>Your AI-powered medical advisor and report explainer</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

def translate(text):
    try:
        if language == "Gujarati" and text:
            return GoogleTranslator(source='auto', target='gu').translate(text)
        return text
    except:
        return text

# Check if we have data
if "results" not in st.session_state or not st.session_state.get("analysis_done", False):
    st.warning("⚠️ " + translate("Please analyze a medical report first!"))
    st.markdown("---")
    st.page_link("pages/analyzer.py", label="🔙 " + translate("Back to Report Analyzer"), use_container_width=True)
    st.stop()

results = st.session_state.get("results", [])
summary = st.session_state.get("summary", "")
info = st.session_state.get("info", {})

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("assistant", translate("Hi! 👋 I am your Health Assistant.\nWhat do you want to know?"))
    ]

def add_message(role, text):
    st.session_state.chat_history.append((role, translate(text)))

def render_chat_message(content):
    if not content:
        return
    content = str(content)
    content = content.replace("```html", "")
    content = content.replace("```HTML", "")
    content = content.replace("```", "")
    content = content.strip()
    
    import textwrap
    st.markdown(textwrap.dedent(content), unsafe_allow_html=True)

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        render_chat_message(msg)

st.markdown("---")

st.markdown("""
    <div class='section-header'>
        <h2>📌 Choose Option</h2>
    </div>
""", unsafe_allow_html=True)

# Add helper for button prompts to Gemini
def ask_gemini_button(user_query, fallback_text):
    st.session_state.chat_history.append(("user", translate(user_query)))
    if is_gemini_available():
        report_data = {"results": results, "patient_info": info}
        with st.spinner(translate("Thinking...")):
            response = chat_with_health_assistant(report_data, user_query, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append(("assistant", response))
    else:
        st.session_state.chat_history.append(("assistant", translate(fallback_text)))
    st.rerun()

col1, col2 = st.columns(2)

# 📊 SUMMARY
if col1.button("📊 Smart Summary", use_container_width=True):
    fallback_summary = f"""
    <div style="background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(213, 198, 141, 0.4); padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
        <h4 style="margin: 0 0 10px 0; color: #4a4e3b; font-weight: 700;">📊 {translate("Smart Summary")}</h4>
        <div style="color: #1a1d13; line-height: 1.5; font-size: 14px;">{summary}</div>
    </div>
    """
    ask_gemini_button("Provide a smart summary of my report", fallback_summary)

# 👤 PATIENT INFO
if col2.button("👤 Patient Info", use_container_width=True):
    text = f"""
    <div style="background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(213, 198, 141, 0.4); padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
        <h4 style="margin: 0 0 10px 0; color: #4a4e3b; font-weight: 700;">👤 {translate("Patient Information")}</h4>
        <ul style="list-style-type: none; padding-left: 0; margin: 0; font-size: 14px;">
            <li style="margin-bottom: 5px; color: #1a1d13;"><b>Name:</b> {info.get('name','N/A')}</li>
            <li style="margin-bottom: 5px; color: #1a1d13;"><b>Age:</b> {info.get('age','N/A')}</li>
            <li style="margin-bottom: 0; color: #1a1d13;"><b>Date:</b> {info.get('date','N/A')}</li>
        </ul>
    </div>
    """
    ask_gemini_button("Show patient info", text)

# 🧠 DISEASE EXPLANATION
if col1.button("🧠 Disease Explanation", use_container_width=True):
    diseases = predict_diseases(results)
    abnormal = [r for r in results if "LOW" in r['status'] or "HIGH" in r['status']]
    
    fallback = f"""
    <div style="background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(213, 198, 141, 0.4); padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
        <h4 style="margin: 0 0 10px 0; color: #4a4e3b; font-weight: 700;">🧠 {translate("Possible Health Conditions")}</h4>
    """
    if diseases:
        for d in diseases:
            fallback += f"""
            <div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed rgba(213, 198, 141, 0.5);">
                <span style="font-weight: 700; color: #b91c1c;">🔸 {translate(d['name'])} ({translate(d['confidence'])})</span><br/>
                <span style="font-size: 13px; color: #1a1d13;"><b>Reason:</b> {translate(d['reason'])}</span><br/>
                <span style="font-size: 13px; color: #047857;"><b>Advice:</b> {translate(d['advice'])}</span>
            </div>
            """
    elif abnormal:
        fallback += f"""
        <div style="color: #b45309; font-weight: 600; margin-bottom: 10px;">⚠️ {translate("Some parameters are abnormal but no clear disease pattern detected.")}</div>
        """
    else:
        fallback += f"""
        <div style="color: #047857; font-weight: 600; margin-bottom: 10px;">✅ {translate("Your report is normal.")}</div>
        """
    fallback += f"""
        <div style="font-size: 13px; color: #b91c1c; font-weight: 600; margin-top: 5px;">👉 {translate("Please consult a doctor for confirmation.")}</div>
    </div>
    """
    ask_gemini_button("Explain my possible conditions and diseases based on the report abnormalities", fallback)

# 💡 PERSONALIZED ADVICE
if col2.button("💡 Personalized Advice", use_container_width=True):
    advice = f"""
    <div style="background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(213, 198, 141, 0.4); padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
        <h4 style="margin: 0 0 10px 0; color: #4a4e3b; font-weight: 700;">💡 {translate("Health Advice")}</h4>
        <ul style="padding-left: 20px; margin: 0 0 10px 0; color: #1a1d13; font-size: 14px;">
    """
    abnormal = False
    for r in results:
        if "LOW" in r['status']:
            advice += f"<li><b>{translate(r['parameter'])}:</b> {translate('Increase with proper nutrition')}</li>"
            abnormal = True
        elif "HIGH" in r['status']:
            advice += f"<li><b>{translate(r['parameter'])}:</b> {translate('Control with lifestyle changes')}</li>"
            abnormal = True
    if not abnormal:
        advice += f"<li>{translate('All parameters are normal. Maintain healthy lifestyle.')}</li>"
    advice += f"""
        </ul>
        <div style="font-weight: 600; color: #047857; margin-top: 10px; font-size: 13px;">
            ✔ {translate("Balanced diet")} | ✔ {translate("Regular exercise")} | ✔ {translate("Doctor consultation")}
        </div>
    </div>
    """
    ask_gemini_button("Give me personalized health and diet advice based on my parameters", advice)

# 📈 IMPROVEMENT TRACKING
if col1.button("📈 Improvement Tips", use_container_width=True):
    fallback = f"""
    <div style="background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(213, 198, 141, 0.4); padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
        <h4 style="margin: 0 0 10px 0; color: #4a4e3b; font-weight: 700;">📈 {translate("Improvement Plan")}</h4>
        <ul style="padding-left: 20px; margin: 0; color: #1a1d13; font-size: 14px;">
            <li>{translate("Iron-rich diet (spinach, dates, jaggery)")}</li>
            <li>{translate("Drink more water")}</li>
            <li>{translate("Proper sleep (7–8 hours)")}</li>
            <li>{translate("Regular exercise")}</li>
            <li>{translate("Re-test after 15 days")}</li>
        </ul>
    </div>
    """
    ask_gemini_button("How can I improve my abnormal parameter values?", fallback)

if col2.button("🚨 Critical Check", use_container_width=True):
    critical = [r for r in results if "CRITICAL" in r['status']]
    if critical:
        fallback = f"""
        <div style="background: rgba(254, 226, 226, 0.9); border: 1px solid #f87171; padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.05);">
            <h4 style="margin: 0 0 10px 0; color: #991b1b; font-weight: 800;">🚨 {translate("Critical Conditions")}</h4>
            <ul style="padding-left: 20px; margin: 0 0 10px 0; color: #991b1b; font-size: 14px;">
        """
        for r in critical:
            fallback += f"<li><b>{translate(r['parameter'])}</b> {translate('is in critical status')} ({r['value']} {r['unit']})</li>"
        fallback += f"""
            </ul>
            <div style="font-weight: 700; color: #dc2626; font-size: 14px;">👉 {translate("Immediate doctor consultation required!")}</div>
        </div>
        """
    else:
        fallback = f"""
        <div style="background: rgba(209, 250, 229, 0.9); border: 1px solid #34d399; padding: 15px; border-radius: 12px; color: #065f46; font-weight: 700; font-size: 14px;">
            ✅ {translate("No critical conditions detected.")}
        </div>
        """
    ask_gemini_button("Check if any of my parameters are in critical state", fallback)

# Free-text user question
user_input = st.chat_input(translate("Ask questions about your uploaded report..."))
if user_input:
    # Append user question
    st.session_state.chat_history.append(("user", user_input))
    st.rerun()

# Generate response if the last message is from user
if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "user":
    last_query = st.session_state.chat_history[-1][1]
    report_data = {
        "results": results,
        "patient_info": info
    }
    if is_gemini_available():
        response = chat_with_health_assistant(report_data, last_query, st.session_state.chat_history[:-1])
    else:
        response = translate("⚠️ Gemini AI is currently unavailable. Please check your API configuration and try again.")
    
    st.session_state.chat_history.append(("assistant", response))
    st.rerun()

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.page_link("pages/analyzer.py", label="🔙 Back to Report Analyzer", use_container_width=True)
