import os
import re
import warnings
warnings.filterwarnings('ignore')

try:
    import fitz  
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

# 1. FILE TYPE DETECTION

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


# 2. PDF EXTRACTION — PyMuPDF (FR1)

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extracts text from a PDF medical report using PyMuPDF (fitz).
    No OCR required — fast and accurate for digital PDFs.
    """

    if not _HAS_FITZ:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(pdf_path)

    full_text = ''
    for page in doc:
        full_text += page.get_text() + '\n'

    try:
        pages = len(doc)   
    except:
        pages = 1

    doc.close()

    return {
        'text': full_text,
        'pages': pages,
        'extraction_method': 'PyMuPDF (Direct — No OCR)',
        'file_name': os.path.basename(pdf_path),
        'file_type': 'pdf',
    }
    
# 3. OCR EXTRACTION — pytesseract / EasyOCR (FR2)

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


# 3.5 SCANNED PDF EXTRACTION — Using pdf2image

def extract_text_from_scanned_pdf(pdf_path: str) -> dict:
    """
    Extracts text from a scanned/image-based PDF by converting each page to an image
    and then applying OCR.
    
    Requires: pip install pdf2image
    Mac only: brew install poppler
    Linux: sudo apt-get install poppler-utils
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError("pdf2image not installed. Run: pip install pdf2image")
    
    full_text = ""
    images = convert_from_path(pdf_path)

    for i, img in enumerate(images):
        temp_path = f"temp_page_{i}.png"
        img.save(temp_path, "PNG")

        ocr_result = extract_text_from_image(temp_path)
        full_text += ocr_result['text'] + "\n"

        os.remove(temp_path)

    return {
        'text': full_text,
        'pages': len(images),
        'extraction_method': 'OCR via pdf2image + Tesseract/EasyOCR',
        'file_name': os.path.basename(pdf_path),
        'file_type': 'pdf',
    }


# 4. DATA EXTRACTION — FINAL FIXED VERSION (CRITICAL: Handles "Total Count")

def extract_patient_info(text: str) -> dict:
    """
    Extracts patient name and age from OCR or PDF text.
    """
    patient_info = {'name': 'Patient', 'age': None}
    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Try to extract name (common patterns)
        if 'name' in line_lower:
            # Look for name on current line after "Name:"
            if ':' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    potential_name = parts[1].strip()
                    # Filter out common non-name words
                    if potential_name and len(potential_name) > 2 and potential_name not in ['patient', 'name', 'mr', 'mrs', 'ms']:
                        patient_info['name'] = potential_name
                    else:
                        # If colon present but no name after it, try next line
                        if i + 1 < len(lines):
                            potential_name = lines[i + 1].strip()
                            if potential_name and len(potential_name) > 2 and potential_name not in ['patient', 'name', 'mr', 'mrs', 'ms', 'registration', 'date']:
                                patient_info['name'] = potential_name
            else:
                # Try next line if no colon on current line
                if i + 1 < len(lines):
                    potential_name = lines[i + 1].strip()
                    if potential_name and len(potential_name) > 2 and potential_name not in ['patient', 'name', 'mr', 'mrs', 'ms', 'registration', 'date']:
                        patient_info['name'] = potential_name
        
        # Try to extract age
        age_match = re.search(r'age\s*[:\-]?\s*(\d+)', line_lower)
        if age_match:
            patient_info['age'] = int(age_match.group(1))
        
        # Also look for age patterns like "23 years", "23 yrs", "23y"
        age_pattern = re.search(r'(\d+)\s*(years?|yrs?|y)', line_lower)
        if age_pattern:
            patient_info['age'] = int(age_pattern.group(1))
        
        # Look for Age/Sex pattern like "23 Years/Male"
        age_sex_pattern = re.search(r'(\d+)\s+years?', line_lower)
        if age_sex_pattern:
            patient_info['age'] = int(age_sex_pattern.group(1))
    
    return patient_info


