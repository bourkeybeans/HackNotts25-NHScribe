from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(Text)
    age = Column(Integer)
    sex = Column(String, CheckConstraint("sex IN ('M','F','Other')"))
    conditions = Column(Text)

    # optional relationships
    results = relationship("Results", back_populates="patient")

class Results(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    test_name = Column(String)
    value = Column(String)
    unit = Column(String)
    flag = Column(String)
    reference_low = Column(String)
    reference_high = Column(String)
    source_file = Column(String)
    batch_id = Column(String)

    patient = relationship("Patient", back_populates="results")
