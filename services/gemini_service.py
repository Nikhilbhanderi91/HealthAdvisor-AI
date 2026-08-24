import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing Gemini SDK
HAS_GEMINI_SDK = False
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    logger.warning("google-generativeai package is not installed. Please install it using pip.")

def get_api_key() -> str:
    """Retrieve Gemini API Key from environment."""
    return os.getenv("GEMINI_API_KEY", "").strip()

def is_gemini_available() -> bool:
    """Check if Gemini SDK is installed and API key is configured."""
    return HAS_GEMINI_SDK and bool(get_api_key())

def init_gemini():
    """Initialize the Gemini client with the configured API key."""
    if not HAS_GEMINI_SDK:
        raise ImportError("google-generativeai package is not installed.")
    
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing or empty.")
    
    genai.configure(api_key=api_key)

def format_report_context(report_data: dict) -> str:
    """Format structured report data into a concise text representation for Gemini context."""
    if not report_data:
        return "No report data available."
    
    patient_info = report_data.get("patient_info", {})
    results = report_data.get("results", [])
    
    context = []
    context.append("Patient Information:")
    context.append(f"Name: {patient_info.get('name', 'N/A')}")
    context.append(f"Age: {patient_info.get('age', 'N/A')}")
    context.append(f"Gender: {patient_info.get('gender', 'N/A')}")
    context.append(f"Report Date: {patient_info.get('date', 'N/A')}")
    context.append("")
    context.append("Medical Parameters:")
    
    for r in results:
        param = r.get("parameter", "N/A")
        val = r.get("value", "N/A")
        unit = r.get("unit", "")
        low = r.get("low", "N/A")
        high = r.get("high", "N/A")
        status = r.get("status", "NORMAL")
        
        context.append(f"- {param}")
        context.append(f"  Value: {val} {unit}")
        context.append(f"  Reference Range: {low}-{high}")
        context.append(f"  Status: {status}")
    
    return "\n".join(context)

def generate_report_summary(report_data: dict) -> dict:
    """
    Generate a structured, educational report summary using Gemini.
    Returns a dictionary with structured keys:
    - report_overview
    - normal_results
    - abnormal_results
    - easy_explanation
    - overall_insight
    - suggested_next_step
    - gujarati_explanation
    """
    if not is_gemini_available():
        return {
            "error": "Gemini API is not configured or unavailable.",
            "report_overview": "Unable to load AI summary. Please check your GEMINI_API_KEY configuration.",
            "normal_results": "",
            "abnormal_results": "",
            "easy_explanation": "",
            "overall_insight": "",
            "suggested_next_step": "",
            "gujarati_explanation": ""
        }
    
    try:
        init_gemini()
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        report_context = format_report_context(report_data)
        
        prompt = f"""You are HealthAdvisor AI, an educational health-information assistant.

Your task is to explain laboratory report information in simple language.

Use ONLY the supplied report data.
Never invent medical values, reference ranges, patient information, symptoms, diseases, or test results.
Do not provide a definitive diagnosis.
Explain abnormal parameters in general educational terms.
Clearly distinguish extracted facts from AI-generated explanations.
If the available information is insufficient, explicitly state that the information is insufficient.

You must output a JSON object containing exactly the following keys. Do NOT include markdown code fence formatting.
Key specifications:
- "report_overview": simple overall explanation of the uploaded report.
- "normal_results": a brief summary or list of parameters identified as NORMAL.
- "abnormal_results": a brief summary or list of parameters identified as LOW or HIGH.
- "easy_explanation": simple language explanation for abnormal parameters (explaining what the parameter is and what it means to be low/high).
- "overall_insight": a concise educational interpretation based only on the extracted values.
- "suggested_next_step": general guidance recommending professional medical consultation.
- "gujarati_explanation": a simple Gujarati translation summarizing the report overview, abnormal parameters, and next steps.

REPORT DATA:
{report_context}

Output JSON format:"""

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result_dict = json.loads(response.text.strip())
        return result_dict
        
    except Exception as e:
        logger.error(f"Error generating report summary: {e}")
        return {
            "error": str(e),
            "report_overview": "⚠️ Gemini AI is currently unavailable. Please check your API configuration and try again.",
            "normal_results": "N/A",
            "abnormal_results": "N/A",
            "easy_explanation": "N/A",
            "overall_insight": "N/A",
            "suggested_next_step": "Please consult a healthcare professional.",
            "gujarati_explanation": "ભૂલ: સેવા અનુપલબ્ધ છે."
        }

def chat_with_health_assistant(report_data: dict, user_message: str, chat_history: list) -> str:
    """
    Handle chatbot messages using Gemini, referencing the analyzed report as context.
    """
    if not is_gemini_available():
        return "⚠️ Gemini AI is currently unavailable. Please check your API configuration and try again."
    
    try:
        init_gemini()
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        report_context = format_report_context(report_data)
        
        # Build chat history conversation string
        formatted_history = []
        for role, text in chat_history:
            role_label = "User" if role == "user" else "Assistant"
            formatted_history.append(f"{role_label}: {text}")
        
        history_str = "\n".join(formatted_history)
        
        prompt = f"""You are HealthAdvisor AI Health Assistant.
You provide educational explanations of medical laboratory reports.
Use the supplied report data as your primary context.
Answer the user's question clearly and directly based on the report.
Never invent report values or missing information.
Never provide a definitive diagnosis.
Do not prescribe medicines or dosages.
If the requested information is not present in the report, clearly say that the information is unavailable.
Support both English and Gujarati. Respond in the language requested or used by the user.

REPORT DATA:
{report_context}

CHAT HISTORY:
{history_str}

USER QUESTION:
{user_message}

Answer:"""

        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error in chat_with_health_assistant: {e}")
        return f"⚠️ Error interacting with AI assistant: {str(e)}"