def extract_medical_parameters(text: str) -> dict:
    """
    Extracts medical parameters from OCR or PDF text.
    
    CRITICAL FIX: Now properly handles multi-line parameter-value pairs
    """
    extracted = {}

    # Fix comma numbers (e.g., 44,000 → 44000)
    text = text.replace(",", "")
    lines = text.split("\n")
    
    print("🔍 Scanning for medical parameters...")

    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Look ahead to next line for value (multi-line format)
        next_line = lines[i + 1] if i + 1 < len(lines) else ""

        # Hemoglobin - Updated to match "Haemoglobin:" format with value on next line
        if "hemoglobin" in line_lower or "haemoglobin" in line_lower:
            # Try current line first
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                # Try next line
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                # Validation range
                if 5 <= value <= 25:
                    extracted["Hemoglobin"] = value
                    print(f"   ✅ Found Hemoglobin: {value}")

        # RBC - Updated to match "RBC Count:" format with value on next line
        elif "rbc" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 2 <= value <= 8:  # Expanded range
                    extracted["RBC"] = value
                    print(f"   ✅ Found RBC: {value}")

        # WBC - CRITICAL FIX: Looks for "Total Count" which is common in reports
        elif "total count" in line_lower or "total leucocyte" in line_lower or "wbc" in line_lower:
            match = re.search(r"(\d+)", line)
            if not match:
                match = re.search(r"(\d+)", next_line)
            if match:
                value = float(match.group(1))
                # Wider range to capture all valid WBC values
                if 1000 <= value <= 50000:
                    extracted["WBC"] = value
                    print(f"   ✅ Found WBC: {value} (from: {line[:50]})")

        # Platelets
        elif "platelet" in line_lower:
            match = re.search(r"(\d+)", line)
            if not match:
                match = re.search(r"(\d+)", next_line)
            if match:
                value = float(match.group(1))
                if 10000 <= value <= 1000000:
                    extracted["Platelets"] = value
                    print(f"   ✅ Found Platelets: {value}")

        # PCV / HCT - Updated to match "HCT:" format with value on next line
        elif "pcv" in line_lower or "hct" in line_lower or "hematocrit" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 10 <= value <= 70:
                    extracted["PCV"] = value
                    print(f"   ✅ Found PCV: {value}")

        # Glucose
        elif "glucose" in line_lower or "sugar" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 30 <= value <= 500:
                    extracted["Glucose"] = value
                    print(f"   ✅ Found Glucose: {value}")

        # Creatinine
        elif "creatinine" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 0.3 <= value <= 10:
                    extracted["Creatinine"] = value
                    print(f"   ✅ Found Creatinine: {value}")

        # MCV
        elif "mcv" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 50 <= value <= 150:
                    extracted["MCV"] = value
                    print(f"   ✅ Found MCV: {value}")

        # MCH
        elif "mch" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 15 <= value <= 50:
                    extracted["MCH"] = value
                    print(f"   ✅ Found MCH: {value}")

        # CRP
        elif "crp" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 0 <= value <= 200:
                    extracted["CRP"] = value
                    print(f"   ✅ Found CRP: {value}")

        # ESR
        elif "esr" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 0 <= value <= 100:
                    extracted["ESR"] = value
                    print(f"   ✅ Found ESR: {value}")

        # HbA1c
        elif "hba1c" in line_lower or "glycated" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 3 <= value <= 15:
                    extracted["HbA1c"] = value
                    print(f"   ✅ Found HbA1c: {value}")

        # Urine Sugar
        elif "urine" in line_lower and "sugar" in line_lower:
            if "absent" in line_lower or "negative" in line_lower or "nil" in line_lower:
                extracted["Urine Sugar"] = 0
                print(f"   ✅ Found Urine Sugar: Absent")
            elif "present" in line_lower or "positive" in line_lower or "trace" in line_lower:
                extracted["Urine Sugar"] = 1
                print(f"   ✅ Found Urine Sugar: Present")

        # IgE
        elif "ige" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 0 <= value <= 2000:
                    extracted["IgE"] = value
                    print(f"   ✅ Found IgE: {value}")

        # eGFR
        elif "egfr" in line_lower or "gfr" in line_lower:
            match = re.search(r"(\d+\.?\d*)", line)
            if not match:
                match = re.search(r"(\d+\.?\d*)", next_line)
            if match:
                value = float(match.group(1))
                if 5 <= value <= 150:
                    extracted["eGFR"] = value
                    print(f"   ✅ Found eGFR: {value}")

        # Blood Culture
        elif "blood culture" in line_lower or "culture" in line_lower:
            if "no growth" in line_lower or "negative" in line_lower or "sterile" in line_lower:
                extracted["Blood Culture"] = 0
                print(f"   ✅ Found Blood Culture: No Growth")
            elif "growth" in line_lower or "positive" in line_lower:
                extracted["Blood Culture"] = 1
                print(f"   ✅ Found Blood Culture: Growth Detected")

    print(f"📊 Total parameters extracted: {len(extracted)}")
    return extracted


# 5. RULE-BASED ANALYSIS ENGINE

# Updated reference ranges with severity thresholds
NORMAL_RANGES = {
    'Hemoglobin': {
        'male':    {'low': 13.0, 'high': 17.0, 'unit': 'g/dL'},
        'female':  {'low': 12.0, 'high': 15.0, 'unit': 'g/dL'},
        'general': {'low': 12.0, 'high': 17.0, 'unit': 'g/dL'},
        'very_low': 7.0,
        'slight_low': 11.0,
        'slight_high': 18.0,
    },
    'RBC': {
        'male':    {'low': 4.5, 'high': 5.9, 'unit': 'M/μL'},
        'female':  {'low': 4.1, 'high': 5.1, 'unit': 'M/μL'},
        'general': {'low': 4.1, 'high': 5.9, 'unit': 'M/μL'},
    },
    'PCV': {
        'male':    {'low': 40.0, 'high': 50.0, 'unit': '%'},
        'female':  {'low': 36.0, 'high': 46.0, 'unit': '%'},
        'general': {'low': 36.0, 'high': 50.0, 'unit': '%'},
    },
    'MCV': {
        'general': {'low': 80.0, 'high': 100.0, 'unit': 'fL'},
        'slight_high': 100.0,
        'very_low': 80.0,
    },
    'MCH': {
        'general': {'low': 27.0, 'high': 32.0, 'unit': 'pg'},
    },
    'WBC': {
        'general': {'low': 4000, 'high': 11000, 'unit': '/μL'},
        'very_low': 2000,
        'extremely_low': 2000,
    },
    'Platelets': {
        'general': {'low': 150000, 'high': 400000, 'unit': '/μL'},
        'critical_low': 50000,
    },
    'CRP': {
        'general': {'low': 0, 'high': 5.0, 'unit': 'mg/L'},
        'slight_high': 50.0,
        'very_high': 50.0,
    },
    'ESR': {
        'male':    {'low': 0, 'high': 15.0, 'unit': 'mm/hr'},
        'female':  {'low': 0, 'high': 20.0, 'unit': 'mm/hr'},
        'general': {'low': 0, 'high': 20.0, 'unit': 'mm/hr'},
    },
    'HbA1c': {
        'general': {'low': 0, 'high': 5.7, 'unit': '%'},
        'prediabetes': 6.4,
    },
    'Urine Sugar': {
        'general': {'low': 0, 'high': 0, 'unit': ''},
    },
    'IgE': {
        'general': {'low': 0, 'high': 100, 'unit': 'IU/mL'},
        'very_high': 500,
    },
    'eGFR': {
        'general': {'low': 60, 'high': 120, 'unit': 'mL/min'},
    },
    'Blood Culture': {
        'general': {'low': 0, 'high': 0, 'unit': ''},
    },
    'Glucose': {
        'general': {'low': 70, 'high': 100, 'unit': 'mg/dL'},
    },
    'Creatinine': {
        'general': {'low': 0.6, 'high': 1.3, 'unit': 'mg/dL'},
    },
}


