import os, re, warnings
warnings.filterwarnings('ignore')

# 1. MODULES
def _opt(n):
    try: return __import__(n)
    except: return None
fitz, pytesseract, easyocr, Image, pdf2image = _opt('fitz'), _opt('pytesseract'), _opt('easyocr'), _opt('PIL.Image'), _opt('pdf2image')

# 2. AI KNOWLEDGE BASE
PARAM_KB = {
    'Hemoglobin': {
        'kw': ['haemoglobin', 'hemoglobin', 'hb', 'hgb'], 'valid': [3, 25], 'unit': 'g/dL', 
        'ref': {'male': (13.5, 17.5), 'female': (12.0, 16.0), 'gen': (12.5, 17.0)}, 
        't': {'v_low': 8.0, 'mod_low': 10.0, 's_low': 11.5}, 
        'advice': {
            '🚨 VERY LOW': 'EMERGENCY ❗ Critical Anemia. Consult doctor IMMEDIATELY.', 
            '🔴 MODERATE LOW': 'Significant Anemia. Consult Doctor for clinical investigation.',
            '🔴 LOW': 'Anemia detected. Consult Doctor + Iron-rich diet (Dates, Veggies).', 
            '🟡 Slight LOW': 'Routine Doctor Consultation + Iron/Ferritin profiling.'
        }
    },
    'WBC': {
        'kw': ['wbc', 'total count'], 'valid': [100, 100000], 'unit': '/μL', 
        'ref': {'gen': (4000, 10000)}, 't': {'v_low': 1500}, 
        'advice': {
            '🚨 VERY LOW': 'Immediate Hospitalization ❗ Severe infection risk (Leukopenia).', 
            '🔴 LOW': 'Weakened immunity. Rest and avoid crowds.'
        }
    },
    'ANC': {
        'kw': ['absolute neutrophils count', 'anc'], 'valid': [0, 10000], 'unit': '/c.mm',
        'ref': {'gen': (2000, 7000)}, 't': {'v_low': 500, 'mod_low': 1000},
        'advice': {
            '🚨 VERY LOW': 'CRITICAL ❗ Severe Neutropenia. Extremely high infection risk. Fatal if untreated.',
            '🔴 LOW': 'Neutropenia. High risk of infection. Consult hematologist.'
        }
    },
    'Platelets': {
        'kw': ['platelet', 'plt'], 'valid': [1000, 1e6], 'unit': '/μL', 
        'ref': {'gen': (150000, 450000)}, 't': {'v_low': 50000}, 
        'advice': {'🚨 CRITICAL LOW': 'EMERGENCY ❗ High bleeding risk. Avoid any trauma/NSAIDs.'}
    },
    'PCV': {'kw': ['pcv', 'hct'], 'valid': [10, 70], 'unit': '%', 'ref': {'male': (40, 52), 'female': (36, 48), 'gen': (38, 50)}},
    'MCV': {'kw': ['mcv'], 'valid': [40, 150], 'unit': 'fL', 'ref': {'gen': (78, 98)}, 't': {'v_low': 60}},
    'MCH': {'kw': ['mch'], 'valid': [10, 50], 'unit': 'pg', 'ref': {'gen': (27, 32)}},
    'Creatinine': {
        'kw': ['creatinine', 's.creatinine'], 'valid': [0.1, 15], 'unit': 'mg/dL', 'ref': {'gen': (0.6, 1.4)}, 't': {'mod_high': 1.5, 'v_high': 3.0},
        'advice': {'🔴 HIGH': 'Kidney Strain. Consult Nephrologist. Hydrate and avoid NSAIDs.'}
    },
    'eGFR': {
        'kw': ['egfr', 'gfr'], 'valid': [5, 200], 'unit': 'mL/min', 'ref': {'gen': (90, 130)}, 't': {'v_low': 15, 'mod_low': 60, 's_low': 89},
        'advice': {'🔴 Stage 3 CKD': 'Moderate Kidney Impairment. Nephrology consultation MANDATORY.'}
    },
    'CRP': {
        'kw': ['crp', 'reactive protein'], 'valid': [0, 1000], 'unit': 'mg/L', 'ref': {'gen': (0, 6)}, 't': {'s_high': 50, 'mod_high': 100, 'v_high': 300}, 
        'advice': {'🚨 VERY HIGH': 'Critical Sepsis/Inflammation ❗ Emergency medical review required.'}
    },
    'Glucose': {'kw': ['glucose', 'sugar', 'rbs'], 'valid': [30, 600], 'unit': 'mg/dL', 'ref': {'gen': (70, 140)}},
    'Sodium': {'kw': ['sodium'], 'valid': [100, 200], 'unit': 'mmol/L', 'ref': {'gen': (135, 148)}},
    'Potassium': {'kw': ['potassium'], 'valid': [1, 10], 'unit': 'mmol/L', 'ref': {'gen': (3.5, 5.3)}},
    'Chloride': {'kw': ['chloride'], 'valid': [50, 150], 'unit': 'mmol/L', 'ref': {'gen': (98, 107)}},
    'Bilirubin': {'kw': ['bilirubin'], 'valid': [0, 50], 'unit': 'mg/dL', 'ref': {'gen': (0.1, 1.2)}},
    'Cholesterol': {'kw': ['cholesterol'], 'valid': [50, 500], 'unit': 'mg/dL', 'ref': {'gen': (0, 200)}},
    'ESR': {'kw': ['esr'], 'valid': [0, 150], 'unit': 'mm/hr', 'ref': {'gen': (0, 20)}},
    'HbA1c': {'kw': ['hba1c'], 'valid': [3, 20], 'unit': '%', 'ref': {'gen': (0, 5.7)}, 't': {'pre': 6.4}},
    'Urine Sugar': {'kw': ['urine sugar', 'sugar: absent'], 'bool': True, 'ref': {'gen': (0, 0)}},
    'Blood Culture': {'kw': ['blood culture'], 'bool': True, 'ref': {'gen': (0, 0)}}
}

