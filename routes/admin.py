from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_user_collection, get_logs_collection, get_prediction_logs_collection
from routes.auth import get_current_user
from bson.objectid import ObjectId
from utils.logger import log_action

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ✅ Middleware to ensure admin access
async def admin_required(request: Request):
    user = await get_current_user(request)
    if not user or not user.get("is_admin", False):
        return RedirectResponse(url="/dashboard", status_code=303)
    return user

# ✅ Admin Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

# ✅ View All Users
@router.get("/users", response_class=HTMLResponse)
async def view_users(request: Request, user=Depends(admin_required)):
    users_collection = get_user_collection()
    users = await users_collection.find().to_list(100)
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users})

# ✅ Delete User (Admin-only)
@router.post("/users/delete/{user_id}")
async def delete_user(request: Request, user_id: str, admin=Depends(admin_required)):
    users_collection = get_user_collection()
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Log the deletion action
    await log_action(admin["email"], f"Deleted user {user_id}")

    return RedirectResponse(url="/admin/users", status_code=303)




# ✅ View Logs
@router.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request, user=Depends(admin_required)):
    logs_collection = get_logs_collection()
    prediction_logs_collection = get_prediction_logs_collection()

    logs = await logs_collection.find().sort("timestamp", -1).to_list(100)
    prediction_logs = await prediction_logs_collection.find().sort("timestamp", -1).to_list(100)

    return templates.TemplateResponse("admin_logs.html", {
        "request": request,
        "logs": logs,
        "prediction_logs": prediction_logs
    })


# ✅ Admin Logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)  # ← fixed route
    response.delete_cookie("access_token")
    return response

