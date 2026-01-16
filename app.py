from flask import Flask, request, jsonify
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

@app.route("/")
def home():
    return "Prakriti API Running with Appwrite"

# -----------------------------
# Upload + Predict
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

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
    pdf_path = f"{uuid.uuid4()}.pdf"
    generate_pdf(pdf_path, name, age, answers, result, filepath)

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

# -----------------------------
# Fetch Records (Doctor)
# -----------------------------
@app.route("/records")
def records():
    docs = database.list_documents(
        database_id=DATABASE_ID,
        collection_id=COLLECTION_ID
    )
    return jsonify(docs["documents"])

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

if __name__ == "__main__":
    app.run()
