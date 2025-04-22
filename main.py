from fastapi import FastAPI, File, UploadFile, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes.auth import router as auth_router  # ✅ Import auth router
from routes.admin import router as admin_router  # ✅ Import admin router
from routes.predict import predict_image
import shutil
import os
import json
from database import get_feedback_collection
from routes.auth import get_current_user  # ✅ This should decode the JWT
from datetime import datetime
from routes.feedback import router as feedback_router
from bson.objectid import ObjectId
app = FastAPI()

# ✅ Mount static files for CSS, JS, images
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# ✅ Ensure upload directory exists
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])  
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(feedback_router, tags=["feedback"])

# ✅ Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Contact Page
@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# ✅ About Page
@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# ✅ Dashboard Page
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email")

    feedbacks_collection = get_feedback_collection()
    feedback_cursor = feedbacks_collection.find({"user": user_email})
    feedbacks = await feedback_cursor.to_list(length=100)  # or any upper limit


    print("Feedback for user dashboard:", feedbacks)  # for debugging

    return templates.TemplateResponse("dashboard.html", {
    "request": request,
    "feedbacks": feedbacks
})


# ✅ Analysis Page
@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    try:
        with open("latest_prediction.json", "r") as f:
            result = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        result = {
            "predicted_shot": "❌ No analysis available.",
            "description": []
        }

    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "predicted_shot": result["predicted_shot"],
        "description": result["description"]
    })

# ✅ Contact Form Submission
@app.post("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    form_data = await request.form()
    return templates.TemplateResponse("contact.html", {"request": request, "message": "Form submitted successfully!"})

# ✅ File Upload Page
@app.get("/upload/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# ✅ File Upload API
@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"📸 File uploaded successfully! filename: {file.filename}")

    prediction = await predict_image(file_location, request)
    print(f"🎯 Prediction: {prediction}")

    # Save full prediction as JSON
    with open("latest_prediction.json", "w") as f:
        json.dump(prediction, f)

    return RedirectResponse(url="/analysis", status_code=303)

# ✅ Feedback Page
@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request})

# ✅ Feedback Submission — FIXED ✅
@app.post("/submit-feedback")
async def submit_feedback(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    form = await request.form()
    message = form.get("message")

    user_email = current_user.get("email") if current_user else "Anonymous"
    if current_user is None:
        raise HTTPException(status_code=401, detail="Login required to submit feedback")


    collection = get_feedback_collection()
    await collection.insert_one({
        "user": user_email,
        "message": message,
        "timestamp": datetime.utcnow()
    })

    return RedirectResponse(url="/dashboard", status_code=303)

