import joblib
import numpy as np
from keras.models import load_model
from services.preprocess import preprocess_input
from pathlib import Path

# MLP+Autoencoder model yolu
MLP_MODEL_PATH = Path("model/mlp_model.keras")  # .keras uzantısı doğruysa bunu düzelt

# Modeli yalnızca 1 kez yükle
model = load_model(MLP_MODEL_PATH)

def predict_cancellation(data: dict) -> dict:
    try:
        # Ön işleme
        processed = preprocess_input(data)

        # Tahmin
        prob = model.predict(processed, verbose=0)[0][0]
        prediction = int(prob >= 0.5)

        return {
            "probability": round(float(prob), 3),
            "prediction": prediction,
            "meaning": "İptal Edilecek" if prediction == 1 else "İptal Edilmeyecek"
        }

    except Exception as e:
        return {"error": f"Tahminleme sırasında hata oluştu: {str(e)}"}