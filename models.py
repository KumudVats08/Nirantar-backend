from sqlalchemy import Column, Integer, String
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)


class LegacyPatient(Base):
    __tablename__ = "legacy_patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)

    PID = Column(String)
    PT_NM = Column(String)
    AGE_YRS = Column(Integer)
    DX = Column(String)


class ModernPatient(Base):
    __tablename__ = "modern_patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)

    name = Column(String)
    age = Column(Integer)
    diagnosis = Column(String)

print("Patient models for legacy and modern formats created successfully.")