from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, uuid
from appwrite.input_file import InputFile

from model import predict_prakriti
from appwrite_client import database, storage, DATABASE_ID, COLLECTION_ID, BUCKET_ID

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return "Prakriti API Running with Appwrite"

# -----------------------------
# Upload + Predict
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    try:
        image = request.files["image"]
        answers = request.form.get("answers")
        name = request.form.get("name")
        age = int(request.form.get("age"))

        # Save locally
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath)

        # Upload image to Appwrite
        image_upload = storage.create_file(
            bucket_id=BUCKET_ID,
            file_id="unique()",
            file=InputFile.from_path(filepath)
        )
        image_id = image_upload["$id"]

        # Predict
        result = predict_prakriti(filepath, answers)

        # Create PDF
        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        generate_pdf(pdf_path, name, age, answers, result, filepath)

        # Upload PDF
        pdf_upload = storage.create_file(
            bucket_id=BUCKET_ID,
            file_id="unique()",
            file=InputFile.from_path(pdf_path)
        )
        pdf_id = pdf_upload["$id"]

        # Save record to Appwrite DB
        doc = database.create_document(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            document_id="unique()",
            data={
                "name": name,
                "age": age,
                "answers": answers,
                "prakriti": result["prakriti"],
                "confidence": result["confidence"],
                "image_id": image_id,
                "pdf_id": pdf_id
            }
        )

        return jsonify({
            "prakriti": result["prakriti"],
            "confidence": result["confidence"],
            "document_id": doc["$id"],
            "pdf_id": pdf_id
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Download PDF
# -----------------------------
@app.route("/download/<pdf_id>")
def download_pdf(pdf_id):
    try:
        file_bytes = storage.get_file_download(
            bucket_id=BUCKET_ID,
            file_id=pdf_id
        )

        temp_path = f"/tmp/{pdf_id}.pdf"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        return send_file(
            temp_path,
            as_attachment=True,
            download_name="prakriti_report.pdf"
        )

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Fetch Records (Doctor Dashboard)
# -----------------------------
@app.route("/records")
def records():
    try:
        docs = database.list_documents(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID
        )
        return jsonify(docs["documents"])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf(path, name, age, answers, result, image_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []

    elements.append(Paragraph("Prakriti Assessment Report", styles["Title"]))
    elements.append(Spacer(1,12))

    elements.append(Paragraph(f"Name: {name}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {age}", styles["Normal"]))
    elements.append(Paragraph(f"Prakriti: {result['prakriti']}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {result['confidence']}", styles["Normal"]))
    elements.append(Spacer(1,12))

    elements.append(Paragraph("Answers:", styles["Heading2"]))
    elements.append(Paragraph(answers, styles["Normal"]))
    elements.append(Spacer(1,12))

    try:
        elements.append(Image(image_path, width=200, height=150))
    except:
        pass

    doc.build(elements)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run()
