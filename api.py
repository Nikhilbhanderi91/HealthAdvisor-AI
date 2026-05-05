from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from health_backend import run_analysis

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "HealthAdvisor API Running"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['file']
        gender = request.form.get('gender', 'general')

        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", file.filename)
        file.save(file_path)

        result = run_analysis(file_path, gender=gender)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)