from extraction.pdf_extractor import extract_pdf
from extraction.ocr_extractor import extract_image
from processing.parser import extract_parameters
from processing.analyzer import analyze
from ai.diagnosis import detect_diagnosis

def run_pipeline(file_path, gender="general"):

    # Step 1: Extract text
    if file_path.lower().endswith(".pdf"):
        text = extract_pdf(file_path)
    else:
        text = extract_image(file_path)

    # Step 2: Extract parameters
    params = extract_parameters(text)

    # Step 3: Analyze
    results = analyze(params, gender)

    # Step 4: Diagnosis
    diagnosis = detect_diagnosis(results)

    return {
        "params": params,
        "results": results,
        "diagnosis": diagnosis
    }