from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from model import predict_prakriti
from database import init_db, save_record, get_all_records
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


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

    record_id = save_record(record)
    return jsonify({
    "prakriti": result["prakriti"],
    "confidence": result["confidence"],
    "record_id": record_id
})

@app.route("/records")
def records():
    return jsonify(get_all_records())

@app.route("/download/<int:record_id>")
def download_report(record_id):
    import sqlite3

    conn = sqlite3.connect("prakriti.db")
    c = conn.cursor()
    c.execute("SELECT * FROM submissions WHERE id=?", (record_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Record not found", 404

    pdf_path = f"report_{record_id}.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    elements.append(Paragraph("<b>Prakriti Assessment Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Name: {row[1]}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {row[2]}", styles["Normal"]))
    elements.append(Paragraph(f"Predicted Prakriti: {row[5]}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {row[6]}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Answers:", styles["Heading2"]))
    elements.append(Paragraph(row[3], styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Add Image
    try:
        elements.append(Image(row[4], width=200, height=150))
    except:
        pass

    doc.build(elements)

    return jsonify({
        "download_url": f"/static/{pdf_path}"
    })


if __name__ == "__main__":
    app.run()
