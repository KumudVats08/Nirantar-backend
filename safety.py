def safety_decision(validation_result):

    if validation_result["status"] == "PASS":
        return {
            "decision": "APPROVE",
            "migration_allowed": True
        }

    return {
        "decision": "PAUSE",
        "migration_allowed": False
    }

print('Safety module loaded successfully.')