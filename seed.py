from database import SessionLocal, Base, engine
from models import Patient, LegacyPatient, ModernPatient

Base.metadata.create_all(bind=engine)


patients = [
    Patient(patient_id="P1024"),
    Patient(patient_id="P2048"),
    Patient(patient_id="P3011"),
    Patient(patient_id="P4096"),
    Patient(patient_id="P5120")
]


legacy_patients = [
    LegacyPatient(
        patient_id="P1024",
        PID="P1024",
        PT_NM="Aarav Sharma",
        AGE_YRS=22,
        DX="Hypertension"
    ),
    LegacyPatient(
        patient_id="P2048",
        PID="P2048",
        PT_NM="Meera Kapoor",
        AGE_YRS=34,
        DX="Type 2 Diabetes"
    ),
    LegacyPatient(
        patient_id="P3011",
        PID="P3011",
        PT_NM="Rohan Mehta",
        AGE_YRS=47,
        DX="Asthma"
    ),
    LegacyPatient(
        patient_id="P4096",
        PID="P4096",
        PT_NM="Ananya Singh",
        AGE_YRS=29,
        DX="Migraine"
    ),
    LegacyPatient(
        patient_id="P5120",
        PID="P5120",
        PT_NM="Kabir Malhotra",
        AGE_YRS=61,
        DX="Coronary Artery Disease"
    )
]


modern_patients = [
    ModernPatient(
        patient_id="P1024",
        name="Aarav Sharma",
        age=25,  # INTENTIONAL VALUE MISMATCH
        diagnosis="Hypertension"
    ),
    ModernPatient(
        patient_id="P2048",
        name="Meera Kapoor",
        age=34,
        diagnosis="Type 2 Diabetes"
    ),
    ModernPatient(
        patient_id="P3011",
        name="Rohan Mehta",
        age=47,
        diagnosis="Asthma"
    ),
    ModernPatient(
        patient_id="P4096",
        name="Ananya Singh",
        age=29,
        diagnosis="Migraine"
    ),
    ModernPatient(
        patient_id="P5120",
        name="Kabir Malhotra",
        age=61,
        diagnosis="Coronary Artery Disease"
    )
]


db = SessionLocal()

try:
    db.add_all(patients)
    db.add_all(legacy_patients)
    db.add_all(modern_patients)
    db.commit()

    print("HOSP-OLD and HOSP-NEW seeded successfully!")

finally:
    db.close()

print("Database session closed after seeding.")