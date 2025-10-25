from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Patient, Results, Letter
import uuid, csv, io, os
import uvicorn

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



if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
