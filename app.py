import streamlit as st
import os
from health_backend import run_analysis

# ✅ FIX: Use deep-translator (works with Python 3.13)
from deep_translator import GoogleTranslator

def translate_to_gujarati(text):
    try:
        return GoogleTranslator(source='auto', target='gu').translate(text)
    except:
        return text


# ─── PAGE CONFIG ───────────────────────────────────
st.set_page_config(page_title="Health Advisor AI", layout="centered")

st.title("🩺 AI Medical Report Analyzer")
st.markdown("Upload your report and get **instant health insights**")
st.markdown("---")

# 🌐 Language Selector
language = st.selectbox(
    "🌐 Select Language",
    ["English", "Gujarati"]
)

st.info("👆 Please upload a medical report to begin analysis")

uploaded_file = st.file_uploader(
    "📤 Upload Report (PDF/Image)", 
    type=["pdf", "jpg", "png"]
)

if uploaded_file is not None:

    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded successfully!")

    # Gender selection for accurate reference ranges
    gender = st.selectbox(
        "👤 Select Patient Gender",
        ["Male", "Female", "General"],
        index=0
    )
    gender_map = {"Male": "male", "Female": "female", "General": "general"}

    if st.button("🔍 Analyze Report"):

        with st.spinner("Analyzing your report..."):

            # ✅ Updated: Use new run_analysis that returns dictionary
            analysis_result = run_analysis(file_path, gender=gender_map[gender])
            results = analysis_result['results']
            patient_info = analysis_result['patient_info']
            formatted_report = analysis_result['formatted_report']

        st.markdown("---")

        st.subheader("📊 Extracted Parameters")

        if results:
            for r in results:
                text = f"{r['parameter']} : {r['value']} {r['unit']} ({r['status']})"

                # 🌐 Translate
                if language == "Gujarati":
                    text = translate_to_gujarati(text)

                if "🚨" in r['status']:
                    st.error(text)
                elif "🔴" in r['status']:
                    st.error(text)
                elif "🟡" in r['status']:
                    st.warning(text)
                elif "🟢" in r['status']:
                    st.success(text)
                else:
                    st.info(text)
        else:
            st.warning("No parameters detected")

        st.markdown("---")

        st.subheader("Formatted Medical Report")

        # 🌐 Translate formatted report
        if language == "Gujarati":
            formatted_report = translate_to_gujarati(formatted_report)

        st.text(formatted_report)

        st.markdown("---")

        st.subheader("📈 Parameter Visualization")

        chart_data = {r['parameter']: r['value'] for r in results if r['unit'] and r['unit'] != ''}

        if chart_data:
            st.bar_chart(chart_data)

st.markdown("---")
st.caption("⚕️ AI-based health assistant | For educational use only")