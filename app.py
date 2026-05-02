import streamlit as st
import os
from health_backend import run_analysis

# ✅ SSL FIX: Ensure translator works by pointing to correct CA certificates
import certifi
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

from deep_translator import GoogleTranslator

def translate_to_gujarati(text):
    try:
        if not text or text.strip() == "": return text
        return GoogleTranslator(source='auto', target='gu').translate(text)
    except Exception as e:
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

        # 🌐 Dynamic UI Subheaders
        ext_title = "📊 Extracted Parameters"
        rep_title = "Formatted Medical Report"
        vis_title = "📈 Parameter Visualization"
        if language == "Gujarati":
            ext_title = translate_to_gujarati(ext_title)
            rep_title = translate_to_gujarati(rep_title)
            vis_title = translate_to_gujarati(vis_title)

        st.subheader(ext_title)

        if results:
            # 🌐 Prepare strings for batch translation
            display_list = []
            for r in results:
                display_list.append(f"{r['parameter']} : {r['value']} {r['unit']} ({r['status']})")
            
            # Batch Translate if needed
            if language == "Gujarati":
                with st.spinner("Translating results..."):
                    try:
                        full_text = "\n".join(display_list)
                        translated_text = translate_to_gujarati(full_text)
                        display_list = translated_text.split("\n")
                    except: pass

            # Display results
            for i, r in enumerate(results):
                text = display_list[i] if i < len(display_list) else f"{r['parameter']} : {r['value']} {r['unit']} ({r['status']})"
                if "🚨" in r['status'] or "🔴" in r['status']: st.error(text)
                elif "🟡" in r['status']: st.warning(text)
                elif "🟢" in r['status']: st.success(text)
                else: st.info(text)
        else:
            st.warning("No parameters detected")

        st.markdown("---")
        st.subheader(rep_title)

        # 🌐 Full Report Translation
        if language == "Gujarati":
            with st.spinner("Translating full report..."):
                try:
                    # Translate line by line or by sections to ensure 100% coverage
                    lines = formatted_report.split("\n")
                    translated_lines = []
                    for line in lines:
                        if line.strip():
                            translated_lines.append(translate_to_gujarati(line))
                        else:
                            translated_lines.append("")
                    formatted_report = "\n".join(translated_lines)
                except: pass

        st.text(formatted_report)

        st.markdown("---")

        st.subheader("📈 Parameter Visualization")

        chart_data = {r['parameter']: r['value'] for r in results if r['unit'] and r['unit'] != ''}

        if chart_data:
            st.bar_chart(chart_data)

st.markdown("---")
st.caption("⚕️ AI-based health assistant | For educational use only")