def analyze_parameter_with_severity(param_name: str, value: float, gender: str = 'general') -> dict:
    """Analyzes a single parameter against normal ranges with severity indicators."""

    if param_name not in NORMAL_RANGES:
        return {
            'parameter': param_name,
            'status':    '⚪ UNKNOWN',
            'severity':  'UNKNOWN',
            'value':     value,
            'unit':      '',
        }

    ref = NORMAL_RANGES[param_name]

    if gender in ref and isinstance(ref[gender], dict):
        ranges = ref[gender]
    else:
        ranges = ref['general']

    low_val  = ranges['low']
    high_val = ranges['high']
    unit     = ranges['unit']

    # Determine severity based on parameter-specific rules
    status = '🟢 NORMAL'
    severity = 'NORMAL'
    
    if param_name == 'Hemoglobin':
        if value < ref.get('very_low', 7.0):
            status = '🚨 VERY LOW'
            severity = 'CRITICAL'
        elif value < low_val:
            if value >= ref.get('slight_low', 11.0):
                status = '🟡 Slight LOW'
                severity = 'SLIGHT'
            else:
                status = '🔴 LOW'
                severity = 'HIGH'
        elif value > high_val:
            if value <= ref.get('slight_high', 18.0):
                status = '🟡 Slight HIGH'
                severity = 'SLIGHT'
            else:
                status = '🔴 HIGH'
                severity = 'HIGH'
    
    elif param_name == 'RBC':
        if value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'PCV':
        if value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'MCV':
        if value < ref.get('very_low', 80.0):
            status = '🔴 LOW (Microcytic)'
            severity = 'HIGH'
        elif value > high_val:
            status = '🟡 HIGH (Macrocytic)'
            severity = 'SLIGHT'
    
    elif param_name == 'MCH':
        if value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'WBC':
        if value < ref.get('extremely_low', 2000):
            status = '🚨 EXTREMELY LOW'
            severity = 'CRITICAL'
        elif value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'Platelets':
        if value < ref.get('critical_low', 50000):
            status = '� CRITICAL LOW'
            severity = 'CRITICAL'
        elif value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'CRP':
        if value > ref.get('very_high', 50.0):
            status = '🚨 VERY HIGH'
            severity = 'CRITICAL'
        elif value > high_val:
            if value <= ref.get('slight_high', 50.0):
                status = '🟡 HIGH'
                severity = 'SLIGHT'
            else:
                status = '🔴 HIGH'
                severity = 'HIGH'
    
    elif param_name == 'ESR':
        if value > high_val:
            status = '🟡 HIGH'
            severity = 'SLIGHT'
    
    elif param_name == 'HbA1c':
        if value <= high_val:
            status = '🟢 NORMAL'
            severity = 'NORMAL'
        elif value <= ref.get('prediabetes', 6.4):
            status = '🟡 PREDIABETES'
            severity = 'SLIGHT'
        else:
            status = '🔴 DIABETES'
            severity = 'HIGH'
    
    elif param_name == 'Urine Sugar':
        if value > 0:
            status = '🟡 ABNORMAL'
            severity = 'SLIGHT'
    
    elif param_name == 'IgE':
        if value > ref.get('very_high', 500):
            status = '🚨 VERY HIGH'
            severity = 'CRITICAL'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'
    
    elif param_name == 'eGFR':
        if value < low_val:
            status = '🟡 Kidney Impairment'
            severity = 'SLIGHT'
    
    elif param_name == 'Blood Culture':
        if value == 0:
            status = '🟢 No Infection Detected'
            severity = 'NORMAL'
        else:
            status = '🔴 Infection Detected'
            severity = 'HIGH'
    
    else:
        # Generic handling for other parameters
        if value < low_val:
            status = '🔴 LOW'
            severity = 'HIGH'
        elif value > high_val:
            status = '🔴 HIGH'
            severity = 'HIGH'

    return {
        'parameter': param_name,
        'status': status,
        'severity': severity,
        'value': value,
        'unit': unit,
        'low': low_val,
        'high': high_val,
    }


def analyze_all_parameters(params: dict, gender: str = 'general') -> list:
    """Analyzes all extracted parameters with severity indicators."""
    results = []

    for param, value in params.items():
        result = analyze_parameter_with_severity(param, value, gender)
        results.append(result)

    return results


# 6. DIAGNOSIS PATTERN MATCHING

