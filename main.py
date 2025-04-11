from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes.auth import router as auth_router  # ✅ Import auth router
from routes.admin import router as admin_router  # ✅ Import admin router
from routes.predict import predict_image
import shutil
import os

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
  # ✅ Add prefix for admin routes

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
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    try:
        with open("latest_prediction.txt", "r") as f:
            result = f.read()
    except FileNotFoundError:
        result = "No analysis available. Please upload an image first."

    return templates.TemplateResponse("analysis.html", {"request": request, "result": result})

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

    # ✅ Call prediction logic with request
    prediction = await predict_image(file_location, request)
    print(f"🎯 Prediction: {prediction}")

    # ✅ Save prediction result for analysis page
    with open("latest_prediction.txt", "w") as f:
        f.write(prediction)

    # ✅ Redirect to analysis page
    return RedirectResponse(url="/analysis", status_code=303)