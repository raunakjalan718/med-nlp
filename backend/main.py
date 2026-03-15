from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from src.ocr_bridge import extract_text_from_file
from src.nlp_engine import MedicalNLPEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Notice we completely removed the Gatekeeper/PyTorch!
nlp_engine = MedicalNLPEngine()
os.makedirs("temp_uploads", exist_ok=True)

# We combined upload and extraction into one single, fast endpoint
@app.post("/api/extract")
async def extract_data(file: UploadFile = File(...), document_type: str = Form(...)):
    file_loc = f"temp_uploads/{file.filename}"
    with open(file_loc, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    if document_type == "SCAN":
        os.remove(file_loc)
        return {"status": "success", "data": {"System_Action": "Medical Scan routed to Vision Database. No text extracted."}}

    # If it's a document, run the OCR and NLP
    raw_text = extract_text_from_file(file_loc)
    structured_data = nlp_engine.process_document(raw_text, document_type)
    
    os.remove(file_loc)
    return {"status": "success", "data": structured_data}