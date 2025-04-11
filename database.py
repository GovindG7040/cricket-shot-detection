from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["cricket_shot_detection"]
users_collection = db["users"]

async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

async def update_user_profile(user_id: str, name: str, email: str):
    await users_collection.update_one({"_id": user_id}, {"$set": {"name": name, "email": email}})

async def update_user_password(user_id: str, old_password: str, new_password: str):
    await users_collection.update_one({"_id": user_id}, {"$set": {"hashed_password": new_password}})

# ✅ Ensure this function exists
def get_user_collection():
    return users_collection

def get_logs_collection():
    return db["logs"]  # or whatever your logs collection is named
