import os, re, warnings
warnings.filterwarnings('ignore')

PARAMETERS = {
    "Hemoglobin": {
        "min": 12.0, "max": 17.5, "unit": "g/dL",
        "low_reasons": ["Iron Deficiency", "Blood Loss", "Kidney Disease"],
        "high_reasons": ["Dehydration", "Smoking"]
    },
    "RBC": {
        "min": 4.2, "max": 5.5, "unit": "M/μL",
        "low_reasons": ["Anemia", "Blood Loss", "Nutritional Deficiency"],
        "high_reasons": ["Dehydration", "Bone Marrow Disorder"]
    },
    "PCV": {
        "min": 38, "max": 52, "unit": "%",
        "low_reasons": ["Anemia", "Blood Loss"],
        "high_reasons": ["Dehydration"]
    },
    "MCV": {
        "min": 78, "max": 98, "unit": "fL",
        "low_reasons": ["Iron Deficiency Anemia"],
        "high_reasons": ["Vitamin B12 Deficiency"]
    },
    "MCH": {
        "min": 27, "max": 32, "unit": "pg",
        "low_reasons": ["Iron Deficiency"],
        "high_reasons": ["Macrocytic Anemia"]
    },
    "MCHC": {
        "min": 32, "max": 36, "unit": "g/dL",
        "low_reasons": ["Iron Deficiency"],
        "high_reasons": ["Hereditary Spherocytosis"]
    },
    "RDW": {
        "min": 11, "max": 15, "unit": "%",
        "low_reasons": [],
        "high_reasons": ["Anemia", "Vitamin Deficiency"]
    },
    "Platelets": {
        "min": 150000, "max": 400000, "unit": "/μL",
        "low_reasons": ["Dengue", "Viral Infection", "Bone Marrow Issue"],
        "high_reasons": ["Inflammation", "Infection"]
    },
    "Bilirubin Direct": {
        "min": 0.0, "max": 0.4, "unit": "mg/dL",
        "low_reasons": [],
        "high_reasons": ["Liver Disease", "Bile Duct Obstruction"]
    },
    "Protein": {
        "min": 6.3, "max": 8.3, "unit": "g/dL",
        "low_reasons": ["Malnutrition", "Liver Disease"],
        "high_reasons": ["Dehydration"]
    },
    "Albumin": {
        "min": 3.5, "max": 5.0, "unit": "g/dL",
        "low_reasons": ["Liver Disease", "Kidney Disease", "Malnutrition"],
        "high_reasons": ["Dehydration"]
    }
}

def _opt(n):
    try: return __import__(n)
    except: return None

fitz = _opt('fitz')
pytesseract = _opt('pytesseract')
Image = _opt('PIL.Image')
pdf2image = _opt('pdf2image')

