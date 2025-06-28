from fastapi import HTTPException
from db.mongo import users_collection
from schemas.users import UserIn, UserLogin
from bson import ObjectId

async def register_user(user: UserIn):
    existing = await users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=409, detail="Kullanıcı adı zaten var.")

    user_dict = user.dict()
    result = await users_collection.insert_one(user_dict)
    return {
        "message": f"{user.name} başarıyla kayıt oldu.",
        "user_id": str(result.inserted_id)
    }

async def login_user(login_data: UserLogin):
    user = await users_collection.find_one({
        "username": login_data.username,
        "password": login_data.password
    })

    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı.")
    
    return {
        "message": f"Hoşgeldiniz, {user['name']}"
    }