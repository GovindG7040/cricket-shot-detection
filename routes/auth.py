from fastapi import APIRouter, Request, HTTPException, status, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from database import get_user_collection
from models.user import UserCreate, UserLogin, UserUpdate, UserPasswordUpdate
from utils.security import hash_password, verify_password
from config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from fastapi import Body

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")


# ✅ Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# ✅ Function to get current user from request (Token-Based Authentication)
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        print("⚠️ No access_token found in cookies.")
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("⚠️ JWT payload missing 'sub'.")
            return None

        users_collection = get_user_collection()
        user = await users_collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
            print(f"✅ Authenticated user: {user['email']}, Admin: {user.get('is_admin', False)}")
            return user
        print("⚠️ User not found in DB.")
        return None
    except JWTError as e:
        print(f"⚠️ JWT decode failed: {e}")
        return None


# ✅ API: Register User
@router.post("/register")
async def register_user(user: dict = Body(...)):  # Accept plain JSON
    users_collection = get_user_collection()

    existing_user = await users_collection.find_one({"email": user["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user["password"])
    new_user = {
        "name": user["name"],
        "email": user["email"],
        "hashed_password": hashed_password,
        "is_admin": False
    }

    await users_collection.insert_one(new_user)

    #return JSONResponse(content={"message": "User registered successfully"}, status_code=200)
    return RedirectResponse(url="/auth/login", status_code=303)



# ✅ API: Login User
@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    users_collection = get_user_collection()
    existing_user = await users_collection.find_one({"email": email})

    if not existing_user or not verify_password(password, existing_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)

    is_admin = existing_user.get("is_admin", False)
    redirect_url = "/admin/dashboard" if is_admin else "/dashboard"
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    print(f"🔐 Login successful. Redirecting to: {redirect_url}")
    return response


# ✅ Login Page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ✅ Register Page
@router.get("/register", name="register_page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ✅ Edit Profile (GET)
@router.get("/edit-profile", response_class=HTMLResponse)
async def edit_profile(request: Request):
    return templates.TemplateResponse("edit_profile.html", {"request": request})


# ✅ Edit Profile (POST)
@router.post("/edit-profile")
async def edit_profile_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    await update_user_profile(user["_id"], name, email)
    return RedirectResponse(url="/dashboard", status_code=303)


# ✅ Change Password (GET)
@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})


# ✅ Change Password (POST)
@router.post("/change-password")
async def change_password_post(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if new_password != confirm_password:
        return {"error": "New passwords do not match!"}

    await update_user_password(user["_id"], old_password, new_password)
    return RedirectResponse(url="/dashboard", status_code=303)


# ✅ Helper: Update User Profile
async def update_user_profile(user_id: str, name: str, email: str):
    users_collection = get_user_collection()
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"name": name, "email": email}}
    )


# ✅ Helper: Update User Password
async def update_user_password(user_id: str, old_password: str, new_password: str):
    users_collection = get_user_collection()

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or "hashed_password" not in user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(old_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    hashed_new_password = hash_password(new_password)
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hashed_new_password}}
    )


# ✅ Logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
