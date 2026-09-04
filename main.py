from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import LegacyPatient, ModernPatient
from adapter import legacy_to_dict, modern_to_dict
from validation import validate_patient
from safety import safety_decision
from simulation import simulate_migration
from shadow_validation import shadow_validate
from migration import (approve_migration, go_live,set_migration_state,
                       get_migration_state,MigrationState, go_live, rollback_migration)
from canary import run_canary_migration

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nirantar Health Data Migration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.on_event("startup")
def seed_if_empty():
    """
    Render's free tier disk is not persistent, so hospital.db is recreated
    empty on every redeploy/restart. This seeds it automatically the first
    time, and does nothing if data already exists (so it's safe locally too).
    """
    db = SessionLocal()
    try:
        if db.query(LegacyPatient).count() == 0:
            import seed  # running this module seeds the DB as a side effect
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


@app.get("/patients/{patient_id}/simulate")
def simulate_patient_migration(
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

    simulation_result = simulate_migration(
        legacy_patient,
        modern_patient
    )

    set_migration_state(
    patient_id,
    MigrationState.SIMULATE
        )

    return {
        "patient_id": patient_id,
        "simulation": simulation_result
    }


@app.get("/patients/{patient_id}/shadow-validate")
def shadow_validate_patient(

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

    result = shadow_validate(
        legacy_patient,
        modern_patient
    )

    if result["status"] == "PASS":
        set_migration_state(
            patient_id,
            MigrationState.SHADOW_VALIDATED
        )

    return {
        "patient_id": patient_id,
        "shadow_validation": result
    }


@app.get("/patients/{patient_id}/approve")
def approve_patient_migration(
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

    shadow_result = shadow_validate(
        legacy_patient,
        modern_patient
    )

    approval_result = approve_migration(
        shadow_result
    )

    if approval_result["approved"]:
        set_migration_state(
            patient_id,
            MigrationState.APPROVED
        )

    return {
        "patient_id": patient_id,
        "approval": approval_result
    }


@app.get("/patients/{patient_id}/canary")
def canary_patient_migration(
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

    shadow_result = shadow_validate(
        legacy_patient,
        modern_patient
    )

    approval_result = approve_migration(
        shadow_result
    )

    if not approval_result["approved"]:
        return {
            "patient_id": patient_id,
            "canary": {
                "status": "BLOCKED",
                "reason": approval_result["message"]
            }
        }

    current_state = get_migration_state(patient_id)

    if current_state != MigrationState.APPROVED:
        return {
            "patient_id": patient_id,
            "canary": {
                "status": "BLOCKED",
                "reason": "Patient must be approved before canary migration.",
                "current_state": current_state
            }
        }

    canary_result = run_canary_migration(
        db,
        legacy_patient
    )

    if canary_result["validation"]["status"] == "PASS":
        set_migration_state(
            patient_id,
            MigrationState.CANARY
        )

    return {
        "patient_id": patient_id,
        "canary": canary_result
    }


@app.get("/patients/{patient_id}/live")
def live_patient_migration(
    patient_id: str
):

    result = go_live(patient_id)

    return {
        "patient_id": patient_id,
        "live": result
    }


@app.get("/patients/{patient_id}/rollback")
def rollback_patient_migration(
    patient_id: str,
    db: Session = Depends(get_db)
):

    current_state = get_migration_state(patient_id)

    if current_state != MigrationState.LIVE:
        return {
            "patient_id": patient_id,
            "rollback": {
                "status": "BLOCKED",
                "reason": "Rollback is only available for a LIVE migration.",
                "current_state": current_state
            }
        }

    result = rollback_migration(
        patient_id,
        db
    )

    return {
        "patient_id": patient_id,
        "rollback": result
    }

@app.get("/patients/{patient_id}/status")
def patient_migration_status(
    patient_id: str,
    db: Session = Depends(get_db)
):

    legacy_patient = db.query(LegacyPatient).filter(
        LegacyPatient.patient_id == patient_id
    ).first()

    if legacy_patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found in HOSP-OLD"
        )

    current_state = get_migration_state(patient_id)

    return {
        "patient_id": patient_id,
        "migration_state": current_state,
        "pipeline": {
            "assess": True,
            "simulate": current_state in [
                MigrationState.SIMULATE,
                MigrationState.SHADOW_VALIDATED,
                MigrationState.APPROVED,
                MigrationState.CANARY,
                MigrationState.LIVE,
                MigrationState.ROLLED_BACK
            ],
            "shadow_validation": current_state in [
                MigrationState.SHADOW_VALIDATED,
                MigrationState.APPROVED,
                MigrationState.CANARY,
                MigrationState.LIVE,
                MigrationState.ROLLED_BACK
            ],
            "approval": current_state in [
                MigrationState.APPROVED,
                MigrationState.CANARY,
                MigrationState.LIVE,
                MigrationState.ROLLED_BACK
            ],
            "canary": current_state in [
                MigrationState.CANARY,
                MigrationState.LIVE,
                MigrationState.ROLLED_BACK
            ],
            "live": current_state == MigrationState.LIVE,
            "rolled_back": current_state == MigrationState.ROLLED_BACK
        }
    }
