def predict_diseases(results):
    diseases = []

    params_low = {r['parameter'] for r in results if "LOW" in r['status']}
    params_high = {r['parameter'] for r in results if "HIGH" in r['status']}

    if {"Hemoglobin", "MCV", "MCH"}.intersection(params_low):
        diseases.append({
            "name": "Anemia",
            "confidence": "High",
            "reason": "Low Hemoglobin, MCV, MCH",
            "advice": "Increase iron-rich foods"
        })

    if {"WBC", "Neutrophils"}.intersection(params_high):
        diseases.append({
            "name": "Infection",
            "confidence": "Medium",
            "reason": "High WBC or Neutrophils",
            "advice": "Consult doctor"
        })

    if "Eosinophils" in params_high:
        diseases.append({
            "name": "Allergy",
            "confidence": "Medium",
            "reason": "High Eosinophils",
            "advice": "Avoid allergens"
        })

    return diseases