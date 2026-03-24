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
    str(i): f"q{i}" for i in range(1, 30)
}

@app.route("/")
def home():
    return "Prakriti Data Collection API Running"


@app.route("/submit", methods=["POST"])
def submit():
    try:
        print("🔥 Request received")

        # -------------------------
        # VALIDATION
        # -------------------------
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = request.files["image"]

        answers_raw = request.form.get("answers")
        if not answers_raw:
            return jsonify({"error": "Answers missing"}), 400

        answers = json.loads(answers_raw)

        name = request.form.get("name") or "Unknown"
        age_raw = request.form.get("age")
        age = int(age_raw) if age_raw and age_raw.isdigit() else 0

        print("Name:", name)
        print("Age:", age)

        # -------------------------
        # SAVE IMAGE LOCALLY
        # -------------------------
        img_path = f"{UPLOAD_FOLDER}/{uuid.uuid4()}.png"
        image.save(img_path)
        print("Image saved locally")

        # -------------------------
        # UPLOAD IMAGE (SAFE)
        # -------------------------
        image_id = "upload_failed"

        try:
            print("Uploading image...")
            img = storage.create_file(
                BUCKET_ID,
                "unique()",
                InputFile.from_path(img_path)
            )
            image_id = img["$id"]
            print("Image uploaded:", image_id)

        except Exception as upload_error:
            print("⚠️ Image upload failed:", str(upload_error))

        # -------------------------
        # PREPARE ANSWERS (ALWAYS COMPLETE)
        # -------------------------
        answer_cols = {
            QUESTION_COLUMN_MAP[k]: ", ".join(answers.get(k, []))
            for k in QUESTION_COLUMN_MAP
        }

        print("Prepared all answer columns")

        # -------------------------
        # CREATE DOCUMENT
        # -------------------------
        doc = database.create_document(
            DATABASE_ID,
            COLLECTION_ID,
            "unique()",
            {
                "name": name,
                "age": age,
                **answer_cols,
                "image_id": image_id
            }
        )

        print("Document created successfully")

        # -------------------------
        # CLEANUP TEMP FILE
        # -------------------------
        if os.path.exists(img_path):
            os.remove(img_path)

        return jsonify({
            "status": "success",
            "message": "Data stored successfully"
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
