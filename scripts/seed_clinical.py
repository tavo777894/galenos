"""
Minimal clinical seed script.
Creates admin, doctor, one patient, and one signed cardiology encounter.
"""
import os
from datetime import date

from sqlalchemy import or_

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.encounter import Encounter, MedicalSpecialty, EncounterStatus


def get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def upsert_user(db, *, email: str, username: str, password: str, full_name: str, role: UserRole):
    user = db.query(User).filter(or_(User.email == email, User.username == username)).first()
    if user:
        print(f"[EXISTS] User {username} ({email}) id={user.id}")
        return user, False

    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    print(f"[CREATED] User {username} ({email}) id={user.id}")
    return user, True


def upsert_patient(
    db,
    *,
    ci: str,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    phone: str,
    email: str,
    address: str,
    emergency_contact_name: str,
    emergency_contact_phone: str,
    emergency_contact_relationship: str,
    allergies: str,
    medical_history: str,
):
    patient = db.query(Patient).filter(Patient.ci == ci).first()
    if patient:
        print(f"[EXISTS] Patient ci={ci} id={patient.id}")
        return patient, False

    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        ci=ci,
        date_of_birth=date_of_birth,
        phone=phone,
        email=email,
        address=address,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
        emergency_contact_relationship=emergency_contact_relationship,
        allergies=allergies,
        medical_history=medical_history,
    )
    db.add(patient)
    db.flush()
    print(f"[CREATED] Patient ci={ci} id={patient.id}")
    return patient, True


def upsert_template_if_models_exist(db):
    try:
        from app.models.template import Template
        from app.models.encounter import MedicalSpecialty
    except Exception:
        print("[SKIP] Template model not available")
        return None, False

    title = "Consulta Cardiologia - Evaluacion Cardiovascular"
    template = (
        db.query(Template)
        .filter(Template.specialty == MedicalSpecialty.CARDIOLOGIA, Template.title == title)
        .first()
    )
    if template:
        print(f"[EXISTS] Template '{title}' id={template.id}")
        return template, False

    template = Template(
        title=title,
        description="Cardiology SOAP template",
        specialty=MedicalSpecialty.CARDIOLOGIA,
        default_subjective="Motivo de consulta: dolor toracico de esfuerzo.",
        default_objective="Signos vitales y examen cardiovascular basico.",
        default_assessment="Impresion clinica cardiologica inicial.",
        default_plan="Plan inicial: estudios, tratamiento y seguimiento.",
        is_active=1,
        requires_photo=0,
    )
    db.add(template)
    db.flush()
    print(f"[CREATED] Template '{title}' id={template.id}")
    return template, True


def upsert_snippet_if_models_exist(db):
    try:
        from app.models.snippet import Snippet, SnippetCategory
        from app.models.encounter import MedicalSpecialty
    except Exception:
        print("[SKIP] Snippet model not available")
        return None, False

    if not hasattr(SnippetCategory, "PLAN"):
        print("[SKIP] SnippetCategory not available")
        return None, False

    title = "Plan cardiologia - control"
    category = SnippetCategory.PLAN
    snippet = (
        db.query(Snippet)
        .filter(
            Snippet.specialty == MedicalSpecialty.CARDIOLOGIA,
            Snippet.category == category,
            Snippet.title == title,
        )
        .first()
    )
    if snippet:
        print(f"[EXISTS] Snippet '{title}' id={snippet.id}")
        return snippet, False

    snippet = Snippet(
        specialty=MedicalSpecialty.CARDIOLOGIA,
        category=category,
        title=title,
        content="1. ECG y ecocardiograma. 2. Labs basicos. 3. Control en 7 dias.",
        is_active=1,
    )
    db.add(snippet)
    db.flush()
    print(f"[CREATED] Snippet '{title}' id={snippet.id}")
    return snippet, True


