from simulation import simulate_migration
from safety import safety_decision


def shadow_validate(legacy_patient, modern_patient):

    simulation_result = simulate_migration(
        legacy_patient,
        modern_patient
    )

    parity_result = simulation_result["parity"]

    safety_result = safety_decision(parity_result)

    if safety_result["migration_allowed"]:
        shadow_status = "PASS"
    else:
        shadow_status = "BLOCKED"

    return {
        "mode": "SHADOW_VALIDATION",
        "status": shadow_status,
        "simulation": simulation_result,
        "safety": safety_result
    }