def generate_diagnosis(results: list) -> str:
    """
    Generates a one-line primary diagnosis based on parameter patterns.
    Combines multiple findings for comprehensive diagnosis.
    """
    # Create a dictionary of parameter values and severities for easy lookup
    params = {}
    for r in results:
        params[r['parameter']] = {
            'value': r['value'],
            'severity': r['severity'],
            'status': r['status']
        }
    
    diagnosis_parts = []
    
    # Check for Macrocytic Anemia pattern first (Hb LOW + MCV HIGH)
    if ('Hemoglobin' in params and 'LOW' in params['Hemoglobin']['status']) and \
       ('MCV' in params and 'HIGH' in params['MCV']['status']):
        if params['Hemoglobin']['severity'] == 'CRITICAL':
            diagnosis_parts.append('🚨 Severe Macrocytic Anemia')
        else:
            diagnosis_parts.append('🔴 Macrocytic Anemia')
    
    # Check for Iron Deficiency / Microcytic Anemia (Hb LOW + MCV LOW + MCH LOW)
    elif ('Hemoglobin' in params and 'LOW' in params['Hemoglobin']['status']) and \
         ('MCV' in params and 'LOW' in params['MCV']['status']) and \
         ('MCH' in params and 'LOW' in params['MCH']['status']):
        diagnosis_parts.append('🔴 Iron Deficiency / Microcytic Anemia')
    
    # Check for Pancytopenia (WBC LOW + Platelets LOW + Hb LOW) - only if not already diagnosed as macrocytic
    if ('WBC' in params and 'LOW' in params['WBC']['status']) and \
       ('Platelets' in params and 'LOW' in params['Platelets']['status']) and \
       ('Hemoglobin' in params and 'LOW' in params['Hemoglobin']['status']):
        if 'Macrocytic' not in ' '.join(diagnosis_parts):
            diagnosis_parts.append('🚨 Pancytopenia (🚨 URGENT)')
    
    # Check for Bone marrow issue (Hb LOW + Platelets LOW + WBC LOW)
    elif ('Hemoglobin' in params and 'LOW' in params['Hemoglobin']['status']) and \
         ('Platelets' in params and 'LOW' in params['Platelets']['status']) and \
         ('WBC' in params and 'LOW' in params['WBC']['status']):
        diagnosis_parts.append('🚨 Bone marrow issue / Severe condition')
    
    # Check for Severe infection/sepsis (CRP VERY HIGH + LOW ALL)
    if ('CRP' in params and params['CRP']['severity'] == 'CRITICAL') and \
       sum(1 for p in ['WBC', 'Platelets', 'Hemoglobin'] if p in params and 'LOW' in params[p]['status']) >= 2:
        diagnosis_parts.append('🚨 Severe infection/sepsis')
    
    # Check for Allergy/Parasitic infection (IgE VERY HIGH)
    if 'IgE' in params and params['IgE']['severity'] == 'CRITICAL':
        diagnosis_parts.append('🚨 Allergy/Parasitic infection')
    
    # Check for Early diabetes / Temporary glycosuria (Urine Sugar + Normal HbA1c)
    if 'Urine Sugar' in params and params['Urine Sugar']['severity'] == 'SLIGHT' and \
       ('HbA1c' not in params or params['HbA1c']['severity'] == 'NORMAL'):
        diagnosis_parts.append('🟡 Early diabetes / Temporary glycosuria')
    
    # Check for Mild inflammation (CRP HIGH + WBC NORMAL)
    if 'CRP' in params and params['CRP']['severity'] in ['SLIGHT', 'HIGH'] and \
       ('WBC' not in params or params['WBC']['severity'] == 'NORMAL'):
        diagnosis_parts.append('🟡 Mild inflammation')
    
    # Individual critical conditions
    if 'Platelets' in params and params['Platelets']['severity'] == 'CRITICAL':
        diagnosis_parts.append('🚨 Critical Platelet Count')
    
    if 'Hemoglobin' in params and params['Hemoglobin']['severity'] == 'CRITICAL':
        diagnosis_parts.append('🚨 Severe Anemia')
    
    if 'WBC' in params and params['WBC']['severity'] == 'CRITICAL':
        diagnosis_parts.append('🚨 Severe Leukopenia')
    
    # Individual high severity conditions
    if 'Platelets' in params and params['Platelets']['severity'] == 'HIGH' and 'LOW' in params['Platelets']['status']:
        diagnosis_parts.append('🔴 Low Platelets')
    
    if 'WBC' in params and params['WBC']['severity'] == 'HIGH' and 'LOW' in params['WBC']['status']:
        diagnosis_parts.append('🔴 Low Immunity')
    
    # Diabetes (HbA1c HIGH)
    if 'HbA1c' in params and params['HbA1c']['severity'] == 'HIGH':
        diagnosis_parts.append('🔴 Diabetes')
    
    # Prediabetes (HbA1c SLIGHT)
    if 'HbA1c' in params and params['HbA1c']['severity'] == 'SLIGHT':
        diagnosis_parts.append('🟡 Prediabetes')
    
    # Kidney Impairment (eGFR LOW)
    if 'eGFR' in params and params['eGFR']['severity'] == 'SLIGHT':
        diagnosis_parts.append('🟡 Kidney Impairment')
    
    # Anemia (Hb LOW) - if not already covered
    if 'Hemoglobin' in params and 'LOW' in params['Hemoglobin']['status'] and \
       'Anemia' not in ' '.join(diagnosis_parts):
        diagnosis_parts.append('🔴 Anemia')
    
    # Low Immunity (WBC LOW) - if not already covered
    if 'WBC' in params and 'LOW' in params['WBC']['status'] and \
       'Immunity' not in ' '.join(diagnosis_parts) and 'Leukopenia' not in ' '.join(diagnosis_parts):
        diagnosis_parts.append('🔴 Low Immunity')
    
    # If no abnormal findings
    if not diagnosis_parts:
        abnormal_count = sum(1 for r in results if r['severity'] != 'NORMAL')
        if abnormal_count == 0:
            return '🟢 Normal Health'
        diagnosis_parts.append('🟡 Abnormal Findings')
    
    # Combine diagnosis parts with + separator
    return ' + '.join(diagnosis_parts)


