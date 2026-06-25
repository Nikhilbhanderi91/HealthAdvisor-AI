import streamlit as st
from deep_translator import GoogleTranslator

# ✅ IMPORT DISEASE LOGIC
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from disease_predictor import predict_diseases

st.set_page_config(page_title="Health Assistant", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

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

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)

st.markdown("---")

st.markdown("""
    <div class='section-header'>
        <h2>📌 Choose Option</h2>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# 📊 SUMMARY
if col1.button("📊 Smart Summary", use_container_width=True):
    add_message("user", "Show smart summary")
    add_message("assistant", summary)
    st.rerun()

# 👤 PATIENT INFO
if col2.button("👤 Patient Info", use_container_width=True):
    add_message("user", "Show patient info")

    text = f"""
👤 Name: {info.get('name','N/A')}
🎂 Age: {info.get('age','N/A')}
📅 Date: {info.get('date','N/A')}
"""
    add_message("assistant", text)
    st.rerun()

# 🧠 DISEASE EXPLANATION (FIXED)
if col1.button("🧠 Disease Explanation", use_container_width=True):
    add_message("user", "Explain my condition")

    diseases = predict_diseases(results)

    abnormal = [r for r in results if "LOW" in r['status'] or "HIGH" in r['status']]

    if not diseases and not abnormal:
        add_message("assistant", " Your report is normal.")
    else:
        msg = "🧠 Possible Health Conditions:\n\n"

        if diseases:
            for d in diseases:
                msg += f"🔸 {d['name']} ({d['confidence']})\n"
                msg += f"➤ Reason: {d['reason']}\n"
                msg += f"💡 Advice: {d['advice']}\n\n"
        else:
            msg += "⚠️ Some parameters are abnormal but no clear disease pattern detected.\n\n"

        msg += "👉 Please consult a doctor for confirmation."
        add_message("assistant", msg)

    st.rerun()

# 💡 PERSONALIZED ADVICE (IMPROVED)
if col2.button("💡 Personalized Advice", use_container_width=True):
    add_message("user", "Give me advice")

    advice = "💡 Health Advice:\n\n"

    abnormal = False

    for r in results:
        if "LOW" in r['status']:
            advice += f"- {r['parameter']}: Increase with proper nutrition\n"
            abnormal = True
        elif "HIGH" in r['status']:
            advice += f"- {r['parameter']}: Control with lifestyle changes\n"
            abnormal = True

    if not abnormal:
        advice += "All parameters are normal. Maintain healthy lifestyle."

    advice += "\n\n✔ Balanced diet\n✔ Regular exercise\n✔ Doctor consultation"

    add_message("assistant", advice)
    st.rerun()

# 📈 IMPROVEMENT TRACKING
if col1.button("📈 Improvement Tips", use_container_width=True):
    add_message("user", "How to improve")

    add_message("assistant",
    """📈 Improvement Plan:
- Iron-rich diet (spinach, dates, jaggery)
- Drink more water
- Proper sleep (7–8 hours)
- Regular exercise
- Re-test after 15 days""")

    st.rerun()

if col2.button("🚨 Critical Check", use_container_width=True):
    add_message("user", "Check critical values")

    critical = [r for r in results if "CRITICAL" in r['status']]

    if critical:
        msg = "🚨 Critical Conditions:\n"
        for r in critical:
            msg += f"- {r['parameter']} is {r['status']}\n"
        msg += "\n👉 Immediate doctor consultation required!"
    else:
        msg = "✅ No critical conditions detected."

    add_message("assistant", msg)
    st.rerun()

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.page_link("pages/analyzer.py", label="🔙 Back to Report Analyzer", use_container_width=True)
