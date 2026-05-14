# 🩺 Health Advisor AI - Project Guide

This project is an AI-powered Medical Report Analyzer that provides health insights from uploaded PDF or image reports. It includes a web application, an API, and a research notebook.

## 📋 Required Libraries (Python)

To run this project, you need the following libraries installed:

- **streamlit**: For the web interface.
- **flask & flask-cors**: For the API backend.
- **pandas & openpyxl**: For data manipulation and Excel support.
- **pillow (PIL)**: For image processing.
- **pytesseract & easyocr**: For Optical Character Recognition (OCR).
- **pdf2image**: For converting PDF pages to images.
- **deep-translator**: For multi-language support (English/Gujarati).
- **pymupdf (fitz)**: For PDF text extraction.
- **matplotlib & seaborn**: For data visualization in the notebook.
- **certifi**: For SSL certificate management.

## 🛠️ System Dependencies

The project also requires these tools to be installed on your system:

1. **Tesseract OCR**: Required for reading text from images.
   - *Mac*: `brew install tesseract`
   - *Windows*: Download from UB Mannheim.
   - *Linux*: `sudo apt install tesseract-ocr`

2. **Poppler**: Required for converting PDF to images.
   - *Mac*: `brew install poppler`
   - *Windows*: Download poppler-windows and add to PATH.
   - *Linux*: `sudo apt install poppler-utils`

## 🚀 How to Run the Project

### 1. Install Libraries
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Web App
Start the main application by running:
```bash
streamlit run app.py
```

### 3. Run the Flask API
If you want to use the API backend:
```bash
python api.py
```

### 4. Run the Jupyter Notebook
For research and data analysis:
```bash
jupyter notebook healthadvisor.ipynb
```

## 📖 Usage Guide
- **Web App**: Upload a report (PDF/Image), select gender, and click "Analyze".
- **Chatbot**: Use the "Health Assistant" button for personalized advice.
- **API**: Send a POST request to `/analyze` with a file and gender.

---
*Disclaimer: This tool is for educational purposes only and should not replace professional medical advice.*
