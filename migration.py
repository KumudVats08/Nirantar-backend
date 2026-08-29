class MigrationState:
    ASSESS = "ASSESS"
    SIMULATE = "SIMULATE"
    SHADOW_VALIDATED = "SHADOW_VALIDATED"
    APPROVED = "APPROVED"
    CANARY = "CANARY"
    LIVE = "LIVE"
    ROLLED_BACK = "ROLLED_BACK"


migration_states = {}

rollback_snapshots = {}


def set_migration_state(patient_id, state):
    migration_states[patient_id] = state


def get_migration_state(patient_id):
    return migration_states.get(
        patient_id,
        MigrationState.ASSESS
    )


def approve_migration(shadow_result):

    if shadow_result["status"] != "PASS":
        return {
            "state": MigrationState.SHADOW_VALIDATED,
            "approved": False,
            "message": "Migration cannot be approved because shadow validation failed."
        }

    return {
        "state": MigrationState.APPROVED,
        "approved": True,
        "message": "Migration approved successfully."
    }


def go_live(patient_id):

    current_state = get_migration_state(patient_id)

    if current_state != MigrationState.CANARY:
        return {
            "state": current_state,
            "live": False,
            "message": "Patient must successfully complete canary migration before going live."
        }

    set_migration_state(
        patient_id,
        MigrationState.LIVE
    )

    return {
        "state": MigrationState.LIVE,
        "live": True,
        "message": "Patient migration is now LIVE."
    }



def save_rollback_snapshot(patient_id, modern_patient):
    rollback_snapshots[patient_id] = {
        "patient_id": modern_patient.patient_id,
        "name": modern_patient.name,
        "age": modern_patient.age,
        "diagnosis": modern_patient.diagnosis
    }


def get_rollback_snapshot(patient_id):
    return rollback_snapshots.get(patient_id)


def rollback_migration(patient_id, db):
    
    snapshot = get_rollback_snapshot(patient_id)

    if snapshot is None:
        return {
            "state": get_migration_state(patient_id),
            "rolled_back": False,
            "message": "No rollback snapshot exists for this patient."
        }

    from models import ModernPatient

    modern_patient = db.query(ModernPatient).filter(
        ModernPatient.patient_id == patient_id
    ).first()

    if modern_patient is None:
        return {
            "state": get_migration_state(patient_id),
            "rolled_back": False,
            "message": "Modern patient record not found."
        }

    modern_patient.name = snapshot["name"]
    modern_patient.age = snapshot["age"]
    modern_patient.diagnosis = snapshot["diagnosis"]

    db.commit()

    set_migration_state(
        patient_id,
        MigrationState.ROLLED_BACK
    )

    return {
        "state": MigrationState.ROLLED_BACK,
        "rolled_back": True,
        "restored_record": snapshot,
        "message": "Migration rolled back successfully."
    }