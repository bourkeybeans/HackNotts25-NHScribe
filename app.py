from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from typing import List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Patient, Results, Letter
import uuid, csv, io, os
import uvicorn

from letter_utils.generate_letter_content import generate_letter_content
from letter_utils.create_pdf import create_pdf

# --- Absolute database path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'scribe.db')}"

# --- Engine with debug logging ---
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # set True for debugging SQL statements
)

# --- Session factory ---
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Ensure all tables exist ---
Base.metadata.create_all(bind=engine)

# --- FastAPI  ---
app = FastAPI(title="Pi-Scribe API")

app.mount("/static", StaticFiles(directory="letters"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/patients/")
def create_patient(
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form("Other"),
    address: str = Form(""),
    conditions: str = Form(""),
    db: Session = Depends(get_db)
):
    patient = Patient(name=name, age=age, sex=sex, address=address, conditions=conditions)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/patients/")
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()


@app.get("/patients/search/")
def search_patients(
    name: str = None,
    age: int = None,
    sex: str = None,
    db: Session = Depends(get_db)
):
    """Search for patients by name, age, or sex"""
    query = db.query(Patient)
    
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    if age:
        query = query.filter(Patient.age == age)
    if sex:
        query = query.filter(Patient.sex == sex)
    
    return query.all()


@app.post("/upload-results/")
async def upload_results(
    patient_id: int = Form(...),  
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a CSV of test results for a specific patient."""

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    contents = await file.read()
    decoded = contents.decode("utf-8-sig").strip()
    if not decoded:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    reader = csv.DictReader(io.StringIO(decoded))
    batch_id = str(uuid.uuid4())
    inserted = 0

    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items() if k}

        test_name = row.get("test name") or row.get("test") or ""
        value = row.get("result") or row.get("value") or ""
        unit = row.get("units", "")
        flag = row.get("flag", "")
        ref = row.get("reference range", "")

        if not test_name or not value:
            continue

        ref_low, ref_high = None, None
        if "-" in ref:
            parts = [p.strip() for p in ref.split("-", 1)]
            if len(parts) == 2:
                ref_low, ref_high = parts

        result = Results(
            patient_id=patient_id,
            test_name=test_name,
            value=value,
            unit=unit,
            flag=flag,
            reference_low=ref_low,
            reference_high=ref_high,
            source_file=file.filename,
            batch_id=batch_id,
        )
        db.add(result)
        inserted += 1

    db.commit()

    results = db.query(Results).filter(
        Results.patient_id == patient_id,
        Results.batch_id == batch_id
    ).all()

    if not results:
        raise HTTPException(status_code=400, detail="No valid result rows found in CSV")

    return {
        "status": "success",
        "batch_id": batch_id,
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "sex": patient.sex,
            "address": patient.address,
            "conditions": patient.conditions,
        },
        "results": [
            {
                "test_name": r.test_name,
                "value": r.value,
                "unit": r.unit,
                "flag": r.flag,
                "reference_low": r.reference_low,
                "reference_high": r.reference_high,
                "source_file": r.source_file,
                "batch_id": r.batch_id,
            }
            for r in results
        ],
    
    }

@app.get("/letters/recent")
def get_recent_letters(db: Session = Depends(get_db)):
    letters = db.query(Letter).order_by(Letter.created_at.desc()).limit(10).all()
    return [
        {
            "id": l.letter_uid,
            "patientId": f"PT-{l.patient_id:04d}",
            "doctorName": l.doctor_name,
            "status": l.status,
            "details": l.details,
            "time": l.created_at.strftime("%H:%M"),
            "date": l.created_at.strftime("%Y-%m-%d"),
            "approvedAt": l.approved_at.strftime("%H:%M") if l.approved_at else None
        }
        for l in letters
    ]

from pydantic import BaseModel
from datetime import datetime

class StatusUpdate(BaseModel):
    new_status: str

@app.patch("/letters/{letter_uid}/status")
def update_letter_status(
    letter_uid: str,
    body: StatusUpdate,
    db: Session = Depends(get_db)
):
    letter = db.query(Letter).filter(Letter.letter_uid == letter_uid).first()
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")

    allowed = {"Draft", "Approved", "Rejected"}
    new_status = body.new_status
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status '{new_status}'")

    letter.status = new_status
    letter.approved_at = datetime.utcnow() if new_status == "Approved" else None

    db.add(letter)
    db.commit()
    db.refresh(letter)

    return {
        "id": letter.letter_uid,
        "status": letter.status,
        "approvedAt": (
            letter.approved_at.strftime("%Y-%m-%d %H:%M")
            if letter.approved_at else None
        ),
    }


@app.get("/letters/{letter_uid}")
def get_letter(letter_uid: str, db: Session = Depends(get_db)):
    """Get a specific letter by its UID"""
    letter = db.query(Letter).filter(Letter.letter_uid == letter_uid).first()
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    # Get patient information
    patient = db.query(Patient).filter(Patient.id == letter.patient_id).first()
    
    return {
        "letterUid": letter.letter_uid,
        "patientId": letter.patient_id,
        "patientName": patient.name if patient else "Unknown",
        "doctorName": letter.doctor_name or "Unknown",
        "details": letter.details or "",
        "status": letter.status,
        "content": letter.content or "",
        "createdAt": letter.created_at.strftime("%Y-%m-%d %H:%M") if letter.created_at else "",
        "approvedAt": letter.approved_at.strftime("%Y-%m-%d %H:%M") if letter.approved_at else None,
        "filePath": letter.file_path
    }


class ContentUpdate(BaseModel):
    content: str

@app.put("/letters/{letter_uid}/content")
def update_letter_content(
    letter_uid: str,
    body: ContentUpdate,
    db: Session = Depends(get_db)
):
    """Update the content of a letter"""
    letter = db.query(Letter).filter(Letter.letter_uid == letter_uid).first()
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    letter.content = body.content
    db.add(letter)
    db.commit()
    db.refresh(letter)
    
    # Get patient information
    patient = db.query(Patient).filter(Patient.id == letter.patient_id).first()
    
    return {
        "letterUid": letter.letter_uid,
        "patientId": letter.patient_id,
        "patientName": patient.name if patient else "Unknown",
        "doctorName": letter.doctor_name or "Unknown",
        "details": letter.details or "",
        "status": letter.status,
        "content": letter.content or "",
        "createdAt": letter.created_at.strftime("%Y-%m-%d %H:%M") if letter.created_at else "",
        "approvedAt": letter.approved_at.strftime("%Y-%m-%d %H:%M") if letter.approved_at else None,
    }


from fastapi.responses import FileResponse, StreamingResponse
from reportlab.lib.pagesizes import letter as letter_size
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import tempfile

@app.get("/letters/{letter_uid}/pdf")
def download_letter_pdf(letter_uid: str, db: Session = Depends(get_db)):
    """Generate and download a PDF of the letter"""
    letter_obj = db.query(Letter).filter(Letter.letter_uid == letter_uid).first()
    if not letter_obj:
        raise HTTPException(status_code=404, detail="Letter not found")
    
    # Get patient information
    patient = db.query(Patient).filter(Patient.id == letter_obj.patient_id).first()
    patient_name = patient.name if patient else "Unknown"
    
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Create PDF
        doc = SimpleDocTemplate(temp_path, pagesize=letter_size)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#003366',
            spaceAfter=12
        )
        
        address_style = ParagraphStyle(
            'Address',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#666666',
            spaceAfter=20
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=12
        )
        
        # Add letterhead
        story.append(Paragraph("NHS", header_style))
        story.append(Paragraph("123 Main Street<br/>Springfield, USA 12345", address_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add date
        date_str = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(date_str, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add recipient
        story.append(Paragraph(f"Dear {patient_name},", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add content
        content = letter_obj.content or "No content available"
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Replace single newlines with <br/> tags
                para_html = para.replace('\n', '<br/>')
                story.append(Paragraph(para_html, body_style))
        
        story.append(Spacer(1, 0.4*inch))
        
        # Add signature
        story.append(Paragraph("Sincerely,", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>{letter_obj.doctor_name or 'Unknown'}</b>", styles['Normal']))
        story.append(Paragraph("<i>NHS Medical Professional</i>", address_style))
        
        # Build PDF
        doc.build(story)
        
        # Return the PDF file
        return FileResponse(
            temp_path,
            media_type="application/pdf",
            filename=f"letter_{letter_uid}.pdf"
        )
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@app.post("/letters/generate")
def generate_letter(letter_data: Dict[str, Any] = Body(..., embed=True),
                    db: Session = Depends(get_db)):
    
    # Extract patient info
    patient_name = letter_data.get("patient", {}).get("name", "Unknown")
    patient_id = letter_data.get("patient", {}).get("id")
    doctor_name = letter_data.get("doctor", {}).get("name", "Dr. Smith")
    details = letter_data.get("details", "")
    
    # Validate patient exists
    if patient_id:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    
    # Generate letter content
    letter_content = generate_letter_content(letter_data, llama_model="llama3")
    
    # Create HTML file
    result = create_pdf(patient_name, letter_content, doctor_name)
    
    # Create letter record in database
    new_letter = Letter(
        patient_id=patient_id,
        doctor_name=doctor_name,
        details=details,
        status="Draft",
        letter_uid=result["letter_uid"],
        content=letter_content,
        file_path=result["file_path"]
    )
    
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    
    return {
        "status": "success",
        "letter_uid": new_letter.letter_uid,
        "file_path": new_letter.file_path,
        "pdf_url": new_letter.file_path,  # for backward compatibility with frontend
        "html_url": f"/static/{new_letter.file_path}",
        "letter_id": new_letter.id
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
