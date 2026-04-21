"""
health_backend.py
─────────────────────────────────────────────────────────────────────────────
AI-Assisted Medical Report Analysis System — Backend Module
Exported from healthadvisor.ipynb for use with the Streamlit app (app.py).

Exports:
    run_analysis(file_path, patient_name, gender, plot) → list[dict]
    generate_health_summary(results, patient_name)      → str
─────────────────────────────────────────────────────────────────────────────
"""

import os
import re
import warnings
warnings.filterwarnings('ignore')

# ── Optional imports (graceful fallbacks) ─────────────────────────────────────
try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False

try:
    import pytesseract
    from PIL import Image
    _HAS_TESSERACT = True
except ImportError:
    _HAS_TESSERACT = False

try:
    import easyocr
    _HAS_EASYOCR = True
except ImportError:
    _HAS_EASYOCR = False


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FILE TYPE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_file_type(file_path: str) -> str:
    """Returns 'pdf', 'image', or 'unknown'."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        return 'image'
    return 'unknown'


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PDF EXTRACTION — PyMuPDF (FR1)
# ═══════════════════════════════════════════════════════════════════════════════

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extracts text from a PDF medical report using PyMuPDF (fitz).
    No OCR required — fast and accurate for digital PDFs.
    """

    if not _HAS_FITZ:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    # Open document
    doc = fitz.open(pdf_path)

    full_text = ''
    for page in doc:
        full_text += page.get_text() + '\n'

    # ✅ FIX: get page count BEFORE closing
    try:
        pages = len(doc)   # safest way
    except:
        pages = 1

    # Close document AFTER extracting everything
    doc.close()

    # Return structured data
    return {
        'text': full_text,
        'pages': pages,
        'extraction_method': 'PyMuPDF (Direct — No OCR)',
        'file_name': os.path.basename(pdf_path),
        'file_type': 'pdf',
    }
# ═══════════════════════════════════════════════════════════════════════════════
# 3. OCR EXTRACTION — pytesseract / EasyOCR (FR2)
# ═══════════════════════════════════════════════════════════════════════════════

