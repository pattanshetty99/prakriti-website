from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from model import predict_prakriti
from database import init_db, save_record, get_all_records

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

@app.route("/")
def home():
    return "Prakriti API Running"

@app.route("/predict", methods=["POST"])
def predict():
    image = request.files["image"]
    answers = request.form.get("answers")
    name = request.form.get("name")
    age = request.form.get("age")

    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    result = predict_prakriti(filepath, answers)

    record = {
        "name": name,
        "age": age,
        "answers": answers,
        "image_path": filepath,
        "prakriti": result["prakriti"],
        "confidence": result["confidence"]
    }

    save_record(record)
    return jsonify(result)

@app.route("/records")
def records():
    return jsonify(get_all_records())

if __name__ == "__main__":
    app.run()
