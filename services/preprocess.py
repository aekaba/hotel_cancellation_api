import numpy as np
import pandas as pd
import joblib
from keras.models import load_model  
from typing import Dict
from pathlib import Path

# Dosya yolları
SCALER_PATH = Path("model/scaler.pkl")
WINSOR_PATH = Path("model/winsor_limits.pkl")  # winsorizer.pkl değil, winsor_limits.pkl kullanılmıştı
ENCODER_PATH = Path("model/encoder_model.keras")  # encoder.keras değil, encoder_model.keras
OHE_COLUMNS_PATH = Path("model/columns.pkl")

# Objeleri yükle
scaler = joblib.load(SCALER_PATH)
winsor_limits = joblib.load(WINSOR_PATH)
encoder = load_model(ENCODER_PATH)
expected_columns = joblib.load(OHE_COLUMNS_PATH)

def winsorize_dataframe(df: pd.DataFrame, limits: Dict[str, tuple]) -> pd.DataFrame:
    """Her sütun için belirlenen alt/üst limitlerle winsorize uygular."""
    df_winsor = df.copy()
    for col, (lower, upper) in limits.items():
        df_winsor[col] = np.clip(df_winsor[col], lower, upper)
    return df_winsor

def preprocess_input(data: Dict) -> np.ndarray:
    df = pd.DataFrame([data])

    # Kategorik sütunları one-hot encode et
    categoricals = ["type_of_meal_plan", "room_type_reserved", "market_segment_type"]
    df = pd.get_dummies(df, columns=categoricals)

    # Eksik sütunları 0 ile ekle
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_columns]  # Sıra garanti edilir

    # Winsorizer uygulama
    df_winsor = winsorize_dataframe(df, winsor_limits)

    # Normalize et
    df_scaled = scaler.transform(df_winsor)

    # Encode et
    df_encoded = encoder.predict(df_scaled)

    return df_encoded