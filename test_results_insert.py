from sqlalchemy.orm import Session
from models import Results, Base
from app import engine


Base.metadata.create_all(bind=engine)

session = Session(bind=engine)

new_result = Results(
    patient_id=1,                # change to a valid patient_id in your DB
    test_name="Haemoglobin",
    value="120",
    unit="g/L",
    flag="Normal",
    reference_low="115",
    reference_high="165",
    source_file="test_upload.csv"
)

session.add(new_result)
session.commit()

results = session.query(Results).all()
for r in results:
    print(f"{r.id}: {r.test_name} = {r.value} {r.unit} ({r.flag})")

session.close()
