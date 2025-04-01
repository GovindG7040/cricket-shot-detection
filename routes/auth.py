from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.status import HTTP_302_FOUND
from database import users_collection
from utils.security import hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ✅ User Registration
@router.post("/auth/register")
async def register_user(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    email = email.lower()

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(password)

    users_collection.insert_one({"name": name, "email": email, "password": hashed_password})

    return JSONResponse(status_code=201, content={"message": "User registered successfully!"})

# ✅ User Login
@router.post("/auth/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    email = email.lower()
    user = users_collection.find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        print("Login failed for:", email)  # Debugging: Check failed logins
        return RedirectResponse(url="/login?error=invalid", status_code=HTTP_302_FOUND)


    request.session["user_name"] = user["name"]
    request.session["user_email"] = user["email"]

    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)

# ✅ User Logout
@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
