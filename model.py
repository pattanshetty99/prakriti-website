import random

def predict_prakriti(image_path, answers):
    doshas = ["Vata", "Pitta", "Kapha"]
    return {
        "prakriti": random.choice(doshas),
        "confidence": round(random.uniform(0.7, 0.95), 2)
    }
