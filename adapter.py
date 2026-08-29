from models import LegacyPatient, ModernPatient


def legacy_to_dict(patient: LegacyPatient):

    return {
        "PID": patient.PID,
        "PT_NM": patient.PT_NM,
        "AGE_YRS": patient.AGE_YRS,
        "DX": patient.DX
    }


def modern_to_dict(patient: ModernPatient):

    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "age": patient.age,
        "diagnosis": patient.diagnosis
    }


def legacy_to_modern_dict(patient: LegacyPatient):

    return {
        "patient_id": patient.PID,
        "name": patient.PT_NM,
        "age": patient.AGE_YRS,
        "diagnosis": patient.DX
    }


print("Adapter functions for legacy and modern systems created successfully.")