PARAM_KB = {

    # 🧬 CBC
    'Hemoglobin': {'kw': ['haemoglobin','hemoglobin','hb'], 'valid':[3,25],'unit':'g/dL','ref':{'gen':(12.5,17.5)},'cat':'Hematology'},
    'RBC': {'kw':['rbc'],'valid':[1,10],'unit':'M/μL','ref':{'gen':(4.2,5.5)},'cat':'Hematology'},
    'WBC': {'kw':['wbc','total count'],'valid':[100,100000],'unit':'/μL','ref':{'gen':(4000,10000)},'cat':'Hematology'},
    'Platelets': {'kw':['platelet'],'valid':[1000,1e6],'unit':'/μL','ref':{'gen':(150000,450000)},'cat':'Hematology'},

    'PCV': {'kw':['pcv','hct'],'valid':[10,70],'unit':'%','ref':{'gen':(38,52)},'cat':'Hematology'},
    'MCV': {'kw':['mcv'],'valid':[40,150],'unit':'fL','ref':{'gen':(78,98)},'cat':'Hematology'},
    'MCH': {'kw':['mch'],'valid':[10,50],'unit':'pg','ref':{'gen':(27,32)},'cat':'Hematology'},
    'MCHC': {'kw':['mchc'],'valid':[20,50],'unit':'g/dL','ref':{'gen':(32,36)},'cat':'Hematology'},
    'RDW': {'kw':['rdw'],'valid':[5,40],'unit':'%','ref':{'gen':(11,15)},'cat':'Hematology'},

    # 🧪 Differential
    'Neutrophils': {'kw':['polymorphs','neutrophils'],'valid':[0,100],'unit':'%','ref':{'gen':(55,70)},'cat':'Hematology'},
    'Lymphocytes': {'kw':['lymphocytes'],'valid':[0,100],'unit':'%','ref':{'gen':(20,40)},'cat':'Hematology'},
    'Eosinophils': {'kw':['eosinophils'],'valid':[0,100],'unit':'%','ref':{'gen':(0,4)},'cat':'Hematology'},
    'Monocytes': {'kw':['monocytes'],'valid':[0,100],'unit':'%','ref':{'gen':(0,6)},'cat':'Hematology'},
    'Basophils': {'kw':['basophils'],'valid':[0,100],'unit':'%','ref':{'gen':(0,1)},'cat':'Hematology'},

    # 🧪 LFT
    'Bilirubin Total': {'kw':['bilirubin total'],'valid':[0,10],'unit':'mg/dL','ref':{'gen':(0.3,1.2)},'cat':'Liver'},
    'Bilirubin Direct': {'kw':['direct'],'valid':[0,5],'unit':'mg/dL','ref':{'gen':(0,0.4)},'cat':'Liver'},
    'SGPT': {'kw':['sgpt','alt'],'valid':[0,500],'unit':'U/L','ref':{'gen':(0,49)},'cat':'Liver'},
    'SGOT': {'kw':['sgot','ast'],'valid':[0,500],'unit':'U/L','ref':{'gen':(15,45)},'cat':'Liver'},
    'Protein': {'kw':['total protein'],'valid':[0,20],'unit':'g/dL','ref':{'gen':(6.3,8.3)},'cat':'Liver'},
    'Albumin': {'kw':['albumin'],'valid':[0,10],'unit':'g/dL','ref':{'gen':(3.6,4.5)},'cat':'Liver'},

    # 🧠 Biochemistry
    'Glucose': {'kw':['glucose','sugar'],'valid':[30,600],'unit':'mg/dL','ref':{'gen':(70,140)},'cat':'Metabolic'}
}

def extract_text(path):
    if path.lower().endswith(".pdf") and fitz:
        text = ""
        for page in fitz.open(path):
            text += page.get_text()
        return text

    if pytesseract and Image:
        return pytesseract.image_to_string(Image.open(path))

    return ""

