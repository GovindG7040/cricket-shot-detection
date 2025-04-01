from pymongo import MongoClient

# ✅ Update this with your actual MongoDB connection string
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)

# ✅ Select the database
db = client["cricket_system"]

# ✅ Collections
users_collection = db["users"]
admins_collection = db["admins"]
