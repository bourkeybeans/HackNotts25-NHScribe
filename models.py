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
    approved_at = Column(DateTime)
    comments = Column(Text)

    patient = relationship("Patient", back_populates="letters")
