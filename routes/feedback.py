from fastapi import APIRouter, Depends
from database import get_feedback_collection
from routes.auth import get_current_user

router = APIRouter()

@router.get("/api/feedback/response")
async def get_feedback_response(current_user: dict = Depends(get_current_user)):
    feedback_collection = get_feedback_collection()
    feedback = await feedback_collection.find_one(
        {"user": current_user["email"], "response": {"$ne": None}},  # ✅ FIXED FIELD NAME
        sort=[("_id", -1)]
    )
    if feedback:
        return {"response": feedback["response"]}
    return {"response": None}