def upsert_encounter_seed(db, *, patient: Patient, doctor: User, template):
    prefix = "[SEED_CLINICAL]"
    encounter = (
        db.query(Encounter)
        .filter(
            Encounter.patient_id == patient.id,
            Encounter.doctor_id == doctor.id,
            Encounter.specialty == MedicalSpecialty.CARDIOLOGIA,
            Encounter.status == EncounterStatus.SIGNED,
            Encounter.subjective.like(f"{prefix}%"),
        )
        .first()
    )
    if encounter:
        print(f"[EXISTS] Encounter id={encounter.id}")
        return encounter, False

    subjective = (
        f"{prefix} Patient reports intermittent chest pressure for 2 weeks, "
        "worse with exertion and relieved by rest. No syncope or fever. "
        "Family history of coronary disease."
    )
    objective = (
        "BP 138/86 mmHg, HR 84 bpm, RR 16, SpO2 98%. "
        "Cardiac exam: regular rhythm, no murmurs. Lungs clear. No edema."
    )
    assessment = (
        "Chest pain likely stable angina. Risk factors: HTN, dyslipidemia. "
        "Rule out ischemia."
    )
    plan = (
        "1. ECG today. 2. Echocardiogram and lipid profile. "
        "3. Start aspirin 81mg and statin if no contraindication. "
        "4. Lifestyle counseling and follow-up in 2 weeks."
    )

    encounter = Encounter(
        patient_id=patient.id,
        doctor_id=doctor.id,
        specialty=MedicalSpecialty.CARDIOLOGIA,
        status=EncounterStatus.SIGNED,
        template_id=template.id if template else None,
        subjective=subjective,
        objective=objective,
        assessment=assessment,
        plan=plan,
    )
    db.add(encounter)
    db.flush()
    print(f"[CREATED] Encounter id={encounter.id}")
    return encounter, True


def main():
    admin_email = get_env("SEED_ADMIN_EMAIL", "admin@galenos.com")
    admin_username = get_env("SEED_ADMIN_USERNAME", "admin")
    admin_password = get_env("SEED_ADMIN_PASSWORD", "admin123")

    doctor_email = get_env("SEED_DOCTOR_EMAIL", "doctor@galenos.com")
    doctor_username = get_env("SEED_DOCTOR_USERNAME", "doctor")
    doctor_password = get_env("SEED_DOCTOR_PASSWORD", "doctor123")

    db = SessionLocal()
    try:
        admin_user, _ = upsert_user(
            db,
            email=admin_email,
            username=admin_username,
            password=admin_password,
            full_name="Admin User",
            role=UserRole.ADMIN,
        )
        doctor_user, _ = upsert_user(
            db,
            email=doctor_email,
            username=doctor_username,
            password=doctor_password,
            full_name="Dr. Ana Ruiz",
            role=UserRole.DOCTOR,
        )

        patient, _ = upsert_patient(
            db,
            ci="88442211",
            first_name="Maria",
            last_name="Salazar",
            date_of_birth=date(1987, 6, 14),
            phone="+591 70112233",
            email="maria.salazar@example.com",
            address="Av Central 123, La Paz",
            emergency_contact_name="Luis Salazar",
            emergency_contact_phone="+591 70112234",
            emergency_contact_relationship="Hermano",
            allergies="No known drug allergies",
            medical_history="HTN diagnosed in 2021, on amlodipine.",
        )

        template, _ = upsert_template_if_models_exist(db)
        snippet, _ = upsert_snippet_if_models_exist(db)
        encounter, _ = upsert_encounter_seed(db, patient=patient, doctor=doctor_user, template=template)

        admin_id = admin_user.id
        doctor_id = doctor_user.id
        patient_id = patient.id
        patient_ci = patient.ci
        template_id = template.id if template else None
        template_title = template.title if template else None
        snippet_id = snippet.id if snippet else None
        snippet_title = snippet.title if snippet else None
        encounter_id = encounter.id
        encounter_specialty = encounter.specialty
        encounter_status = encounter.status

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("")
    print("Seed summary")
    print(f"Admin: id={admin_id} email={admin_email} username={admin_username} password={admin_password}")
    print(f"Doctor: id={doctor_id} email={doctor_email} username={doctor_username} password={doctor_password}")
    print(f"Patient: id={patient_id} ci={patient_ci}")
    print(f"Encounter: id={encounter_id} specialty={encounter_specialty} status={encounter_status}")
    if template_id:
        print(f"Template: id={template_id} title='{template_title}'")
    if snippet_id:
        print(f"Snippet: id={snippet_id} title='{snippet_title}'")


if __name__ == "__main__":
    main()
