from adapter import legacy_to_modern_dict
from validation import validate_patient
from models import ModernPatient
from migration import save_rollback_snapshot

def run_canary_migration(db, legacy_patient):

    simulated_modern = legacy_to_modern_dict(
        legacy_patient
    )
    canary_patient = db.query(ModernPatient).filter(
        ModernPatient.patient_id == simulated_modern["patient_id"]
).first()

    if canary_patient is not None:

        save_rollback_snapshot(
            legacy_patient.PID,
            canary_patient
        )

        canary_patient.name = simulated_modern["name"]
        canary_patient.age = simulated_modern["age"]
        canary_patient.diagnosis = simulated_modern["diagnosis"]

    else:

        canary_patient = ModernPatient(
            patient_id=simulated_modern["patient_id"],
            name=simulated_modern["name"],
            age=simulated_modern["age"],
            diagnosis=simulated_modern["diagnosis"]
        )

        db.add(canary_patient)

    db.commit()
    db.refresh(canary_patient)

    modern_data = {
        "patient_id": canary_patient.patient_id,
        "name": canary_patient.name,
        "age": canary_patient.age,
        "diagnosis": canary_patient.diagnosis
    }

    legacy_data = {
        "PID": legacy_patient.PID,
        "PT_NM": legacy_patient.PT_NM,
        "AGE_YRS": legacy_patient.AGE_YRS,
        "DX": legacy_patient.DX
    }

    validation_result = validate_patient(
        legacy_data,
        modern_data
    )

    return {
        "mode": "CANARY",
        "patient_id": legacy_patient.PID,
        "modern_record": modern_data,
        "validation": validation_result
    }