from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.requests import Request
from starlette.status import HTTP_302_FOUND
from database import admins_collection  # ✅ Correct import
  # ✅ Correct MongoDB collection name
from utils.security import hash_password, verify_password  # Security functions
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ✅ Admin Login Page (GET)
@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    error_message = request.query_params.get("error", "")
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": error_message})

# ✅ Admin Login (POST)
@router.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Find admin in the database
    admin = admins_collection.find_one({"username": username})  # ✅ Correct
  # ✅ Now using 'admins' collection

    print("Admin from DB:", admin)  # ✅ Debugging Step

    if not admin or not verify_password(password, admin["password"]):
        return RedirectResponse(url="/admin/login?error=invalid", status_code=HTTP_302_FOUND)

    # ✅ Clear user session before admin login
    request.session.clear()
    request.session["admin"] = admin["username"]

    return RedirectResponse(url="/admin/dashboard", status_code=HTTP_302_FOUND)

# ✅ Admin Logout (POST)
@router.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()  # ✅ Clear admin session
    return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

# ✅ Admin Dashboard (GET)
@router.get("/admin/dashboard", response_class=HTMLResponse)  # ✅ Fix: Ensure HTMLResponse
async def admin_dashboard(request: Request):
    if "admin" not in request.session:
        return RedirectResponse(url="/admin/login", status_code=HTTP_302_FOUND)

    return templates.TemplateResponse("admin_dashboard.html", {"request": request})
