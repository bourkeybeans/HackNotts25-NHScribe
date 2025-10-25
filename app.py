from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Patient, Results   # 👈 import Results here
import csv

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
    name: str,
    age: int,
    sex: str = "Other",
    address: str = "",
    conditions: str = "",
    db: Session = Depends(get_db)
):
    patient = Patient(name=name, age=age, sex=sex, address=address, conditions=conditions)
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
            source_file=file.filename
        )
        db.add(result)

    db.commit()
    return {"message": f"Uploaded results from {file.filename}"}
