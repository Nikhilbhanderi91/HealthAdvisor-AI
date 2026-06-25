import streamlit as st

st.set_page_config(page_title="Health Advisor AI", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS styling for beautiful landing page
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
    
    /* Global Navigation Bar */
    .navbar {
        background: rgba(245, 243, 230, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 16px 40px;
        border-radius: 20px;
        border: 1px solid rgba(213, 198, 141, 0.4);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.08);
        margin-bottom: 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .navbar-logo {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .navbar-links {
        display: flex;
        gap: 25px;
        align-items: center;
    }
    .navbar-link {
        color: #4a4e3b;
        text-decoration: none;
        font-weight: 600;
        font-size: 16px;
        padding: 8px 16px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .navbar-link:hover {
        color: #9ca683;
        background: rgba(188, 198, 167, 0.2);
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #9ca683 0%, #bcc6a7 100%);
        padding: 100px 40px;
        border-radius: 32px;
        color: #f5f3e6;
        text-align: center;
        margin-bottom: 50px;
        box-shadow: 0 20px 50px rgba(156, 166, 131, 0.25);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(213, 198, 141, 0.3);
    }
    .hero h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 64px;
        margin-bottom: 20px;
        font-weight: 900;
        letter-spacing: -1px;
        line-height: 1.1;
        color: #f5f3e6;
    }
    .hero p {
        font-size: 24px;
        opacity: 0.95;
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto;
        color: #f5f3e6;
    }
    
    /* Feature Cards */
    .feature-section {
        margin: 50px 0;
    }
    .feature-card {
        background: rgba(245, 243, 230, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 40px 30px;
        border-radius: 24px;
        border: 1px solid rgba(213, 198, 141, 0.4);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.05);
        text-align: center;
        height: 100%;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(156, 166, 131, 0.15);
        border: 1px solid rgba(156, 166, 131, 0.4);
        background: rgba(245, 243, 230, 0.9);
    }
    .feature-icon {
        font-size: 56px;
        margin-bottom: 20px;
        display: inline-block;
        transition: transform 0.3s ease;
    }
    .feature-card:hover .feature-icon {
        transform: scale(1.15) rotate(5deg);
    }
    .feature-title {
        font-size: 22px;
        font-weight: 800;
        color: #4a4e3b;
        margin-bottom: 12px;
    }
    .feature-desc {
        color: #606450;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* Workflow Section */
    .workflow-section {
        margin: 60px 0;
    }
    .workflow-card {
        background: rgba(245, 243, 230, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 35px 25px;
        border-radius: 24px;
        border: 1px solid rgba(213, 198, 141, 0.3);
        box-shadow: 0 8px 32px 0 rgba(156, 166, 131, 0.03);
        text-align: center;
        transition: all 0.3s ease;
    }
    .workflow-card:hover {
        background: rgba(245, 243, 230, 0.8);
        border-color: rgba(156, 166, 131, 0.4);
        transform: translateY(-5px);
    }
    .workflow-number {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%);
        color: #f5f3e6;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 800;
        margin: 0 auto 20px;
        box-shadow: 0 4px 15px rgba(156, 166, 131, 0.3);
    }
    .workflow-title {
        font-size: 20px;
        font-weight: 700;
        color: #4a4e3b;
        margin-bottom: 10px;
    }
    .workflow-desc {
        color: #606450;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* Footer */
    .footer {
        background: #2b2e24;
        color: #bcc6a7;
        padding: 60px 40px;
        border-radius: 28px;
        margin-top: 60px;
        text-align: center;
        box-shadow: 0 -10px 40px rgba(0,0,0,0.1);
    }
    .footer h3 {
        color: #f5f3e6;
        font-size: 28px;
        margin-bottom: 12px;
        font-weight: 800;
    }
    .footer p {
        font-size: 16px;
        margin-bottom: 15px;
    }
    
    /* Section Headers */
    .section-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .section-header h2 {
        font-size: 38px;
        font-weight: 800;
        color: #4a4e3b;
        margin-bottom: 10px;
    }
    .section-header p {
        color: #606450;
        font-size: 18px;
    }
    
    /* Custom primary button style overriding Streamlit */
    .stButton>button {
        background: linear-gradient(135deg, #9ca683 0%, #d5c68d 100%) !important;
        color: #f5f3e6 !important;
        border-radius: 16px !important;
        padding: 14px 28px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(156, 166, 131, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: auto !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 35px rgba(156, 166, 131, 0.4) !important;
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
            <span class="navbar-link">Home</span>
            <span class="navbar-link">Features</span>
            <span class="navbar-link">How It Works</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Hero Section
st.markdown(
    """
    <div class="hero">
        <h1>🏥 Your Intelligent AI Health Partner</h1>
        <p>Analyze medical reports instantly, detect potential issues, and ask questions in English & Gujarati.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Main CTA Button
col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
with col2:
    if st.button("🚀 Start Your Health Journey", type="primary", use_container_width=True):
        st.switch_page("pages/analyzer.py")

# Feature Cards Section
st.markdown("---")
st.markdown("<div class='feature-section'>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-header">
        <h2>✨ Powerful Features</h2>
        <p>Everything you need for better health insights</p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔬</div>
            <div class="feature-title">Instant Analysis</div>
            <div class="feature-desc">
                Get quick and accurate insights from your medical reports in seconds
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Reports Visualizations</div>
            <div class="feature-desc">
                Easy-to-read visualizations and detailed interpretations
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Smart Chatbot</div>
            <div class="feature-desc">
                Ask questions and get personalized health advice
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# How it works / Workflow Section
st.markdown("---")
st.markdown("<div class='workflow-section'>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-header">
        <h2>🔄 How It Works</h2>
        <p>Simple 3-step process to better health</p>
    </div>
    """,
    unsafe_allow_html=True
)

step1, step2, step3 = st.columns(3)
with step1:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-number">1</div>
            <div class="workflow-title">Upload Report</div>
            <div class="workflow-desc">
                Simply upload your medical report in PDF, JPG, or PNG format
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with step2:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-number">2</div>
            <div class="workflow-title">AI Analysis</div>
            <div class="workflow-desc">
                Our advanced AI analyzes your report instantly and accurately
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with step3:
    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-number">3</div>
            <div class="workflow-title">Get Insights</div>
            <div class="workflow-desc">
                View beautiful dashboards, detailed results, and health recommendations
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer">
        <h3>🏥 Health Advisor AI</h3>
        <p>Empowering you with AI-driven health insights</p>
        <p style="font-size: 15px; opacity: 0.7;">
            ⚕️ AI-based health assistant | For educational use only
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
