from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import os
import shutil
from datetime import datetime
import preprocess
import extract_text

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Text Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Tesseract config on startup (assuming default path ok)
@app.on_event("startup")
def startup_event():
    try:
        extract_text.configure_tesseract()
        print("✅ Tesseract configured successfully.")
    except Exception as e:
        print(f"❌ Tesseract init error: {e}")

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "API is running. Place index.html in static/ directory to view UI."}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")
    
    try:
        # 1. Read image into memory bytes
        image_bytes = await file.read()
        
        # 2. Process Image (Numpy Array output)
        processed_img_array = preprocess.preprocess_image(image_bytes)
        
        # 3. Extract text natively from array
        result = extract_text.extract_text_from_image(processed_img_array)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Save to Database
    new_doc = models.Document(
        filename=file.filename,
        raw_text=result.get("raw_text", ""),
        corrected_text=result.get("corrected_text", "")
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return {
        "id": new_doc.id,
        "filename": new_doc.filename,
        "raw_text": new_doc.raw_text,
        "corrected_text": new_doc.corrected_text,
        "created_at": new_doc.created_at
    }

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    docs = db.query(models.Document).order_by(models.Document.created_at.desc()).all()
    return docs