def generate_interpretation(results: list, diagnosis: str) -> str:
    """
    Generates a 2-3 line explanation of what the findings mean.
    """
    abnormal = [r for r in results if r['severity'] != 'NORMAL']
    
    if not abnormal:
        return "All parameters are within normal range. No significant health concerns detected based on this report."
    
    # Build interpretation based on combined diagnosis
    if 'Macrocytic Anemia' in diagnosis and 'Critical Platelet' in diagnosis and 'Low Immunity' in diagnosis:
        mcv = next((r for r in results if r['parameter'] == 'MCV'), None)
        hb = next((r for r in results if r['parameter'] == 'Hemoglobin'), None)
        plt = next((r for r in results if r['parameter'] == 'Platelets'), None)
        wbc = next((r for r in results if r['parameter'] == 'WBC'), None)
        return f"Macrocytic anemia (MCV {mcv['value'] if mcv else 'high'} fL + Hb {hb['value'] if hb else 'low'} g/dL) + dangerous platelet level ({plt['value'] if plt else 'low'}/μL) + low WBC ({wbc['value'] if wbc else 'low'}/μL) → bleeding risk + weakened immunity"
    
    elif 'Pancytopenia' in diagnosis:
        return "Dangerously low levels of all blood cell types indicate possible bone marrow failure or severe systemic condition. Immediate medical intervention is critical to prevent life-threatening complications."
    
    elif 'sepsis' in diagnosis.lower():
        return "Severe inflammation markers combined with low blood cells suggest a serious systemic infection. This condition requires immediate hospitalization and aggressive antibiotic treatment."
    
    elif 'Macrocytic Anemia' in diagnosis:
        mcv = next((r for r in results if r['parameter'] == 'MCV'), None)
        hb = next((r for r in results if r['parameter'] == 'Hemoglobin'), None)
        return f"Large red blood cells (MCV {mcv['value'] if mcv else 'high'} fL) with low hemoglobin ({hb['value'] if hb else 'low'} g/dL) indicate Vitamin B12 or folate deficiency. This can cause fatigue and neurological symptoms if untreated."
    
    elif 'Iron Deficiency' in diagnosis:
        hb = next((r for r in results if r['parameter'] == 'Hemoglobin'), None)
        return f"Small red blood cells with low hemoglobin ({hb['value'] if hb else 'low'} g/dL) suggest iron deficiency anemia. Common causes include poor diet, blood loss, or malabsorption."
    
    elif 'Bone marrow' in diagnosis:
        return "Simultaneous low levels of hemoglobin, platelets, and white blood cells suggest bone marrow dysfunction. This may be due to infections, medications, or blood disorders requiring specialist evaluation."
    
    elif 'Allergy' in diagnosis:
        ige = next((r for r in results if r['parameter'] == 'IgE'), None)
        return f"Extremely elevated IgE ({ige['value'] if ige else 'high'} IU/mL) indicates severe allergic reaction or parasitic infection. Identify and avoid allergens; consider antiparasitic treatment if indicated."
    
    elif 'diabetes' in diagnosis.lower() and 'Early' in diagnosis:
        return "Sugar in urine with normal HbA1c suggests early-stage diabetes or temporary glycosuria. Monitor blood sugar levels and reduce sugar intake to prevent progression."
    
    elif 'Mild inflammation' in diagnosis:
        crp = next((r for r in results if r['parameter'] == 'CRP'), None)
        return f"Elevated CRP ({crp['value'] if crp else 'high'} mg/L) with normal white blood cells suggests mild inflammation or early infection. Monitor for symptoms and stay hydrated."
    
    elif 'Thrombocytopenia' in diagnosis or 'Critical Platelet' in diagnosis:
        plt = next((r for r in results if r['parameter'] == 'Platelets'), None)
        return f"Critically low platelet count ({plt['value'] if plt else 'low'}/μL) creates high bleeding risk. Avoid injury, contact sports, and seek immediate medical attention."
    
    elif 'Severe Anemia' in diagnosis:
        hb = next((r for r in results if r['parameter'] == 'Hemoglobin'), None)
        return f"Very low hemoglobin ({hb['value'] if hb else 'low'} g/dL) indicates severe anemia requiring urgent medical evaluation. May cause extreme fatigue, shortness of breath, and chest pain."
    
    elif 'Leukopenia' in diagnosis:
        wbc = next((r for r in results if r['parameter'] == 'WBC'), None)
        return f"Extremely low white blood cell count ({wbc['value'] if wbc else 'low'}/μL) severely compromises immune system. High risk of infections; avoid crowds and seek immediate medical care."
    
    elif 'Diabetes' in diagnosis:
        hba1c = next((r for r in results if r['parameter'] == 'HbA1c'), None)
        return f"Elevated HbA1c ({hba1c['value'] if hba1c else 'high'}%) indicates diabetes. Requires lifestyle changes, dietary modifications, and likely medication under doctor's supervision."
    
    elif 'Prediabetes' in diagnosis:
        hba1c = next((r for r in results if r['parameter'] == 'HbA1c'), None)
        return f"HbA1c ({hba1c['value'] if hba1c else 'high'}%) in prediabetes range indicates high diabetes risk. Lifestyle changes can reverse this condition."
    
    elif 'Kidney Impairment' in diagnosis:
        egfr = next((r for r in results if r['parameter'] == 'eGFR'), None)
        return f"Reduced eGFR ({egfr['value'] if egfr else 'low'} mL/min) suggests decreased kidney function. Requires hydration, avoid nephrotoxic medications, and medical follow-up."
    
    elif 'Anemia' in diagnosis:
        hb = next((r for r in results if r['parameter'] == 'Hemoglobin'), None)
        return f"Low hemoglobin ({hb['value'] if hb else 'low'} g/dL) indicates anemia. May cause fatigue, weakness, and pale skin. Investigate iron deficiency or other causes."
    
    elif 'Low Immunity' in diagnosis:
        wbc = next((r for r in results if r['parameter'] == 'WBC'), None)
        return f"Low white blood cell count ({wbc['value'] if wbc else 'low'}/μL) indicates weakened immune system. Increased susceptibility to infections; boost immunity with rest and nutrition."
    
    else:
        # Generic interpretation for abnormal findings
        param_names = ', '.join([r['parameter'] for r in abnormal[:3]])
        return f"Abnormal levels in {param_names} indicate potential health issues. Further evaluation by a healthcare provider is recommended for accurate diagnosis and treatment."