def extract_info(text):

    import re

    # 🔧 Clean text (important for PDF parsing)
    text = text.replace("\n", " ").replace("  ", " ")

    info = {
        'name': 'Patient',
        'age': None,
        'date': None,
        'dr': None
    }

    name_match = re.search(r'name\s*[:\-]?\s*([A-Za-z ]{3,40})', text, re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()

        # remove unwanted trailing words
        name = re.sub(r'\b(age|sex|male|female)\b.*', '', name, flags=re.IGNORECASE)

        if len(name) > 3:
            info['name'] = name.upper()


    # handles: Age / Sex : 55 / Male
    age_match = re.search(r'age[^0-9]{0,10}(\d{1,3})', text.lower())
    if age_match:
        age = int(age_match.group(1))
        if 5 < age < 100:
            info['age'] = age

    # fallback (rare case)
    if info['age'] is None:
        age_match = re.search(r'\b(\d{2})\s*(years|yrs|y)\b', text.lower())
        if age_match:
            info['age'] = int(age_match.group(1))

    date_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    if date_match:
        info['date'] = date_match.group(0)

    dr_match = re.search(r'(?:dr\.?|ref\.?\s*by)\s*[:\-]?\s*([A-Za-z ]+)', text, re.IGNORECASE)
    if dr_match:
        doctor = dr_match.group(1).strip()
        if len(doctor) > 2:
            info['dr'] = doctor.upper()

    if info['name'] == 'Patient':
        fallback = re.search(r'\b[A-Z]{3,}(?: [A-Z]{3,})+\b', text)
        if fallback:
            info['name'] = fallback.group(0)

    return info

def extract_params(text):
    extracted = {}
    lines = text.lower().replace(",", "").split("\n")

    for i, line in enumerate(lines):
        for param, config in PARAM_KB.items():

            if param in extracted:
                continue

            for kw in config['kw']:
                if kw in line:

                    m = re.search(r"(\d+\.?\d*)", line)
                    if not m and i+1 < len(lines):
                        m = re.search(r"(\d+\.?\d*)", lines[i+1])

                    if m:
                        val = float(m.group(1))
                        if config['valid'][0] <= val <= config['valid'][1]:
                            extracted[param] = val
                            break

    return extracted

def analyze_parameter(name, value):
    ref = PARAMETERS.get(name)

    if ref:
        lo = ref["min"]
        hi = ref["max"]
        unit = ref["unit"]

        if value < lo:
            status = "LOW"
            reasons = ref["low_reasons"]
        elif value > hi:
            status = "HIGH"
            reasons = ref["high_reasons"]
        else:
            status = "NORMAL"
            reasons = []

        return {
            "parameter": name,
            "value": value,
            "unit": unit,
            "low": lo,
            "high": hi,
            "status": status,
            "reasons": reasons
        }

    c = PARAM_KB.get(name)
    if c:
        lo_hi = c['ref'].get('gen') if 'gen' in c['ref'] else next(iter(c['ref'].values()))
        lo, hi = lo_hi
        unit = c.get('unit', '')

        if value < lo:
            status = "LOW"
        elif value > hi:
            status = "HIGH"
        else:
            status = "NORMAL"

        return {
            "parameter": name,
            "value": value,
            "unit": unit,
            "low": lo,
            "high": hi,
            "status": status,
            "reasons": []
        }

    return {
        "parameter": name,
        "value": value,
        "unit": "",
        "low": None,
        "high": None,
        "status": "UNKNOWN",
        "reasons": []
    }


def generate_interpretation(results):
    summary = []

    for r in results:
        if r["status"] != "NORMAL":
            line = f"• {r['parameter']} is {r['status']} ({r['value']} {r['unit']}). "
            reasons_text = ', '.join(r['reasons'][:3]) if r['reasons'] else 'No specific cause'
            line += f"Possible reasons: {reasons_text}."
            summary.append(line)

    if not summary:
        return "✅ All parameters are within normal range."

    return "🧠 Key Findings:\n\n" + "\n".join(summary)


def generate_smart_summary(results):

    summary = "🧠 📊 MAIN FINDINGS FROM YOUR REPORT\n\n"

    abnormal = [r for r in results if r['status'] != 'NORMAL']

    if not abnormal:
        return "✅ All parameters are normal."

    summary += "🔴 Abnormal Values:\n"
    for r in abnormal:
        summary += f"{r['parameter']}: {r['value']} {r['unit']} ({r['status']})\n"

    return summary

def run_analysis(path, name='Patient', gender='gen'):

    text = extract_text(path)

    info = extract_info(text) 
    params = extract_params(text)

    if name != 'Patient':
        info['name'] = name

    results = [analyze_parameter(p, v) for p, v in params.items()]

    summary = generate_smart_summary(results)
    interpretation = generate_interpretation(results)

    return {
        "results": results,
        "summary": summary,
        "interpretation": interpretation,
        "patient_info": info   
    }

if __name__ == "__main__":
    print("✅ Updated AI Ready")