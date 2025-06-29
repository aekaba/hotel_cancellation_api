from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import HTTPException
from schemas.prediction_input import PredictionInput
from services.predict import predict_cancellation
from schemas.users import UserIn, UserLogin
from services.auth import register_user, login_user
from schemas.reservation_input import ReservationInput
from services.reservation import create_reservation
from services.reservation import predict_and_update_reservation
from services.reservation import get_all_reservations
from services.reservation import delete_reservation
from services.reservation import get_main_page

app = FastAPI(
    title="Rezervasyon İptal Tahmin API",
    description="MLP + Autoencoder modeliyle tahmin yapan servis.",
    version="1.0"
)

router = APIRouter()

@app.get("/")
def home():
    return {"message": "Hotel Cancellation Prediction API çalışıyor!"}

@app.post("/predict")
def predict(input_data: PredictionInput):
    data_dict = input_data.dict()
    result = predict_cancellation(data_dict)
    return result

@app.post("/register", status_code=201)
async def register(user: UserIn):
    return await register_user(user)

@app.post("/login", status_code=200)
async def login(login_data: UserLogin):
    return await login_user(login_data)

@app.post("/reservation")
async def add_reservation(reservation: ReservationInput):
    try:
        # 1. Kayıt işlemi
        result = await create_reservation(reservation)
        reservation_id = result.get("inserted_id")

        if not reservation_id:
            raise HTTPException(status_code=500, detail="Rezervasyon ID oluşturulamadı.")

        # 2. Tahmin ve güncelleme işlemi
        prediction = await predict_and_update_reservation(reservation_id)

        return {
            "status": "success",
            "reservation_id": reservation_id,
            "prediction": prediction["prediction_result"],                # 0 veya 1
            "meaning": prediction["prediction_meaning"],          # anlamlı yorum
            "probability": f"%{round(prediction['prediction_probability'] * 100, 1)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/reservations")
async def list_reservations():
    try:
        reservations = await get_all_reservations()
        return {"status": "success", "reservations": reservations}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
@app.get("/homedetail")
async def home_detail():
    return await get_main_page()

@app.delete("/reservations/{reservation_id}")
async def remove_reservation(reservation_id: str):
    return await delete_reservation(reservation_id)