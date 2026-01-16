from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, uuid, json
from appwrite.input_file import InputFile

from model import predict_prakriti
from appwrite_client import database, storage, DATABASE_ID, COLLECTION_ID, BUCKET_ID

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# QUESTION MAP (Expand later)
# -----------------------------
QUESTION_MAP = {
    "1": "How would you describe your body frame?",
    "2": "How does your body weight change over time?",
    "3": "How is your appetite usually?",
    "4": "How is your digestion after meals?",
    "5": "How do you generally feel after eating?",
    "6": "Bowel movements?"
}

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

        # Save image locally
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

        # Generate PDF
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

        # Save record in DB
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
# Doctor Records
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
# PDF Generator (Styled Layout)
# -----------------------------
def generate_pdf(path, name, age, answers, result, image_path):

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        fontSize=20,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        "section",
        fontSize=14,
        textColor=colors.HexColor("#115e59"),
        spaceBefore=12,
        spaceAfter=6
    )

    normal_style = styles["Normal"]

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []

    # -------- TITLE --------
    elements.append(Paragraph("Prakriti Assessment Report", title_style))
    elements.append(Spacer(1, 12))

    # -------- IMAGE + PATIENT INFO --------
    try:
        face_img = Image(image_path, width=2.5*inch, height=2*inch)
    except:
        face_img = Paragraph("Image not available", normal_style)

    patient_table = Table(
        [
            ["Name", name],
            ["Age", str(age)],
            ["Prakriti", result["prakriti"]],
            ["Confidence", str(result["confidence"])]
        ],
        colWidths=[90, 200]
    )

    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.6, colors.grey),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))

    header_table = Table(
        [[face_img, patient_table]],
        colWidths=[3*inch, 3.5*inch]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOX", (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 18))

    # -------- ANSWERS --------
    elements.append(Paragraph("Selected Responses", section_style))
    elements.append(Spacer(1, 6))

    try:
        parsed_answers = json.loads(answers)

        for qid, selected_opts in parsed_answers.items():
            question_text = QUESTION_MAP.get(qid, f"Question {qid}")
            elements.append(Paragraph(f"<b>Q{qid}. {question_text}</b>", normal_style))
            elements.append(Spacer(1, 4))

            for opt in selected_opts:
                elements.append(Paragraph(f"✔ {opt}", normal_style))

            elements.append(Spacer(1, 10))

    except:
        elements.append(Paragraph("Unable to parse answers.", normal_style))

    doc.build(elements)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run()
