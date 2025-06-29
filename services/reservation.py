from db.mongo import reservation_collection
from schemas.reservation_input import ReservationInput
from fastapi import HTTPException
import traceback
from services.predict import predict_cancellation
from bson import ObjectId
import logging
logger = logging.getLogger(__name__)

async def get_all_reservations():
    reservations = []
    async for reservation in reservation_collection.find():
        reservation["_id"] = str(reservation["_id"])  # ObjectId stringe çevriliyor
        reservations.append(reservation)
    return reservations

async def get_main_page():
    reservations = []
    async for reservation in reservation_collection.find():
        reservations.append(reservation)

    total = len(reservations)
    canceled = len([r for r in reservations if r.get("prediction_result") == 1])
    not_canceled = len([r for r in reservations if r.get("prediction_result") == 0])

    canceled_pct = round((canceled / total) * 100, 2) if total else 0
    not_canceled_pct = round((not_canceled / total) * 100, 2) if total else 0

    return {
        "total_reservations": total,
        "total_cancellations": canceled,
        "total_not_cancellations": not_canceled,
        "cancelled_percentage": canceled_pct,
        "not_cancelled_percentage": not_canceled_pct
    }


async def create_reservation(data: ReservationInput):
    try:
        data_dict = data.dict()

        # Boş alan kontrolü
        null_fields = [k for k, v in data_dict.items() if v is None]
        if null_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Boş geçilen alanlar: {', '.join(null_fields)}"
            )

        inserted = await reservation_collection.insert_one(data_dict)
        return {"inserted_id": str(inserted.inserted_id)}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Veritabanı hatası: {str(e)}")
    

async def predict_and_update_reservation(reservation_id: str):
    try:
        # Veriyi getir
        reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})

        if not reservation:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
        logger.info(f"Rezervasyon verisi: {reservation}")  # <
        # Predict işlemi
        result = predict_cancellation(reservation)
        logger.info(f"Tahmin sonucu: {result}") 

        # Güncelleme
        update_data = {
            "prediction_result": result["prediction"],
            "prediction_probability": result["probability"],
            "prediction_meaning": result["meaning"]
        }

        await reservation_collection.update_one(
            {"_id": ObjectId(reservation_id)},
            {"$set": update_data}
        )

        return {"reservation_id": reservation_id, **update_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin/Güncelleme hatası: {str(e)}")
    
async def delete_reservation(reservation_id: str):
    try:
        result = await reservation_collection.delete_one({"_id": ObjectId(reservation_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
        return {"status": "success", "message": "Rezervasyon silindi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Silme hatası: {str(e)}")