def generate_advice(results: list, diagnosis: str) -> str:
    """
    Generates specific actionable advice based on severity.
    """
    critical = [r for r in results if r['severity'] == 'CRITICAL']
    high = [r for r in results if r['severity'] == 'HIGH']
    slight = [r for r in results if r['severity'] == 'SLIGHT']
    
    # Special handling for combined diagnosis patterns
    if 'Macrocytic Anemia' in diagnosis and 'Critical Platelet' in diagnosis and 'Low Immunity' in diagnosis:
        return 'Immediate doctor consultation ❗ + Vitamin B12 diet + Avoid injury'
    
    if critical:
        advice_parts = []
        for r in critical:
            if r['parameter'] == 'Platelets':
                advice_parts.append('Immediate doctor consultation ❗ + Avoid injury/Contact sports')
            elif r['parameter'] == 'Hemoglobin':
                advice_parts.append('Emergency medical attention ❗ + Possible blood transfusion')
            elif r['parameter'] == 'WBC':
                advice_parts.append('Immediate hospitalization ❗ + Isolation from infections')
            elif r['parameter'] == 'CRP':
                advice_parts.append('Emergency care ❗ + Antibiotic treatment')
            elif r['parameter'] == 'IgE':
                advice_parts.append('Allergist consultation ❗ + Identify allergens')
        return ' | '.join(advice_parts)
    
    elif high:
        advice_parts = []
        for r in high:
            if r['parameter'] == 'Hemoglobin':
                advice_parts.append('Doctor consultation + Iron-rich diet + Vitamin C')
            elif r['parameter'] == 'WBC':
                advice_parts.append('Doctor consultation + Boost immunity + Rest')
            elif r['parameter'] == 'Platelets':
                advice_parts.append('Doctor consultation + Avoid injury + Monitor bleeding')
            elif r['parameter'] == 'MCV' and 'LOW' in r['status']:
                advice_parts.append('Iron supplements + Iron-rich foods')
            elif r['parameter'] == 'MCV' and 'HIGH' in r['status']:
                advice_parts.append('Vitamin B12 supplements + Folate-rich foods')
            elif r['parameter'] == 'HbA1c':
                advice_parts.append('Diabetes management + Low sugar diet + Exercise')
            elif r['parameter'] == 'eGFR':
                advice_parts.append('Nephrologist consultation + Hydration + Avoid NSAIDs')
        return ' | '.join(advice_parts) if advice_parts else 'Doctor consultation recommended'
    
    elif slight:
        advice_parts = []
        for r in slight:
            if r['parameter'] == 'Hemoglobin':
                advice_parts.append('Monitor hemoglobin + Iron-rich diet')
            elif r['parameter'] == 'CRP':
                advice_parts.append('Monitor inflammation + Rest + Hydration')
            elif r['parameter'] == 'ESR':
                advice_parts.append('Monitor for inflammation + Follow-up test')
            elif r['parameter'] == 'HbA1c':
                advice_parts.append('Reduce sugar intake + Exercise + Weight management')
            elif r['parameter'] == 'Urine Sugar':
                advice_parts.append('Monitor blood sugar + Reduce sugar intake')
            elif r['parameter'] == 'eGFR':
                advice_parts.append('Stay hydrated + Regular kidney function tests')
            elif r['parameter'] == 'MCV':
                advice_parts.append('Vitamin B12/Folate monitoring')
        return ' | '.join(advice_parts) if advice_parts else 'Monitor and maintain healthy lifestyle'
    
    else:
        return 'Continue healthy lifestyle + Regular check-ups + Balanced diet + Exercise'


# 7. NEW REPORT GENERATOR

def generate_formatted_report(results: list, patient_name: str = 'Patient', patient_age: int = None, gender: str = 'general') -> str:
    """
    Generates a report in the exact format specified by the user.
    """
    # Determine report source
    blood_params = ['Hemoglobin', 'WBC', 'RBC', 'Platelets', 'PCV', 'MCV', 'MCH']
    urine_params = ['Urine Sugar']
    other_params = ['CRP', 'ESR', 'HbA1c', 'IgE', 'eGFR', 'Blood Culture', 'Glucose', 'Creatinine']
    
    has_blood = any(r['parameter'] in blood_params for r in results)
    has_urine = any(r['parameter'] in urine_params for r in results)
    has_other = any(r['parameter'] in other_params for r in results)
    
    if has_blood and has_urine:
        source = 'Blood + Urine'
    elif has_blood:
        source = 'Blood'
    elif has_urine:
        source = 'Urine'
    else:
        source = 'Medical Report'
    
    # Filter abnormal parameters only
    abnormal = [r for r in results if r['severity'] != 'NORMAL']
    
    # Generate diagnosis and interpretation
    diagnosis = generate_diagnosis(results)
    interpretation = generate_interpretation(results, diagnosis)
    advice = generate_advice(results, diagnosis)
    
    # Build the report
    lines = []
    
    # Header
    age_str = f'Age {patient_age}' if patient_age else 'Age Unknown'
    lines.append(f"🩺 📊 REPORT — {patient_name} ({age_str})")
    lines.append("")
    lines.append(f"📄 Source: {source}")
    lines.append("")
    
    # Key Findings
    lines.append("🔍 Key Findings")
    if abnormal:
        for r in abnormal:
            lines.append(f"{r['parameter']}: {r['value']} {r['unit']} → {r['status']}")
    else:
        lines.append("All parameters are within normal range")
    lines.append("")
    
    # Diagnosis
    lines.append("🧠 Diagnosis")
    lines.append(diagnosis)
    lines.append("")
    
    # Interpretation
    lines.append("⚠️ Interpretation")
    lines.append(interpretation)
    lines.append("")
    
    # Advice
    lines.append("💡 Advice")
    lines.append(advice)
    
    return '\n'.join(lines)


# 8. NLP EXPLANATION GENERATOR (Legacy - kept for compatibility)

ADVICE_LIBRARY = {
    'Hemoglobin': {
        'LOW':  '🩸 Eat iron-rich foods: spinach, lentils, red meat, and fortified cereals. Consider vitamin C to improve iron absorption.',
        'HIGH': '💧 Drink more water and avoid smoking. High altitude areas can also cause higher hemoglobin.',
    },
    'Glucose': {
        'LOW':  '🍎 Eat a small snack with sugar (fruit juice, candy) if feeling shaky. Avoid skipping meals.',
        'HIGH': '🍚 Reduce sugar and refined carbs. Exercise regularly and monitor blood sugar levels.',
    },
    'WBC': {
        'LOW':  '🛡️ Boost immunity: eat well, sleep 7-8 hours, avoid crowded places during flu season.',
        'HIGH': '🌡️ Rest and stay hydrated. May need antibiotics if infection is present — consult your doctor.',
    },
    'RBC': {
        'LOW':  '🥩 Increase iron intake (red meat, beans, dark leafy greens). Get tested for anemia.',
        'HIGH': '💧 Stay hydrated. High RBC may need further evaluation by a doctor.',
    },
    'Platelets': {
        'LOW':  '⚠️ Avoid injury and contact sports. See a doctor if you notice unusual bruising or bleeding.',
        'HIGH': '🩺 Your doctor may need to monitor this. Stay hydrated and avoid smoking.',
    },
    'Creatinine': {
        'LOW':  '✅ Generally normal. Maintain good hydration.',
        'HIGH': '💊 Limit protein intake temporarily. Drink water. See a doctor for kidney function tests.',
    },
    'PCV': {
        'LOW':  '🥬 Eat iron-rich foods. Consider anemia testing.',
        'HIGH': '💧 Increase water intake. Avoid smoking and high altitudes without medical advice.',
    },
}

