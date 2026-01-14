from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from model import predict_prakriti

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Prakriti API Running"

@app.route("/predict", methods=["POST"])
def predict():
    image = request.files["image"]
    answers = request.form.get("answers")

    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    result = predict_prakriti(filepath, answers)

    return jsonify(result)

if __name__ == "__main__":
    app.run()
