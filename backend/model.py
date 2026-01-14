import random

def predict_prakriti(image_path, answers):
    """
    image_path: uploaded image file path
    answers: JSON string
    """

    doshas = ["Vata", "Pitta", "Kapha"]

    return {
        "prakriti": random.choice(doshas),
        "confidence": round(random.uniform(0.70, 0.95), 2)
    }