REPORT_TYPE_HINTS = {
    frozenset(['Hemoglobin', 'WBC', 'RBC', 'Platelets']): 'Complete Blood Count (CBC)',
    frozenset(['Glucose']): 'Blood Sugar / Diabetes Screening',
    frozenset(['Creatinine']): 'Kidney Function Test (KFT)',
    frozenset(['Hemoglobin', 'PCV']): 'Anemia Panel',
}


def _detect_report_type(results: list) -> str:
    """Detects the type of report based on available parameters."""
    param_set = set(r['parameter'] for r in results)
    
    for hint_set, name in REPORT_TYPE_HINTS.items():
        if hint_set.issubset(param_set):
            return name
    
    if len(param_set) >= 3:
        return 'Comprehensive Health Panel'
    elif len(param_set) >= 1:
        return 'Medical Lab Report'
    return 'Unknown Report Type'


def _status_word(status_str: str) -> str:
    """Extracts the status word (LOW/HIGH/NORMAL) from status string."""
    for key in ('LOW', 'HIGH', 'NORMAL', 'UNKNOWN'):
        if key in status_str.upper():
            return key
    return 'UNKNOWN'


def generate_health_summary(results: list, patient_name: str = 'Patient',
                             gemini_api_key: str = None) -> str:
    """
    Generates a clear, user-friendly health report explanation.
    
    Uses rule-based generation by default, or Gemini API if key is provided.
    """
    if gemini_api_key:
        return _gemini_summary(results, patient_name, gemini_api_key)
    return _rule_based_summary(results, patient_name)


def _rule_based_summary(results: list, patient_name: str) -> str:
    """Generates a rule-based health summary."""
    report_type = _detect_report_type(results)
    abnormal = [r for r in results if _status_word(r['status']) in ('LOW', 'HIGH')]
    
    lines = [
        '=' * 70,
        f'  🏥 HEALTH REPORT SUMMARY — {patient_name.upper()}',
        f'  Report Type: {report_type}',
        '=' * 70,
        '',
        f'Dear {patient_name},',
        '',
        f'Based on your {report_type}, here is a simple explanation of your results:',
        '',
        '-' * 70,
        '📊 YOUR RESULTS AT A GLANCE',
        '-' * 70,
    ]
    
    # Parameter details
    for r in results:
        status_symbol = {'LOW': '🔴', 'HIGH': '🟡', 'NORMAL': '🟢'}.get(_status_word(r['status']), '⚪')
        
        lines.extend([
            '',
            f'{status_symbol} {r["parameter"]}',
            f'   • Your Value    : {r["value"]} {r["unit"]}',
            f'   • Normal Range  : {r["low"]} – {r["high"]} {r["unit"]}',
            f'   • Status        : {r["status"]}',
            f'   • What it means : {r["message"]}',
        ])
    
    # Health advice section
    lines.extend(['', '-' * 70, '💡 HEALTH RECOMMENDATIONS', '-' * 70, ''])
    
    if abnormal:
        lines.append('Based on your abnormal results:')
        lines.append('')
        for r in abnormal:
            sw = _status_word(r['status'])
            advice = ADVICE_LIBRARY.get(r['parameter'], {}).get(sw)
            if advice:
                lines.append(f'   • {r["parameter"]} ({sw}): {advice}')
        
        lines.extend(['', 'General health tips for everyone:'])
    else:
        lines.append('✨ Great news! All your results are within normal limits.')
        lines.append('')
        lines.append('To maintain your good health:')
    
    lines.extend([
        '   • 💧 Drink 8-10 glasses of water daily',
        '   • 🥗 Eat a balanced diet with fruits and vegetables',
        '   • 🚶 Get 30 minutes of moderate exercise daily',
        '   • 😴 Sleep 7-8 hours per night',
        '   • 🚫 Avoid smoking and limit alcohol',
        '   • 🏥 Get regular health check-ups',
        '',
        '=' * 70,
        '⚠️  IMPORTANT MEDICAL DISCLAIMER',
        '=' * 70,
        '',
        'This analysis is generated by an AI system for informational purposes only.',
        'It does NOT replace professional medical advice, diagnosis, or treatment.',
        '',
        'Please consult a qualified healthcare provider to:',
        '   • Confirm these findings',
        '   • Get an accurate diagnosis',
        '   • Receive appropriate treatment',
        '',
        'Do NOT self-medicate or make major health decisions based solely on this report.',
        '',
        '=' * 70,
        '  💙 Stay healthy! — Your AI Health Assistant',
        '=' * 70,
    ])
    
    return '\n'.join(lines)


def _gemini_summary(results: list, patient_name: str, api_key: str) -> str:
    """Uses Google Gemini API to generate the explanation."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        params_text = '\n'.join([
            f"- {r['parameter']}: {r['value']} {r['unit']} "
            f"(Normal: {r['low']}-{r['high']}) - Status: {_status_word(r['status'])}"
            for r in results
        ])

        prompt = f"""You are a medical AI assistant. Analyze these lab results and provide a clear, simple explanation:

Patient: {patient_name}

Results:
{params_text}

Please provide:
1. A brief overview of the report
2. For each result, explain what it means in simple terms
3. If any values are abnormal, provide basic lifestyle advice
4. Always recommend consulting a doctor

Keep it friendly and easy to understand. Do NOT prescribe medications."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API failed: {e}")
        return _rule_based_summary(results, patient_name)


# 9. MAIN PIPELINE — run_analysis() (UPDATED WITH PATIENT INFO EXTRACTION)

