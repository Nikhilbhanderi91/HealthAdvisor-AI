# 🩺 HealthAdvisor AI

An AI-powered medical report analysis system that extracts parameters from reports and provides intelligent health insights, summaries, and comparisons.

---

## 🎯 Project Objective

HealthAdvisor AI is designed to help users—especially in rural areas—understand their medical reports easily.

It analyzes reports and provides:
- 📊 Parameter extraction  
- 🧠 AI-based summary  
- ⚠️ Disease detection  
- 💡 Health advice  
- 📈 Report comparison (progress tracking)  

---

## 🚀 Features

### 📤 Upload Reports
- Upload PDF or Image medical reports  
- Supports basic lab reports (CBC, glucose, etc.)

### 🔍 Parameter Extraction
Extracts key medical parameters:
- Hemoglobin  
- RBC, WBC  
- Platelets  
- PCV, MCV, MCH  
- Glucose  

### 🧠 AI Analysis
- Detects NORMAL / LOW / HIGH values  
- Rule-based expert system  

### 📄 Smart Summary
- Highlights abnormal values  
- Gives simple explanation  

### 👤 Patient Info Extraction
- Name  
- Age  
- Date  

### 🤖 Chatbot (English + Gujarati)
- Ask questions about your report  
- Get explanations and advice  


---

## 🧠 AI Concepts Used

- Rule-Based Expert System  
- NLP (Regex-based extraction)  
- Knowledge-Based System  
- Decision Support System  

---

## 🏗️ Tech Stack

### Backend
- Python  
- PyMuPDF (fitz)  
- Regex (NLP)  
- pytesseract (optional OCR)  

### Frontend
- Streamlit  

### Extra
- Deep Translator (Gujarati support)  


---

## ⚙️ Installation & Run

```bash
# Clone repository
git clone https://github.com/your-username/HealthAdvisor-AI.git

# Go to project folder
cd HealthAdvisor-AI

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
