from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(Text)
    age = Column(Integer)
    sex = Column(String, CheckConstraint("sex IN ('M','F','Other')"))
    conditions = Column(Text)

    letters = relationship("Letter", back_populates="patient", cascade="all, delete")

class Letter(Base):
    __tablename__ = "letters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_name = Column(String)
    letter_date = Column(DateTime, default=datetime.utcnow)
    approval_status = Column(String, CheckConstraint(
        "approval_status IN ('draft','pending','approved','rejected')"
    ), default="draft")
    raw_text = Column(Text)
    results_csv = Column(Text)
    approved_at = Column(DateTime)
    comments = Column(Text)

    patient = relationship("Patient", back_populates="letters")

class Results(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    unit = Column(String)
    flag = Column(String)  # 'normal', 'low', 'high', 'abnormal'
    reference_low = Column(String)  # optional for LLM summaries
    reference_high = Column(String)
    collected_at = Column(DateTime, default=datetime.utcnow)
    source_file = Column(String)
    