def run_analysis(file_path: str, patient_name: str = 'Patient',
                 gender: str = 'general', plot: bool = False) -> dict:
    """
    Main function to analyze a medical report.
    
    Args:
        file_path: Path to PDF or image file
        patient_name: Name of the patient (optional, will try to extract from report)
        gender: 'male', 'female', or 'general'
        plot: Whether to generate a visualization
    
    Returns:
        Dictionary containing:
        - results: List of analysis results for each parameter
        - patient_info: Dictionary with extracted patient name and age
        - formatted_report: The formatted report string
    """
    print(f"\n{'='*60}")
    print(f"🔬 MEDICAL REPORT ANALYZER")
    print(f"   File: {os.path.basename(file_path)}")
    print(f"   Gender: {gender}")
    print(f"{'='*60}\n")

    # Step 1: Detect file type
    file_type = detect_file_type(file_path)
    print(f"📁 File type: {file_type.upper()}")

    # Step 2: Extract text with proper fallback for scanned PDFs
    if file_type == 'pdf':
        print("📖 Step 1: Trying direct PDF text extraction...")
        report_info = extract_text_from_pdf(file_path)
        
        # 🔥 CRITICAL: Check if PDF has extractable text
        if len(report_info['text'].strip()) < 100:
            print("⚠️ Direct extraction limited (<100 chars) - PDF appears to be SCANNED")
            print("🔍 Step 2: Switching to OCR-based extraction via pdf2image...")
            report_info = extract_text_from_scanned_pdf(file_path)
        else:
            print("✅ Direct text extraction successful!")
            
    elif file_type == 'image':
        print("🖼️ Processing image file with OCR...")
        report_info = extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use PDF, JPG, or PNG.")

    raw_text = report_info['text']
    
    # Debug output
    print(f"\n📄 EXTRACTION DETAILS:")
    print(f"   Method: {report_info.get('extraction_method', 'Unknown')}")
    print(f"   Pages: {report_info.get('pages', 1)}")
    print(f"   Text length: {len(raw_text)} characters")
    print(f"   Preview: {raw_text[:300]}...")
    print("-" * 60)

    # Step 3: Extract patient information
    patient_info = extract_patient_info(raw_text)
    # Use provided name if extraction failed or if explicitly provided
    if patient_name != 'Patient':
        patient_info['name'] = patient_name
    print(f"\n👤 PATIENT INFO:")
    print(f"   Name: {patient_info['name']}")
    print(f"   Age: {patient_info['age'] if patient_info['age'] else 'Not detected'}")
    print("-" * 60)

    # Step 4: Extract medical parameters
    params = extract_medical_parameters(raw_text)
    
    print(f"\n📊 EXTRACTED PARAMETERS:")
    if params:
        for param, value in params.items():
            print(f"   ✅ {param}: {value}")
    else:
        print("   ❌ No parameters extracted!")
        print("\n   Possible issues:")
        print("   1. OCR quality may be poor")
        print("   2. Report format may not be recognized")
        print("   3. Check if file contains actual medical data")
    print("-" * 60)

    # Step 5: Analyze parameters with severity indicators
    results = analyze_all_parameters(params, gender=gender)
    
    print(f"\n📈 ANALYSIS RESULTS:")
    for r in results:
        print(f"   {r['parameter']}: {r['value']} {r['unit']} → {r['status']}")
    print(f"{'='*60}\n")

    # Step 6: Generate formatted report
    formatted_report = generate_formatted_report(
        results, 
        patient_name=patient_info['name'], 
        patient_age=patient_info['age'], 
        gender=gender
    )

    # Step 7: Generate plot if requested
    if plot and results:
        _plot_results(results, patient_info['name'])

    return {
        'results': results,
        'patient_info': patient_info,
        'formatted_report': formatted_report
    }


def _plot_results(results: list, patient_name: str = 'Patient'):
    """Generates and saves a bar chart of results."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        plottable = [r for r in results if r['low'] is not None and r['low'] >= 0]
        if not plottable:
            print("⚠️ No plottable parameters found")
            return

        fig, axes = plt.subplots(1, len(plottable), figsize=(5 * len(plottable), 6))
        if len(plottable) == 1:
            axes = [axes]

        color_map = {'NORMAL': '#2ecc71', 'HIGH': '#e67e22', 'LOW': '#e74c3c'}

        for ax, r in zip(axes, plottable):
            sw = _status_word(r['status'])
            color = color_map.get(sw, '#3498db')
            
            # Create bar chart with range indicators
            ax.axhspan(r['low'], r['high'], alpha=0.2, color='#2ecc71', label='Normal Range')
            ax.bar(r['parameter'], r['value'], color=color, alpha=0.8, width=0.6)
            ax.axhline(r['low'], color='#27ae60', linestyle='--', linewidth=1.5, alpha=0.7)
            ax.axhline(r['high'], color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.7)
            
            ax.set_title(f"{r['parameter']}\n{r['status']}", fontsize=12, fontweight='bold')
            ax.set_ylabel(r['unit'], fontsize=10)
            ax.set_xticks([])
            
            # Add value label on bar
            ax.text(0, r['value'] * 1.02, f'{r["value"]:.1f}', 
                   ha='center', va='bottom', fontweight='bold', fontsize=11)

        plt.suptitle(f'Medical Report Analysis — {patient_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('medical_report_chart.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("📊 Chart saved as 'medical_report_chart.png'")
        
    except ImportError:
        print("⚠️ matplotlib not installed - skipping chart generation")
    except Exception as e:
        print(f"⚠️ Could not generate plot: {e}")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🏥 MEDICAL REPORT ANALYZER - READY")
    print("=" * 60)
    print("\n📌 Usage Examples:")
    print("   # Analyze a PDF report")
    print("   results = run_analysis('blood_report.pdf', patient_name='John Doe', gender='male')")
    print()
    print("   # Generate human-readable summary")
    print("   summary = generate_health_summary(results, patient_name='John Doe')")
    print("   print(summary)")
    print()
    print("=" * 60)