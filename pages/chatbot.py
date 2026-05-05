import streamlit as st
from deep_translator import GoogleTranslator

# ✅ IMPORT DISEASE LOGIC
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from disease_predictor import predict_diseases


st.set_page_config(page_title="Chatbot", layout="centered")

st.title("🤖 Health Assistant")

if "results" not in st.session_state:
    st.warning("⚠️ Please analyze report first in main app")
    st.stop()

results = st.session_state.get("results", [])
summary = st.session_state.get("summary", "")
info = st.session_state.get("info", {})

language = st.selectbox("🌐 Select Language", ["English", "Gujarati"])

def translate(text):
    try:
        if language == "Gujarati" and text:
            return GoogleTranslator(source='auto', target='gu').translate(text)
        return text
    except:
        return text

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

st.subheader("📌 Choose Option")

col1, col2 = st.columns(2)

# 📊 SUMMARY
if col1.button("📊 Smart Summary"):
    add_message("user", "Show smart summary")
    add_message("assistant", summary)
    st.rerun()

# 👤 PATIENT INFO
if col2.button("👤 Patient Info"):
    add_message("user", "Show patient info")

    text = f"""
👤 Name: {info.get('name','N/A')}
🎂 Age: {info.get('age','N/A')}
📅 Date: {info.get('date','N/A')}
"""
    add_message("assistant", text)
    st.rerun()

# 🧠 DISEASE EXPLANATION (FIXED)
if col1.button("🧠 Disease Explanation"):
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
if col2.button("💡 Personalized Advice"):
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
if col1.button("📈 Improvement Tips"):
    add_message("user", "How to improve")

    add_message("assistant",
    """📈 Improvement Plan:
- Iron-rich diet (spinach, dates, jaggery)
- Drink more water
- Proper sleep (7–8 hours)
- Regular exercise
- Re-test after 15 days""")

    st.rerun()

if col2.button("🚨 Critical Check"):
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

if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("---")
st.page_link("app.py", label="🔙 Back to Analyzer")