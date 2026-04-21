import streamlit as st
import os
from health_backend import run_analysis, generate_health_summary

st.set_page_config(page_title="Health Advisor AI", layout="centered")

st.title("🩺 AI Medical Report Analyzer")
st.markdown("Upload your report and get **instant health insights**")
st.markdown("---")

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

    if st.button("🔍 Analyze Report"):

        with st.spinner("Analyzing your report..."):

            results = run_analysis(file_path)
            summary = generate_health_summary(results)

        st.markdown("---")

        st.subheader("📊 Extracted Parameters")

        if results:
            for r in results:
                if r['status'] == "LOW":
                    st.error(f"{r['parameter']} : {r['value']} (LOW)")
                elif r['status'] == "HIGH":
                    st.warning(f"{r['parameter']} : {r['value']} (HIGH)")
                else:
                    st.success(f"{r['parameter']} : {r['value']} (NORMAL)")
        else:
            st.warning("No parameters detected")

        st.markdown("---")

        st.subheader("🧠 AI Explanation & Advice")
        st.text(summary)

        st.markdown("---")

        st.subheader("📈 Parameter Visualization")

        chart_data = {r['parameter']: r['value'] for r in results}

        if chart_data:
            st.bar_chart(chart_data)

st.markdown("---")
st.caption("⚕️ AI-based health assistant | For educational use only")