RULES = [
    {'m': {'WBC': 'LOW', 'Platelets': 'LOW', 'Hemoglobin': 'LOW'}, 'd': '🚨 Pancytopenia / Bone Marrow Crisis', 'msg': "Critical reduction in all blood lines. High risk of Sepsis/Bone Marrow failure."},
    {'m': {'ANC': 'CRITICAL'}, 'd': '🚨 Severe Neutropenia (ANC < 500)', 'msg': "Extremely high infection risk. Minor infections can be FATAL. Isolation required."},
    {'m': {'CRP': 'CRITICAL'}, 'd': '🚨 Severe Systemic Sepsis / Inflammation', 'msg': "Critical CRP ({CRP_v} mg/L) indicates severe systemic response or sepsis."},
    {'m': {'eGFR': ['HIGH', 'CRITICAL']}, 'd': '🔴 Chronic Kidney Disease (Stage 3+)', 'msg': "Moderate to Severe Kidney Impairment (eGFR {eGFR_v}). Nephrology consult required."},
    {'m': {'Hemoglobin': 'HIGH', 'MCV': 'LOW', 'MCH': 'LOW'}, 'd': '🔴 Microcytic Hypochromic Anemia', 'msg': "Small, pale RBCs + Low Hb ({Hemoglobin_v}) → Iron Deficiency pattern."},
    {'m': {'Platelets': 'CRITICAL'}, 'd': '🚨 Critical Thrombocytopenia', 'msg': "Critically low platelets ({Platelets_v}) → Active bleeding risk."},
    {'m': {'Hemoglobin': 'CRITICAL'}, 'd': '🚨 Severe Anemia', 'msg': "Life-threatening Hemoglobin level ({Hemoglobin_v} g/dL)."},
    {'m': {'WBC': 'CRITICAL'}, 'd': '🚨 Severe Leukopenia', 'msg': "Critically low WBC ({WBC_v}) → Extremely weak immunity."},
    {'m': {'HbA1c': 'HIGH'}, 'd': '🔴 Diabetes Mellitus', 'msg': "Chronic high blood sugar (HbA1c {HbA1c_v}%)."},
    {'m': {'CRP': ['SLIGHT', 'HIGH'], 'WBC': 'NORMAL'}, 'd': '🟡 Mild Inflammation', 'msg': "Slightly elevated CRP ({CRP_v})."},
    {'m': {'Hemoglobin': 'LOW'}, 'd': '🔴 Anemia', 'msg': "Low Hemoglobin ({Hemoglobin_v} g/dL)."}
]

# 3. UTILS & EXTRACTION
def extract_text(p):
    if p.lower().endswith('.pdf'):
        if not fitz: return ""
        text = "".join(page.get_text() for page in fitz.open(p))
        if len(text.strip()) < 100 and pdf2image:
            for i, img in enumerate(pdf2image.convert_from_path(p)):
                img.save("t.png"); text += extract_text("t.png"); os.remove("t.png")
        return text
    return pytesseract.image_to_string(Image.Image.open(p).convert('L'), config='--oem 3 --psm 6') if pytesseract else ""

def extract_info(text):
    info = {'name': 'Patient', 'age': None}
    for l in text.lower().split('\n'):
        m = re.search(r'\bage\b\s*[:\-/\\]?\s*(\d+)', l)
        if m: info['age'] = int(m.group(1))
        m = re.search(r'(\d+)\s*(years?|yrs?|y)\b', l)
        if m and (not info['age'] or info['age'] < 5 or 'sex' in l): info['age'] = int(m.group(1))
    return info

def extract_params(text):
    ext, text = {}, text.replace(",", "")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        l, nx = line.lower(), (lines[i+1] if i+1 < len(lines) else "")
        for p, c in PARAM_KB.items():
            if p in ext: continue
            for kw in c['kw']:
                if kw in l:
                    if c.get('bool'): ext[p] = 1 if any(k in l for k in ['present', 'positive', 'trace', 'growth']) else 0
                    else:
                        m = re.search(r"(\d+\.?\d*)", line[l.find(kw)+len(kw):]) or re.search(r"(\d+\.?\d*)", nx)
                        if m and c['valid'][0] <= float(m.group(1)) <= c['valid'][1]: ext[p] = float(m.group(1))
                    if p in ext: break
    return ext

