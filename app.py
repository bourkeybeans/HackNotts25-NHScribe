from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Patient, Results
import uuid, csv
from datetime import datetime

# --- Database setup ---
DATABASE_URL = "sqlite:///./scribe.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Pi-Scribe API")

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Routes ---

@app.post("/patients/")
def create_patient(
    name: str,
    age: int,
    sex: str = "Other",
    address: str = "",
    conditions: str = "",
    db: Session = Depends(get_db)
):
    """Create a new patient record."""
    patient = Patient(
        name=name,
        age=age,
        sex=sex,
        address=address,
        conditions=conditions
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/patients/")
def list_patients(db: Session = Depends(get_db)):
    """Return all patients."""
    patients = db.query(Patient).all()
    return patients


@app.post("/upload-results/")
async def upload_results(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a CSV of test results for a specific patient."""
    # 1. Ensure the patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Read file contents
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    batch_id = str(uuid.uuid4())
    lines = contents.decode("utf-8").splitlines()
    reader = csv.DictReader(lines)

    # 3. Parse each row safely
    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items() if k}

        test_name = row.get("test name")
        value = row.get("result")
        unit = row.get("units")
        flag = row.get("flag")
        ref = row.get("reference range", "")

        # split 115-165 into low/high if available
        ref_low, ref_high = None, None
        if "-" in ref:
            parts = [p.strip() for p in ref.split("-", 1)]
            if len(parts) == 2:
                ref_low, ref_high = parts

        if not test_name or not value:
            continue  # skip incomplete rows

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

    db.commit()

    # 4. Fetch results for response
    results = db.query(Results).filter(
        Results.patient_id == patient_id,
        Results.batch_id == batch_id
    ).all()

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
