from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, json
from appwrite.input_file import InputFile
from appwrite_client import database, storage, DATABASE_ID, COLLECTION_ID, BUCKET_ID

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

QUESTION_COLUMN_MAP = {
    "1": "q1",
    "2": "q2",
    "3": "q3",
    "4": "q4",
    "5": "q5",
    "6": "q6",
    "7": "q7",
    "8": "q8",
    "9": "q9",
    "10": "q10",
    "11": "q11",
    "12": "q12",
    "13": "q13",
    "14": "q14",
    "15": "q15",
    "16": "q16",
    "17": "q17",
    "18": "q18",
    "19": "q19",
    "20": "q20",
    "21": "q21",
    "22": "q22",
    "23": "q23",
    "24": "q24",
    "25": "q25",
    "26": "q26",
    "27": "q27",
    "28": "q28",
    "29": "q29",
}

@app.route("/")
def home():
    return "Prakriti Data Collection API Running"

@app.route("/submit", methods=["POST"])
def submit():
    try:
        image = request.files["image"]
        answers = json.loads(request.form.get("answers"))
        name = request.form.get("name")
        age = int(request.form.get("age"))

        img_path = f"{UPLOAD_FOLDER}/{uuid.uuid4()}.png"
        image.save(img_path)

        img = storage.create_file(
            BUCKET_ID, "unique()", InputFile.from_path(img_path)
        )

        answer_cols = {
            QUESTION_COLUMN_MAP[k]: ", ".join(v)
            for k, v in answers.items()
            if k in QUESTION_COLUMN_MAP
        }

        doc = database.create_document(
            DATABASE_ID,
            COLLECTION_ID,
            "unique()",
            {
                "name": name,
                "age": age,
                **answer_cols,
                "image_id": img["$id"]
            }
        )

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
