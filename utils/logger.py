from database import get_logs_collection
from datetime import datetime

async def log_action(email: str, action: str):
    logs_collection = get_logs_collection()
    await logs_collection.insert_one({
        "email": email,
        "action": action,
        "timestamp": datetime.utcnow()
    })
