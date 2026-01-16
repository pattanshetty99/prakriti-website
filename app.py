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
# QUESTION MAP
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
        database.create_document(
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
# PDF Generator (PROFESSIONAL DESIGN)
# -----------------------------
def generate_pdf(path, name, age, answers, result, image_path):

    styles = getSampleStyleSheet()

    # ----------- STYLES -----------
    title_style = ParagraphStyle(
        "title",
        fontSize=26,
        alignment=1,
        textColor=colors.white,
        spaceAfter=10
    )

    patient_style = ParagraphStyle(
        "patient",
        fontSize=12,
        textColor=colors.HexColor("#0f172a"),
        leading=16
    )

    section_style = ParagraphStyle(
        "section",
        fontSize=14,
        textColor=colors.white,
        backColor=colors.HexColor("#2563eb"),
        leftIndent=8,
        spaceBefore=16,
        spaceAfter=8
    )

    question_style = ParagraphStyle(
        "question",
        fontSize=11,
        leading=14
    )

    result_style = ParagraphStyle(
        "result",
        fontSize=16,
        alignment=1,
        textColor=colors.white
    )

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    # ---------------- HEADER BANNER ----------------
    header = Table(
        [[Paragraph("PRAKRITI ASSESSMENT REPORT", title_style)]],
        colWidths=[7.3*inch]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1e3a8a")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 18))

    # ---------------- PHOTO + PATIENT INFO ----------------
    try:
        face_img = Image(image_path, width=2.5*inch, height=2.2*inch)
    except:
        face_img = Paragraph("Image not available", patient_style)

    patient_info = [
        Paragraph(f"<b>Patient Name:</b> {name}", patient_style),
        Paragraph(f"<b>Age:</b> {age}", patient_style),
    ]

    info_table = Table(
        [[face_img, patient_info]],
        colWidths=[3*inch, 4.2*inch]
    )

    info_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # ---------------- RESPONSES SECTION ----------------
    elements.append(Paragraph("Selected Responses", section_style))
    elements.append(Spacer(1, 10))

    parsed_answers = json.loads(answers)

    for qid, selected_opts in parsed_answers.items():
        question_text = QUESTION_MAP.get(qid, f"Question {qid}")

        block = []
        block.append(Paragraph(f"<b>Q{qid}. {question_text}</b>", question_style))
        block.append(Spacer(1, 4))

        for opt in selected_opts:
            block.append(Paragraph(f"✔ {opt}", question_style))

        card = Table([[block]], colWidths=[7.1*inch])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#eef2ff")),
            ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#6366f1")),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ]))

        elements.append(card)
        elements.append(Spacer(1, 12))

    elements.append(Spacer(1, 24))

    # ---------------- FINAL RESULT BANNER ----------------
    result_text = Paragraph(
        f"<b>Prakriti:</b> {result['prakriti']} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; "
        f"<b>Confidence:</b> {result['confidence']}",
        result_style
    )

    result_table = Table([[result_text]], colWidths=[7.2*inch])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#047857")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("BOX", (0,0), (-1,-1), 1.5, colors.black),
    ]))

    elements.append(result_table)

    doc.build(elements)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run()
