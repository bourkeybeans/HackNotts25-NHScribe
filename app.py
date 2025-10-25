from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Patient, Results   # 👈 import Results here

import uuid, csv
from fastapi import UploadFile, File, Depends
from models import Results, Patient, Letter
from datetime import datetime

DATABASE_URL = "sqlite:///./scribe.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pi-Scribe API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/patients/")
def create_patient(
    forename: str,
    surname: str,
    age: int,
    sex: str = "Other",
    address: str = "",
    conditions: str = "",
    db: Session = Depends(get_db)
):
    patient = Patient(forename=forename, surname=surname, age=age, sex=sex, address=address, conditions=conditions)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/patients/")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return patients

@app.post("/upload-results/")
async def upload_results(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    batch_id = str(uuid.uuid4())

    contents = await file.read()
    lines = contents.decode("utf-8").splitlines()
    reader = csv.DictReader(lines)

    for row in reader:
        result = Results(
            patient_id=patient_id,
            test_name=row["Test Name"],
            value=row["Result"],
            unit=row["Units"],
            flag=row["Flag"],
            reference_low=row["Reference Range"].split("-")[0] if "-" in row["Reference Range"] else None,
            reference_high=row["Reference Range"].split("-")[-1] if "-" in row["Reference Range"] else None,
            source_file=file.filename,
            batch_id=batch_id,
        )
        db.add(result)

    db.commit()

    results = db.query(Results).filter(
        Results.patient_id == patient_id,
        Results.batch_id == batch_id
    ).all()

    patient_data = {
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "sex": patient.sex,
        "address": patient.address,
        "conditions": patient.conditions,
    }

    results_data = [
        {
            "test_name": r.test_name,
            "value": r.value,
            "unit": r.unit,
            "flag": r.flag,
            "reference_low": r.reference_low,
            "reference_high": r.reference_high,
            "batch_id": r.batch_id,
            "source_file": r.source_file,
        }
        for r in results
    ]

    return {
        "batch_id": batch_id,
        "patient": patient_data,
        "results": results_data,
    }
