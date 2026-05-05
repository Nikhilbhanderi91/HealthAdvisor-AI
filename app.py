import streamlit as st
import os
import pandas as pd
from health_backend import run_analysis

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

st.set_page_config(page_title="Health Advisor AI", layout="centered")

language = st.selectbox("🌐 Select Language", ["English", "Gujarati"])

st.title(t("🩺 AI Medical Report Analyzer"))
st.markdown(t("Upload your report and get instant health insights"))
st.markdown("---")

st.info(t("👆 Please upload a medical report to begin analysis"))

uploaded_file = st.file_uploader(
    t("📤 Upload Report (PDF/Image)"), 
    type=["pdf", "jpg", "png"]
)

gender = st.selectbox(
    t("👤 Select Patient Gender"),
    ["Male", "Female", "General"]
)

gender_map = {"Male": "male", "Female": "female", "General": "general"}

st.markdown("### ")
analyze_clicked = st.button(t("🔍 Analyze Report"), width="stretch")

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

            st.session_state["results"] = results
            st.session_state["summary"] = summary
            st.session_state["interpretation"] = interpretation
            st.session_state["info"] = info
            st.session_state.analysis_done = True

        st.success(t("✅ Analysis Completed"))


if st.session_state.analysis_done:

    results = st.session_state.get("results", [])
    summary = st.session_state.get("summary", "")
    info = st.session_state.get("info", {})

    st.markdown("---")
    st.subheader(t("👤 Patient Information"))

    col1, col2 = st.columns(2)

    with col1:
        st.info(t(f"👤 Name: {info.get('name', 'N/A')}"))
        st.info(t(f"🎂 Age: {info.get('age', 'N/A')}"))

    with col2:
        st.info(t(f"📅 Date: {info.get('date', 'N/A')}"))

    st.markdown("---")
    st.subheader(t("📊 Medical Parameters"))

    if results:
        df = pd.DataFrame([{
            "Parameter": r["parameter"],
            "Value": f"{r['value']} {r['unit']}",
            "Normal Range": f"{r['low']} - {r['high']}",
            "Status": r["status"]
        } for r in results])

        st.table(df)

    else:
        st.warning(t("No parameters detected"))

    st.markdown("---")
    st.subheader(t("📄 Formatted Medical Report"))

    st.markdown(t("🧬 HEALTHADVISOR AI REPORT"))
    st.markdown(t("### 🔍 KEY FINDINGS (ABNORMALITIES)"))

    abnormal = [r for r in results if "HIGH" in r['status'] or "LOW" in r['status']]

    if abnormal:
        display_list = [f"• {r['parameter']}: {r['value']} {r['unit']} → {r['status']}" for r in abnormal]
        if language == "Gujarati":
            display_list = translate_bulk(display_list)
        for item in display_list:
            st.markdown(item)
    else:
        st.success(t("✅ All parameters are normal"))

    params_low = {r['parameter'] for r in results if "LOW" in r['status']}
    params_high = {r['parameter'] for r in results if "HIGH" in r['status']}

    st.markdown(t("### ⚠️ CLINICAL INTERPRETATION"))

    if "Hemoglobin" in params_low:
        st.write(t("Low Hemoglobin indicates possible anemia."))
    if "WBC" in params_high:
        st.write(t("High WBC may indicate infection."))

    st.markdown(t("### 💡 MEDICAL ADVICE"))

    if "Hemoglobin" in params_low:
        st.write(t("Increase iron-rich diet (spinach, dates, jaggery)"))
    if "WBC" in params_high:
        st.write(t("Consult doctor for infection check"))

    st.write(t("Maintain healthy lifestyle"))

    st.markdown("---")
    st.subheader(t("🧠 AI Medical Summary"))

    st.text(t(summary))

    interpretation = st.session_state.get("interpretation", "")

    st.markdown("---")
    st.subheader(t("🧠 Overall Interpretation (Table View)"))

    table_data = []
    for r in results:
        if r["status"] != "NORMAL":
            table_data.append({
                "Parameter": translate_text(r["parameter"]),
                "Value": translate_text(f"{r['value']} {r['unit']}"),
                "Status": translate_text(r["status"]),
                "Possible Reasons": translate_text(", ".join(r.get("reasons", [])))
            })

    if table_data:
        df = pd.DataFrame(table_data)
        if language == "Gujarati":
            df.columns = [
                "પેરામીટર",
                "મૂલ્ય",
                "સ્થિતિ",
                "કારણો"
            ]
        st.dataframe(df, width="stretch")
    else:
        st.success(t("✅ All parameters are normal"))

    st.markdown("---")
    st.subheader(t("🤖 Need Help?"))

    if st.button(t("💬 Open Health Assistant"), width="stretch"):
        st.switch_page("pages/chatbot.py")

st.markdown("---")
st.caption(t("⚕️ AI-based health assistant | For educational use only"))