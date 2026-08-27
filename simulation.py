from adapter import legacy_to_dict, modern_to_dict
from validation import validate_patient


def simulate_migration(legacy_patient, modern_patient):

    legacy_data = legacy_to_dict(legacy_patient)
    modern_data = modern_to_dict(modern_patient)

    validation_result = validate_patient(
        legacy_data,
        modern_data
    )

    return {
        "mode": "SIMULATION",
        "legacy": legacy_data,
        "current_modern": modern_data,
        "parity": validation_result
    }



print('Simulation module loaded successfully.')