def extract_text_from_image(image_path: str, use_easyocr: bool = False) -> dict:
    """
    Extracts text from an image-based medical report via OCR.
    Primary: pytesseract | Fallback: EasyOCR
    """
    text = ''
    method = 'Unknown'

    if use_easyocr or not _HAS_TESSERACT:
        if not _HAS_EASYOCR:
            raise ImportError("EasyOCR not installed. Run: pip install easyocr")
        reader = easyocr.Reader(['en'], verbose=False)
        results = reader.readtext(image_path, detail=0)
        text = ' '.join(results)
        method = 'EasyOCR'
    else:
        try:
            img = Image.open(image_path).convert('L')
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img, config=custom_config)
            method = 'pytesseract (Tesseract)'
        except Exception:
            if _HAS_EASYOCR:
                reader = easyocr.Reader(['en'], verbose=False)
                results = reader.readtext(image_path, detail=0)
                text = ' '.join(results)
                method = 'EasyOCR (fallback)'
            else:
                raise RuntimeError(
                    "Both pytesseract and EasyOCR failed or are not installed."
                )

    return {
        'text': text,
        'pages': 1,
        'extraction_method': method,
        'file_name': os.path.basename(image_path),
        'file_type': 'image',
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. DATA EXTRACTION — SMART CONTEXT PARSER (FIXED)
# ═══════════════════════════════════════════════════════════════════════════════

import re

PARAMETER_KEYWORDS = {
    'Hemoglobin': ['hemoglobin', 'haemoglobin', 'hb', 'hgb'],
    'Glucose': ['glucose', 'sugar', 'fbs', 'rbs'],
    'WBC': ['wbc', 'white blood', 'leucocyte'],
    'RBC': ['rbc', 'red blood', 'erythrocyte'],
    'Platelets': ['platelet', 'plt', 'thrombocyte'],
    'PCV': ['pcv', 'packed cell volume'],   # ✅ ADDED
    'Creatinine': ['creatinine'],
    'Cholesterol': ['cholesterol'],
    'HbA1c': ['hba1c', 'glycated'],
    'Bilirubin': ['bilirubin'],
    'Sodium': ['sodium', 'na+'],
    'Potassium': ['potassium', 'k+']
}


def keyword_match(line, keywords):
    for k in keywords:
        pattern = rf'\b{re.escape(k)}\b'
        if re.search(pattern, line):
            return True
    return False


def extract_medical_parameters(text: str) -> dict:
    """
    FINAL FIXED VERSION:
    ✔ Line-based parsing
    ✔ Context-aware extraction
    ✔ Prevents wrong values like 34.5
    """
    extracted = {}
    lines = text.split("\n")

    for param, keywords in PARAMETER_KEYWORDS.items():
        for line in lines:
            line_lower = line.lower()

            if keyword_match(line_lower, keywords):

                numbers = re.findall(r"\d+\.?\d*", line)

                if numbers:
                    try:
                        value = float(numbers[0])

                        # 🔥 VALIDATION RULES (VERY IMPORTANT)
                        if param == "Hemoglobin" and not (5 <= value <= 25):
                            continue
                        if param == "WBC" and not (1000 <= value <= 20000):
                            continue
                        if param == "Platelets" and not (10000 <= value <= 1000000):
                            continue
                        if param == "RBC" and not (3 <= value <= 8):
                            continue
                        if param == "PCV" and not (10 <= value <= 70):
                            continue

                        extracted[param] = value
                        break

                    except:
                        continue

    return extracted

# ═══════════════════════════════════════════════════════════════════════════════
# 5. RULE-BASED ANALYSIS ENGINE (FINAL FIXED VERSION)
# ═══════════════════════════════════════════════════════════════════════════════

NORMAL_RANGES = {
    'Hemoglobin': {
        'male':    {'low': 13.0, 'high': 17.0, 'unit': 'g/dL'},
        'female':  {'low': 12.0, 'high': 15.0, 'unit': 'g/dL'},
        'general': {'low': 12.0, 'high': 17.0, 'unit': 'g/dL'},
        'low_msg':    'Low hemoglobin suggests ANEMIA. May cause fatigue and weakness.',
        'high_msg':   'High hemoglobin may indicate dehydration.',
        'normal_msg': 'Hemoglobin is within the healthy range.',
    },

    'WBC': {
        'general': {'low': 4000, 'high': 11000, 'unit': 'cumm'},
        'low_msg':    'Low WBC. Immunity may be weak.',
        'high_msg':   'High WBC. Possible infection or inflammation.',
        'normal_msg': 'White blood cell count is normal.',
    },

    'RBC': {
        'male':    {'low': 4.5, 'high': 5.5, 'unit': 'mill/cumm'},
        'female':  {'low': 4.0, 'high': 5.0, 'unit': 'mill/cumm'},
        'general': {'low': 4.2, 'high': 5.5, 'unit': 'mill/cumm'},
        'low_msg':    'Low RBC may indicate anemia.',
        'high_msg':   'High RBC may indicate dehydration.',
        'normal_msg': 'Red blood cell count is normal.',
    },

    'Platelets': {
        'general': {'low': 150000, 'high': 410000, 'unit': 'cumm'},
        'low_msg':    'Low platelets. Risk of bleeding.',
        'high_msg':   'High platelets. Risk of clotting.',
        'normal_msg': 'Platelet count is within normal limits.',
    },

    # ✅ ADDED PCV (IMPORTANT)
    'PCV': {
        'general': {'low': 40, 'high': 50, 'unit': '%'},
        'low_msg':    'Low PCV may indicate anemia.',
        'high_msg':   'High PCV may indicate dehydration or blood disorder.',
        'normal_msg': 'PCV is within normal range.',
    },

    'Glucose': {
        'general': {'low': 70, 'high': 100, 'unit': 'mg/dL'},
        'low_msg':    'Low blood sugar.',
        'high_msg':   'High blood sugar (Diabetes risk).',
        'normal_msg': 'Blood sugar is normal.',
    },

    'Creatinine': {
        'general': {'low': 0.6, 'high': 1.3, 'unit': 'mg/dL'},
        'low_msg':    'Low creatinine.',
        'high_msg':   'High creatinine (Kidney issue).',
        'normal_msg': 'Creatinine is normal.',
    },
}


# ─────────────────────────────────────────────────────────────
# ANALYZE SINGLE PARAMETER (FINAL VERSION)
# ─────────────────────────────────────────────────────────────
def analyze_parameter(param_name: str, value: float, gender: str = 'general') -> dict:

    if param_name not in NORMAL_RANGES:
        return {
            'parameter': param_name,
            'status':    '⬜ UNKNOWN',
            'message':   'Parameter not supported.',
            'value':     value,
            'low':       None,
            'high':      None,
            'unit':      '',
        }

    ref = NORMAL_RANGES[param_name]

    # ✅ Use gender-specific range if available
    if gender in ref:
        ranges = ref[gender]
    else:
        ranges = ref['general']

    low_val  = ranges['low']
    high_val = ranges['high']
    unit     = ranges['unit']

    # ─── STATUS LOGIC ─────────────────────────────────────────

    # ✅ Platelets Borderline Fix
    if param_name == "Platelets":
        if value < low_val:
            status  = '🔴 LOW'
            message = ref['low_msg']
        elif value == low_val:
            status  = '🟡 BORDERLINE'
            message = 'Platelet count is at lower borderline.'
        elif value > high_val:
            status  = '🟡 HIGH'
            message = ref['high_msg']
        else:
            status  = '🟢 NORMAL'
            message = ref['normal_msg']

    # ✅ Normal Parameters
    else:
        if value < low_val:
            status  = '🔴 LOW'
            message = ref['low_msg']
        elif value > high_val:
            status  = '🟡 HIGH'
            message = ref['high_msg']
        else:
            status  = '🟢 NORMAL'
            message = ref['normal_msg']

    return {
        'parameter': param_name,
        'status':    status,
        'message':   message,
        'value':     value,
        'low':       low_val,
        'high':      high_val,
        'unit':      unit,
    }


# ─────────────────────────────────────────────────────────────
# ANALYZE ALL PARAMETERS
# ─────────────────────────────────────────────────────────────
def analyze_all_parameters(params: dict, gender: str = 'general') -> list:
    results = []

    for param, value in params.items():
        result = analyze_parameter(param, value, gender)
        results.append(result)

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 6. NLP EXPLANATION GENERATOR (Structured Prompt — FR5)
# ═══════════════════════════════════════════════════════════════════════════════

ADVICE_LIBRARY = {
    'Hemoglobin': {
        'LOW':  'Eat iron-rich foods like spinach, lentils, and meat. Rest well.',
        'HIGH': 'Drink plenty of water and avoid smoking.',
    },
    'Glucose': {
        'LOW':  'Eat or drink something sugary right away. Avoid skipping meals.',
        'HIGH': 'Reduce sugary foods, exercise regularly, and monitor sugar levels.',
    },
    'WBC': {
        'LOW':  'Avoid crowded places and maintain hygiene to reduce infection risk.',
        'HIGH': 'Rest, stay hydrated, and consult a doctor about possible infection.',
    },
    'RBC': {
        'LOW':  'Eat nutritious food. Consult your doctor about anemia.',
        'HIGH': 'Drink more water and get checked by a doctor.',
    },
    'Platelets': {
        'LOW':  'Avoid injury. See a doctor promptly if you notice unusual bruising.',
        'HIGH': 'Your doctor may need to monitor this closely for clot risk.',
    },
    'Creatinine': {
        'LOW':  'Generally not alarming but worth mentioning to your doctor.',
        'HIGH': 'Drink enough water and reduce high-protein foods until you see a doctor.',
    },
    'Cholesterol': {
        'HIGH': 'Eat less fried or fatty food. Walk for at least 30 minutes daily.',
    },
    'HbA1c': {
        'HIGH': 'Reduce sugary foods, exercise regularly, and see an endocrinologist.',
    },
    'Bilirubin': {
        'HIGH': 'Avoid alcohol and see a doctor. May indicate liver involvement.',
    },
    'Sodium': {
        'LOW':  'Increase salt intake slightly and consult a doctor.',
        'HIGH': 'Drink more water and reduce salty foods.',
    },
    'Potassium': {
        'LOW':  'Eat bananas, potatoes, and leafy greens. Consult a doctor.',
        'HIGH': 'Avoid high-potassium foods and seek medical care promptly.',
    },
}

REPORT_TYPE_HINTS = {
    frozenset(['Hemoglobin', 'WBC', 'RBC', 'Platelets']): 'Complete Blood Count (CBC)',
    frozenset(['Glucose', 'HbA1c']): 'Diabetes / Blood Sugar Panel',
    frozenset(['Creatinine']): 'Kidney Function Test (KFT)',
    frozenset(['Cholesterol', 'Bilirubin']): 'Liver & Lipid Panel',
    frozenset(['Sodium', 'Potassium']): 'Electrolyte Panel',
}


def _detect_report_type(results: list) -> str:
    param_set = set(r['parameter'] for r in results)
    for hint_set, name in REPORT_TYPE_HINTS.items():
        if hint_set.issubset(param_set):
            return name
    return 'Comprehensive Medical Panel' if len(param_set) >= 4 else 'Medical Lab Report'


def _status_word(status_str: str) -> str:
    for key in ('LOW', 'HIGH', 'NORMAL', 'UNKNOWN'):
        if key in status_str.upper():
            return key
    return 'UNKNOWN'


def generate_health_summary(results: list, patient_name: str = 'Patient',
                             gemini_api_key: str = None) -> str:
    """
    Generates a clear, user-friendly health report explanation from analysis results.

    Follows the structured AI prompt:
      1. Identify report type
      2. Per-parameter: name, value, status, simple explanation
      3. General health advice for abnormal values
      4. No specific medicines or prescriptions
      5. Always recommends consulting a doctor

    Args:
        results:         Output from analyze_all_parameters() or run_analysis()
        patient_name:    Patient name for the report header
        gemini_api_key:  Optional Gemini API key for AI-generated language

    Returns:
        str — human-readable medical summary
    """
    if gemini_api_key:
        return _gemini_summary(results, patient_name, gemini_api_key)
    return _rule_based_summary(results, patient_name)


def _rule_based_summary(results: list, patient_name: str) -> str:
    """Offline rule-based summary following the structured prompt."""
    report_type = _detect_report_type(results)
    abnormal    = [r for r in results if _status_word(r['status']) in ('LOW', 'HIGH')]

    lines = [
        '=' * 65,
        f'  🏥 HEALTH REPORT EXPLANATION — {patient_name.upper()}',
        f'  📋 Report Type : {report_type}',
        '=' * 65,
        '',
        f'Dear {patient_name},',
        '',
        f'Below is a simple explanation of your {report_type} results.',
        'This is written in plain language to help you understand your health status.',
        '',
        '-' * 65,
        '📌 PARAMETER-BY-PARAMETER EXPLANATION',
        '-' * 65,
    ]

    emoji_map = {'NORMAL': '🟢', 'HIGH': '🟡', 'LOW': '🔴', 'UNKNOWN': '⬜'}

    for r in results:
        sw    = _status_word(r['status'])
        emoji = emoji_map.get(sw, '⬜')
        lines += [
            '',
            f"{emoji} {r['parameter']}",
            f"   Measured Value : {r['value']} {r['unit']}",
            f"   Normal Range   : {r['low']} – {r['high']} {r['unit']}",
            f"   Status         : {sw}",
        ]
        if sw == 'NORMAL':
            lines.append(
                f"   Meaning        : ✅ Your {r['parameter']} is within the healthy range. No concern."
            )
        elif sw in ADVICE_LIBRARY.get(r['parameter'], {}):
            lines.append(
                f"   Meaning        : ⚠️  {ADVICE_LIBRARY[r['parameter']][sw]}"
            )
        else:
            lines.append(
                f"   Meaning        : This value is {sw.lower()} — discuss with your doctor."
            )

    # Health advice section
    lines += ['', '-' * 65, '💡 GENERAL HEALTH ADVICE', '-' * 65, '']

    if abnormal:
        lines.append('Based on the abnormal values found in your report:')
        lines.append('')
        seen = set()
        for r in abnormal:
            sw = _status_word(r['status'])
            tip = ADVICE_LIBRARY.get(r['parameter'], {}).get(sw)
            if tip and tip not in seen:
                lines.append(f'  • {tip}')
                seen.add(tip)
        lines += [
            '',
            'General tips for everyone:',
        ]
    else:
        lines += [
            '✅ All tested parameters are within normal limits. Great result!',
            '',
            'To maintain your good health:',
        ]

    lines += [
        '  • Drink at least 8 glasses of water per day',
        '  • Eat a balanced diet with vegetables, fruits, and whole grains',
        '  • Get at least 30 minutes of light physical activity daily',
        '  • Avoid smoking and excessive alcohol',
        '  • Get regular health check-ups',
        '',
        '=' * 65,
        '👨‍⚕️  IMPORTANT — PLEASE CONSULT YOUR DOCTOR',
        '=' * 65,
        '',
        'This explanation is generated by an AI system for informational',
        'purposes only. It does NOT replace professional medical advice.',
        '',
        '⚠️  Please consult a qualified doctor or healthcare provider to:',
        '   • Confirm the diagnosis',
        '   • Understand results in the context of your full health history',
        '   • Get appropriate treatment if needed',
        '',
        '❌ Do NOT self-medicate based on these results.',
        '=' * 65,
    ]

    return '\n'.join(lines)


def _gemini_summary(results: list, patient_name: str, api_key: str) -> str:
    """Uses Google Gemini API to generate the explanation."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        params_text = '\n'.join([
            f"- {r['parameter']}: {r['value']} {r['unit']} "
            f"→ Status: {_status_word(r['status'])} "
            f"(Normal: {r['low']}–{r['high']})"
            for r in results
        ])

        prompt = (
            "You are an AI-based medical assistant.\n\n"
            "Analyze the given medical report results and generate a clear, simple, "
            "and user-friendly explanation suitable for a non-technical person.\n\n"
            "Instructions:\n"
            "1. Identify the type of report (e.g., Complete Blood Count - CBC).\n"
            "2. For each parameter, mention:\n"
            "   - Parameter name\n"
            "   - Measured value\n"
            "   - Status (Low / Normal / High)\n"
            "   - Simple interpretation of the result\n"
            "3. Provide general health advice based on abnormal values.\n"
            "4. Do not suggest any specific medicines or prescriptions.\n"
            "5. Keep the explanation concise and easy to understand.\n"
            "6. Always include a final recommendation to consult a qualified doctor.\n\n"
            f"Patient Name: {patient_name}\n\n"
            f"Input (Structured Medical Parameters):\n{params_text}\n\n"
            "Output:\nA natural language summary explaining the report and basic health advice."
        )

        response = model.generate_content(prompt)
        return response.text

    except ImportError:
        return _rule_based_summary(results, patient_name)
    except Exception:
        return _rule_based_summary(results, patient_name)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MAIN PIPELINE — run_analysis() (used by app.py)
# ═══════════════════════════════════════════════════════════════════════════════

def run_analysis(file_path: str, patient_name: str = 'Patient',
                 gender: str = 'general', plot: bool = False) -> list:
    """
    Full end-to-end pipeline:
      Upload → Detect Type → Extract Text → Parse Parameters → Analyze

    Args:
        file_path:    Path to PDF or image medical report
        patient_name: Patient name (for display)
        gender:       'male', 'female', or 'general'
        plot:         If True, generates a matplotlib bar chart

    Returns:
        list[dict] — analysis results, one dict per parameter
    """
    # Step 1 — Detect file type
    file_type = detect_file_type(file_path)

    # Step 2 — Extract text
    if file_type == 'pdf':
        report_info = extract_text_from_pdf(file_path)
    elif file_type == 'image':
        report_info = extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use PDF, JPG, or PNG.")

    raw_text = report_info['text']

    # Step 3 — Extract parameters
    params = extract_medical_parameters(raw_text)

    # Step 4 — Analyze
    results = analyze_all_parameters(params, gender=gender)

    # Step 5 — Optional chart
    if plot and results:
        _plot_results(results, patient_name)

    return results


def _plot_results(results: list, patient_name: str = 'Patient'):
    """Generates and saves a bar chart of results (optional, requires matplotlib)."""
    try:
        import matplotlib.pyplot as plt

        plottable = [r for r in results if r['low'] is not None and r['low'] >= 0]
        if not plottable:
            return

        fig, axes = plt.subplots(1, len(plottable), figsize=(4 * len(plottable), 5))
        if len(plottable) == 1:
            axes = [axes]

        color_map = {'NORMAL': '#2ecc71', 'HIGH': '#e67e22', 'LOW': '#e74c3c'}

        for ax, r in zip(axes, plottable):
            sw    = _status_word(r['status'])
            color = color_map.get(sw, '#3498db')
            ax.axhspan(r['low'], r['high'], alpha=0.15, color='#2ecc71')
            ax.bar(r['parameter'], r['value'], color=color, alpha=0.85, width=0.5)
            ax.axhline(r['low'],  color='#27ae60', linestyle='--', linewidth=1, alpha=0.7)
            ax.axhline(r['high'], color='#e74c3c', linestyle='--', linewidth=1, alpha=0.7)
            ax.set_title(f"{r['parameter']}\n{r['status']}", fontsize=10, fontweight='bold')
            ax.set_ylabel(r['unit'], fontsize=9)
            ax.set_xticks([])
            ax.text(0, r['value'] * 1.02, str(r['value']),
                    ha='center', fontweight='bold', fontsize=11, color=color)

        plt.suptitle(f'Medical Report — {patient_name}', fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig('analysis_results.png', dpi=150, bbox_inches='tight')
        plt.close()
    except ImportError:
        pass  # matplotlib not available — skip chart silently
