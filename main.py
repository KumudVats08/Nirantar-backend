from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import LegacyPatient, ModernPatient
from adapter import legacy_to_dict, modern_to_dict
from validation import validate_patient
from safety import safety_decision

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nirantar Health Data Migration API", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/patients/{patient_id}/validate")
def validate_patient_data(
    patient_id: str,
    db: Session = Depends(get_db)
    ):

    legacy_patient = db.query(LegacyPatient).filter(
        LegacyPatient.patient_id == patient_id
    ).first()

    modern_patient = db.query(ModernPatient).filter(
        ModernPatient.patient_id == patient_id
    ).first()

    if legacy_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found in HOSP-OLD"
        )

    if modern_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found in HOSP-NEW"
        )

    legacy_data = legacy_to_dict(legacy_patient)
    modern_data = modern_to_dict(modern_patient)

    validation_result = validate_patient(
        legacy_data,
        modern_data
    )

    safety_result = safety_decision(validation_result)


    return {
        "patient_id": patient_id,
        "legacy": legacy_data,
        "modern": modern_data,
        "validation": validation_result,
        "safety": safety_result
    }