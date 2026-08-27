def normalize(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().lower()

    return str(value).strip().lower()


def validate_patient(legacy, modern):

    differences = []

    if normalize(legacy["PID"]) != normalize(modern["patient_id"]):
        differences.append({
            "field": "patient_id",
            "legacy": legacy["PID"],
            "modern": modern["patient_id"]
        })

    if normalize(legacy["PT_NM"]) != normalize(modern["name"]):
        differences.append({
            "field": "name",
            "legacy": legacy["PT_NM"],
            "modern": modern["name"]
        })

    if normalize(legacy["AGE_YRS"]) != normalize(modern["age"]):
        differences.append({
            "field": "age",
            "legacy": legacy["AGE_YRS"],
            "modern": modern["age"]
        })

    if normalize(legacy["DX"]) != normalize(modern["diagnosis"]):
        differences.append({
            "field": "diagnosis",
            "legacy": legacy["DX"],
            "modern": modern["diagnosis"]
        })

    if differences:
        return {
            "parity": "MISMATCH",
            "status": "CRITICAL",
            "action": "PAUSE_MIGRATION",
            "differences": differences
        }

    return {
        "parity": "MATCH",
        "status": "PASS",
        "action": "CONTINUE_MIGRATION",
        "differences": []
    }

print('Validation module loaded successfully.')