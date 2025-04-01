from fastapi import FastAPI, File, UploadFile, Form, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from database import users_collection
from fastapi import HTTPException
from routes import admin


# Import authentication routes
from routes.auth import router as auth_router  

app = FastAPI()

# Secure session handling
app.add_middleware(SessionMiddleware, secret_key="your_secret_key", session_cookie="session_id", same_site="lax")
app.include_router(auth_router)  # No prefix
  # Authentication handled in `routes.auth`
app.include_router(admin.router)
# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific frontend URLs if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for CSS, JS, images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Ensure uploads folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- ROUTES --------------------

@app.get("/", name="index")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", name='login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# -------------------- USER DASHBOARD --------------------

@app.get("/dashboard")
async def dashboard(request: Request):
    user_name = request.session.get("user_name", "Guest")  
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "user_name": user_name})

@app.get("/profile")
async def profile(request: Request):
    print("Session Data:", request.session)  # Debugging: Check stored session data
    user_name = request.session.get("user_name", "Guest")
    user_email = request.session.get("user_email", "guest@example.com")
    return templates.TemplateResponse("profile.html", {"request": request, "user_name": user_name, "user_email": user_email})


@app.post("/profile/update")
async def update_profile(request: Request, name: str = Form(...), email: str = Form(...)):
    request.session["user_name"] = name
    request.session["user_email"] = email
    request.session["message"] = "Profile updated successfully!"
    return RedirectResponse(url="/profile", status_code=303)

# -------------------- SETTINGS --------------------

@app.get("/settings", name="settings")
async def settings(request: Request):
    message = request.session.pop("message", None)
    return templates.TemplateResponse("settings.html", {
        "request": request, 
        "message": message
    })

@app.post("/settings/change-password")
async def change_password(request: Request, new_password: str = Form(...)):
    request.session["user_password"] = new_password  # ❗ Store securely in DB, not session!
    request.session["message"] = "Password updated successfully!"
    return RedirectResponse(url="/settings", status_code=303)

# -------------------- LOGOUT --------------------

@app.get("/logout", name="logout")
async def logout(request: Request):
    request.session.clear()  # Clear user session
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout-page", response_class=HTMLResponse)
async def logout_page(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})

# -------------------- UPLOAD & ANALYSIS --------------------

@app.get("/upload", name="upload_image")
async def upload_image(request: Request):
    message = request.session.pop("upload_message", None)  
    return templates.TemplateResponse("upload_image.html", {"request": request, "message": message})

@app.get("/analysis", name="view_analysis")
async def view_analysis(request: Request):
    shot_result = request.session.get("shot_result", "No analysis available yet.")
    return templates.TemplateResponse("analysis.html", {"request": request, "shot_result": shot_result})

@app.post("/upload-image/", name="upload_image_api")
async def upload_image_api(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    request.session["shot_result"] = "No analysis yet"
    request.session["upload_message"] = "Image uploaded successfully!"
    return RedirectResponse(url="/upload", status_code=303)

# -------------------- NEWLY ADDED PAGES --------------------

@app.get("/terms-conditions", name="terms_conditions")
async def terms_conditions(request: Request):
    return templates.TemplateResponse("terms_conditions.html", {"request": request})

@app.get("/history", name="history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account-deletion", name="account_deletion")
async def account_deletion(request: Request):
    return templates.TemplateResponse("account_deletion.html", {"request": request})

@app.post("/delete-account")
async def delete_account(request: Request):
    user_email = request.session.get("user_email")

    if not user_email:
        raise HTTPException(status_code=400, detail="No user logged in.")

    # Delete user from database
    result = users_collection.delete_one({"email": user_email})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found in database.")

    # Clear session after deletion
    request.session.clear()

    return RedirectResponse(url="/", status_code=303)

@app.get("/admin/total_users")
def get_total_users():
    total_users = users_collection.count_documents({})
    return {"total_users": total_users}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