# 4. ENGINE
def analyze_parameter(name, value, gender='gen'):
    c = PARAM_KB[name]
    lo, hi = c['ref'].get(gender, c['ref']['gen'])
    t, s, sev = c.get('t', {}), '🟢 NORMAL', 'NORMAL'
    if c.get('bool'):
        if value > 0: s, sev = ('🔴 Infection' if name == 'Blood Culture' else '🟡 ABNORMAL'), ('HIGH' if name == 'Blood Culture' else 'SLIGHT')
    elif value < t.get('v_low', -1): s, sev = ('🚨 VERY LOW' if name not in ['Platelets', 'ANC'] else f'🚨 CRITICAL LOW ({name})'), 'CRITICAL'
    elif value < t.get('mod_low', -1): s, sev = '🔴 MODERATE LOW', 'HIGH'
    elif value < lo: s, sev = ('🟡 Slight LOW' if value >= t.get('s_low', -1) else '🔴 LOW'), ('SLIGHT' if value >= t.get('s_low', -1) else 'HIGH')
    elif value > t.get('v_high', 1e9): s, sev = '🚨 VERY HIGH', 'CRITICAL'
    elif value > t.get('mod_high', 1e9): s, sev = ('🔴 Stage 3 CKD' if name == 'eGFR' else '🔴 HIGH'), 'HIGH'
    elif value > hi:
        if value <= t.get('s_high', 1e9): s, sev = '🟡 Slight HIGH', 'SLIGHT'
        elif name == 'HbA1c' and value <= t.get('pre', 6.4): s, sev = '🟡 PREDIABETES', 'SLIGHT'
        else: s, sev = '🔴 HIGH' if name != 'HbA1c' else '🔴 DIABETES', 'HIGH'
    return {'parameter': name, 'status': s, 'severity': sev, 'value': value, 'unit': c.get('unit', ''), 'low': lo, 'high': hi}

def generate_diagnosis(results):
    p_map, parts = {r['parameter']: r for r in results}, []
    for r in RULES:
        match = all(any(x in p_map.get(k, {}).get('status', '') for x in ([v] if isinstance(v, str) else v)) for k, v in r['m'].items())
        if match:
            d = r['d']
            if not any(word in " ".join(parts) for word in d.split() if len(word) > 4): parts.append(d)
    return " + ".join(parts) or ("🟢 Normal Health" if not any(r['severity'] != 'NORMAL' for r in results) else "🟡 Abnormal Findings")

def generate_interpretation(results, diagnosis):
    p_map = {r['parameter']: r for r in results}
    for r in RULES:
        if r['d'] in diagnosis: return r['msg'].format(**{f"{k}_v": p_map.get(k, {}).get('value', 'N/A') for k in PARAM_KB})
    return "Abnormal results detected. Clinical correlation required."

def generate_advice(results, diagnosis):
    advices = set()
    is_crit = any(r['severity'] == 'CRITICAL' for r in results)
    for r in results:
        if r['severity'] == 'NORMAL': continue
        kb_adv = PARAM_KB[r['parameter']].get('advice', {})
        msg = kb_adv.get(r['status']) or kb_adv.get(r['severity'])
        if msg and (not is_crit or "diet" not in msg.lower()): advices.add(msg)
    return " | ".join(filter(None, advices)) or "Consult Doctor."

def generate_formatted_report(results, name='Patient', age=None, gender='gen'):
    diag = generate_diagnosis(results)
    report = f"🩺 📊 REPORT — {name} (Age {age or '??'})\n\n🔍 Key Findings\n"
    report += "\n".join(f"{r['parameter']}: {r['value']} {r['unit']} → {r['status']}" for r in results if r['severity'] != 'NORMAL')
    report += f"\n\n🧠 Diagnosis\n{diag}\n\n⚠️ Interpretation\n{generate_interpretation(results, diag)}\n\n💡 Advice\n{generate_advice(results, diag)}"
    return report

def run_analysis(path, name='Patient', gender='gen', plot=False):
    text = extract_text(path)
    p_info, params = extract_info(text), extract_params(text)
    if name != 'Patient': p_info['name'] = name
    results = [analyze_parameter(p, v, gender) for p, v in params.items()]
    return {'results': results, 'patient_info': p_info, 'formatted_report': generate_formatted_report(results, p_info['name'], p_info['age'], gender)}

analyze_parameter_with_severity = analyze_parameter
def analyze_all_parameters(params, gender='gen'): return [analyze_parameter(p, v, gender) for p, v in params.items()]
extract_text_from_pdf = extract_text_from_image = extract_text_from_scanned_pdf = extract_text
extract_patient_info = extract_info
extract_medical_parameters = extract_params
PARAM_CONFIG = PARAM_KB

if __name__ == "__main__":
    print("🏥 AI ANALYZER READY")