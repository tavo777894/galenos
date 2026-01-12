"""
Seed script to populate database with initial test data.
"""
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.template import Template
from app.models.snippet import Snippet, SnippetCategory
from app.models.encounter import MedicalSpecialty
from app.core.security import get_password_hash


def create_users(db):
    """Create initial users."""
    print("Creating users...")

    # Check if users already exist
    if db.query(User).count() > 0:
        print("Users already exist. Skipping user creation.")
        return

    # Create admin user
    admin_user = User(
        email="admin@galenos.com",
        username="admin",
        full_name="Administrator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin_user)

    # Create doctor user
    doctor_user = User(
        email="doctor@galenos.com",
        username="doctor",
        full_name="Dr. Juan Pérez",
        hashed_password=get_password_hash("doctor123"),
        role=UserRole.DOCTOR,
        is_active=True
    )
    db.add(doctor_user)

    # Create secretary user
    secretary_user = User(
        email="secretaria@galenos.com",
        username="secretaria",
        full_name="María González",
        hashed_password=get_password_hash("secretaria123"),
        role=UserRole.SECRETARIA,
        is_active=True
    )
    db.add(secretary_user)

    db.commit()
    print("✓ Created 3 users (admin, doctor, secretaria)")


def create_patients(db):
    """Create sample patients."""
    print("Creating sample patients...")

    # Check if patients already exist
    if db.query(Patient).count() > 0:
        print("Patients already exist. Skipping patient creation.")
        return

    # Sample patients with complete information
    patients = [
        Patient(
            first_name="Carlos",
            last_name="Rodríguez",
            ci="12345678",
            date_of_birth=date(1985, 3, 15),
            phone="+591 70123456",
            email="carlos.rodriguez@email.com",
            address="Av. Libertador 456, La Paz",
            emergency_contact_name="Ana Rodríguez",
            emergency_contact_phone="+591 70123457",
            emergency_contact_relationship="Esposa",
            allergies="Penicilina, Polen de árboles",
            medical_history="Hipertensión controlada con medicación desde 2018. Cirugía de apéndice en 2010. Antecedentes familiares de diabetes."
        ),
        Patient(
            first_name="Ana María",
            last_name="Martínez",
            ci="87654321",
            date_of_birth=date(1992, 7, 22),
            phone="+591 71234567",
            email="ana.martinez@email.com",
            address="Calle Murillo 123, Santa Cruz",
            emergency_contact_name="Pedro Martínez",
            emergency_contact_phone="+591 71234568",
            emergency_contact_relationship="Padre",
            allergies="Ninguna conocida",
            medical_history="Diabetes tipo 2 diagnosticada en 2020. Control regular con endocrinólogo. Sin complicaciones hasta la fecha."
        ),
        Patient(
            first_name="José",
            last_name="López",
            ci="11223344",
            date_of_birth=date(1978, 11, 8),
            phone="+591 72345678",
            email=None,
            address="Zona Norte, Cochabamba",
            emergency_contact_name="María López",
            emergency_contact_phone="+591 72345679",
            emergency_contact_relationship="Hermana",
            allergies="Mariscos, Látex",
            medical_history="Asma desde la infancia. Tratamiento con inhaladores (Salbutamol). Episodios controlados con medicación preventiva."
        ),
        Patient(
            first_name="Sofía",
            last_name="García",
            ci="99887766",
            date_of_birth=date(2000, 5, 12),
            phone="+591 73456789",
            email="sofia.garcia@email.com",
            address="Calle 6 de Agosto 789, Oruro",
            emergency_contact_name="Roberto García",
            emergency_contact_phone="+591 73456780",
            emergency_contact_relationship="Padre",
            allergies="Ninguna",
            medical_history="Paciente sana. Sin antecedentes médicos relevantes."
        ),
        Patient(
            first_name="Miguel",
            last_name="Fernández",
            ci="55443322",
            date_of_birth=date(1995, 9, 30),
            phone="+591 74567890",
            email="miguel.fernandez@email.com",
            address="Av. América 321, Sucre",
            emergency_contact_name="Laura Fernández",
            emergency_contact_phone="+591 74567891",
            emergency_contact_relationship="Madre",
            allergies="Aspirina, Ibuprofeno",
            medical_history="Alergia a AINEs descubierta en 2019. Utiliza paracetamol como analgésico alternativo."
        ),
    ]

    for patient in patients:
        db.add(patient)

    db.commit()
    print(f"✓ Created {len(patients)} sample patients")


def create_templates(db):
    """Create initial SOAP templates - 5 total (including 2 dermatology templates)."""
    print("Creating SOAP templates...")

    # Check if templates already exist
    if db.query(Template).count() > 0:
        print("Templates already exist. Skipping template creation.")
        return

    templates = [
        # CARDIOLOGIA Template
        Template(
            title="Consulta Cardiológica - Evaluación Cardiovascular",
            description="Plantilla para consultas de cardiología",
            specialty=MedicalSpecialty.CARDIOLOGIA,
            default_subjective="Motivo de consulta:\n\nSíntomas cardiovasculares:\n- Dolor torácico: \n- Disnea: \n- Palpitaciones: \n- Síncope: \n- Edema: \n\nFactores de riesgo cardiovascular:\n- HTA: \n- DM: \n- Dislipidemia: \n- Tabaquismo: \n- Antecedentes familiares:",
            default_objective="Signos vitales:\n- PA: ___ / ___ mmHg\n- FC: ___ lpm\n- FR: ___ rpm\n- SatO2: ___  %\n\nExamen cardiovascular:\n- Ruidos cardíacos: \n- Soplos: \n- Pulsos periféricos: \n- Edema: \n- Ingurgitación yugular:",
            default_assessment="Impresión diagnóstica:\n\nRiesgo cardiovascular:\n\nClasificación funcional NYHA/Killip:",
            default_plan="Plan terapéutico:\n1. Manejo farmacológico:\n2. Estudios complementarios (ECG, ecocardiograma, laboratorio):\n3. Modificación de factores de riesgo:\n4. Seguimiento:\n5. Criterios de interconsulta/hospitalización:",
            is_active=1,
            requires_photo=0
        ),
        # NEUROLOGIA Template
        Template(
            title="Consulta Neurológica - Evaluación Neurológica",
            description="Plantilla para consultas de neurología",
            specialty=MedicalSpecialty.NEUROLOGIA,
            default_subjective="Motivo de consulta:\n\nSíntomas neurológicos:\n- Cefalea: \n- Alteración de conciencia: \n- Déficit motor: \n- Alteración sensitiva: \n- Convulsiones: \n- Vértigo/mareo: \n\nAntecedentes neurológicos:\nMedicación actual:",
            default_objective="Signos vitales:\n- PA: ___ / ___ mmHg\n- FC: ___ lpm\n- Glasgow: ___/15\n\nExamen neurológico:\n- Estado mental: \n- Pares craneales: \n- Sistema motor: Fuerza __/5, Tono, Reflejos\n- Sistema sensitivo: \n- Coordinación y marcha: \n- Signos meníngeos:",
            default_assessment="Síndrome neurológico:\n\nDiagnóstico topográfico:\n\nDiagnóstico etiológico:\n\nDiagnósticos diferenciales:",
            default_plan="Plan de manejo:\n1. Medicación neurológica:\n2. Estudios de imagen (TC, RM):\n3. Estudios neurofisiológicos (EEG, EMG):\n4. Laboratorio específico:\n5. Rehabilitación neurológica:\n6. Seguimiento ambulatorio:",
            is_active=1,
            requires_photo=0
        ),
        # DERMATOLOGIA Template 1 - Lesión cutánea (REQUIRES PHOTO)
        Template(
            title="Dermatología - Lesión cutánea",
            description="Plantilla para evaluación de lesiones cutáneas sospechosas (requiere fotografía clínica)",
            specialty=MedicalSpecialty.DERMATOLOGIA,
            default_subjective="Motivo de consulta:\n\nLesión cutánea:\n- Localización anatómica: \n- Tiempo de evolución: \n- Tamaño aproximado: \n- Cambios recientes (tamaño, forma, color, sangrado): \n- Síntomas asociados (prurito, dolor, ardor): \n- Exposición solar: \n- Tratamientos previos: \n\nAntecedentes:\n- Fototipo cutáneo (Fitzpatrick): \n- Antecedentes de cáncer de piel: \n- Lesiones pigmentadas previas:",
            default_objective="Examen dermatológico:\n\nLesión cutánea:\n- Localización exacta: \n- Tamaño (mm o cm): \n- Morfología: \n- Bordes: \n- Color: \n- Superficie: \n- Palpación: \n\nCriterios ABCDE:\n- Asimetría: [ ] Sí [ ] No\n- Bordes irregulares: [ ] Sí [ ] No\n- Color heterogéneo: [ ] Sí [ ] No\n- Diámetro >6mm: [ ] Sí [ ] No\n- Evolución/cambios: [ ] Sí [ ] No\n\nDermatoscopia: \nGanglios regionales:",
            default_assessment="Diagnóstico presuntivo:\n\nRiesgo de malignidad:\n- [ ] Bajo\n- [ ] Moderado\n- [ ] Alto\n\nIndicación de biopsia: [ ] Sí [ ] No\n\nTipo de biopsia recomendada:",
            default_plan="Plan de manejo:\n1. Documentación fotográfica (OBLIGATORIO)\n2. Biopsia: Tipo y margen\n3. Estudio histopatológico\n4. Según resultado histológico: conducta definitiva\n5. Educación sobre signos de alarma\n6. Fotoprotección estricta\n7. Autoexamen mensual\n8. Control: ",
            is_active=1,
            requires_photo=1  # REQUIERE FOTO
        ),
        # DERMATOLOGIA Template 2 - Control (NO REQUIRES PHOTO)
        Template(
            title="Dermatología - Control",
            description="Plantilla para controles dermatológicos de seguimiento",
            specialty=MedicalSpecialty.DERMATOLOGIA,
            default_subjective="Motivo de consulta:\n\nControl de seguimiento de:\n\nEvolución desde última consulta:\n- Mejoría: \n- Sin cambios: \n- Empeoramiento: \n\nAdherencia al tratamiento:\nEfectos adversos de medicación:\nNuevos síntomas:",
            default_objective="Examen dermatológico:\n\nÁrea previamente afectada:\n- Estado actual: \n- Signos de actividad: \n- Lesiones residuales: \n\nSignos vitales (si procede):\nExamen general de piel:",
            default_assessment="Evaluación de respuesta al tratamiento:\n\nEstado actual de la dermatosis:\n- [ ] Remisión completa\n- [ ] Remisión parcial\n- [ ] Sin cambios\n- [ ] Progresión\n\nNecesidad de ajuste terapéutico:",
            default_plan="Plan de seguimiento:\n1. Continuar tratamiento actual: \n2. Ajustes de medicación: \n3. Medidas generales: \n4. Estudios complementarios si requiere: \n5. Próximo control: \n6. Criterios de reconsulta anticipada:",
            is_active=1,
            requires_photo=0  # NO REQUIERE FOTO
        ),
        # CIRUGIA_CARDIOVASCULAR Template
        Template(
            title="Consulta Cirugía Cardiovascular - Evaluación Quirúrgica",
            description="Plantilla para consultas de cirugía cardiovascular",
            specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR,
            default_subjective="Motivo de interconsulta:\n\nPatología cardiovascular:\n- Cardiopatía: \n- Arteriopatía: \n- Enfermedad valvular: \n- Aneurisma: \n\nSíntomas:\n- Clase funcional: \n- Angina: \n- Claudicación: \n\nComorbilidades:\n- Riesgo quirúrgico estimado:",
            default_objective="Signos vitales:\n- PA: ___ / ___ mmHg (ambos brazos)\n- FC: ___ lpm\n- SatO2: ___ %\n\nExamen cardiovascular:\n- Soplos: \n- Pulsos: \n- Edema: \n\nExamen vascular periférico:\n- Pulsos distales: \n- Signos de isquemia:",
            default_assessment="Diagnóstico cardiovascular quirúrgico:\n\nIndicación quirúrgica:\n\nRiesgo quirúrgico (EuroSCORE/STS):\n\nContraindicaciones:",
            default_plan="Plan quirúrgico:\n1. Procedimiento propuesto:\n2. Estudios preoperatorios (ecocardiograma, cateterismo, angioTC):\n3. Optimización preoperatoria:\n4. Consentimiento informado:\n5. Programación quirúrgica:\n6. Seguimiento postoperatorio:",
            is_active=1,
            requires_photo=0
        )
    ]

    for template in templates:
        db.add(template)

    db.commit()
    print(f"✓ Created {len(templates)} SOAP templates (5 total: 2 dermatology + 1 per other specialty)")


def create_snippets(db):
    """Create initial text snippets - 15 per specialty (60 total)."""
    print("Creating text snippets...")

    # Check if snippets already exist
    if db.query(Snippet).count() > 0:
        print("Snippets already exist. Skipping snippet creation.")
        return

    snippets = []

    # ========== CARDIOLOGIA (15 snippets) ==========
    snippets.extend([
        # MOTIVO (3)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.MOTIVO, title="Dolor precordial",
                content="Dolor precordial de tipo opresivo, EVA 7/10, con irradiación a miembro superior izquierdo y mandíbula, de 2 horas de evolución.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.MOTIVO, title="Disnea de esfuerzo",
                content="Disnea de medianos esfuerzos, clase funcional NYHA II, de 3 meses de evolución, sin ortopnea ni disnea paroxística nocturna.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.MOTIVO, title="Palpitaciones",
                content="Palpitaciones de inicio súbito, de tipo taquicárdico, sin síncope asociado, duración aproximada de 15 minutos.", is_active=1),

        # ANTECEDENTES (2)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.ANTECEDENTES, title="Factores de riesgo CV",
                content="Factores de riesgo cardiovascular: HTA en tratamiento desde hace 5 años, dislipidemia, tabaquismo activo 20 paquetes/año. Antecedente familiar de IAM en padre a los 55 años.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.ANTECEDENTES, title="Cardiopatía isquémica previa",
                content="Antecedente de IAM anteroseptal hace 2 años, tratado con angioplastia + stent en DA. Actualmente en doble antiagregación.", is_active=1),

        # EXAMEN (3)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.EXAMEN, title="Auscultación cardíaca normal",
                content="Ruidos cardíacos rítmicos, normofonéticos, sin soplos audibles. Pulsos periféricos simétricos y palpables. No edema en miembros inferiores.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.EXAMEN, title="Insuficiencia cardíaca",
                content="Taquicárdico, taquipneico. Ingurgitación yugular positiva. Estertores crepitantes bibasales. Reflujo hepatoyugular positivo. Edema bilateral hasta tercio medio de piernas ++/+++.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.EXAMEN, title="Soplo cardíaco",
                content="Soplo sistólico grado III/VI en foco mitral, irradiado a axila. Primer ruido disminuido. Sin tercer ruido audible.", is_active=1),

        # DX (3)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.DX, title="Síndrome coronario agudo",
                content="Síndrome coronario agudo con elevación del ST. STEMI anteroseptal. Killip I.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.DX, title="Insuficiencia cardíaca",
                content="Insuficiencia cardíaca descompensada, clase funcional NYHA III. FE deprimida (<40% por ecocardiograma previo).", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.DX, title="Fibrilación auricular",
                content="Fibrilación auricular de novo, respuesta ventricular rápida. CHA2DS2-VASc: 3 puntos. HAS-BLED: 1 punto.", is_active=1),

        # PLAN (2)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.PLAN, title="Manejo SCA",
                content="1. Doble antiagregación (AAS 100mg + Clopidogrel 75mg)\n2. Estatina de alta intensidad (Atorvastatina 80mg)\n3. Betabloqueante (Metoprolol)\n4. IECA\n5. Cateterismo cardíaco urgente\n6. Monitoreo en UCIC", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.PLAN, title="Manejo IC",
                content="1. Diurético de asa (Furosemida 40mg c/12h)\n2. IECA o ARA II\n3. Betabloqueante (titular dosis)\n4. Espironolactona 25mg/día\n5. Restricción hídrica <1.5L/día\n6. Dieta hiposódica estricta\n7. Control ambulatorio en 7 días", is_active=1),

        # INDICACIONES (2)
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.INDICACIONES, title="Signos de alarma cardíacos",
                content="Acudir a emergencias si presenta: dolor torácico intenso, dificultad para respirar en reposo, palpitaciones sostenidas, síncope, edema progresivo.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CARDIOLOGIA, category=SnippetCategory.INDICACIONES, title="Control post alta",
                content="Control por consultorio externo de cardiología en 7 días con: ECG, ecocardiograma, laboratorio (troponinas, BNP, perfil lipídico, función renal).", is_active=1),
    ])

    # ========== NEUROLOGIA (15 snippets) ==========
    snippets.extend([
        # MOTIVO (3)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.MOTIVO, title="Cefalea intensa",
                content="Cefalea de inicio súbito, tipo explosivo, intensidad 10/10, localizada en región occipital, sin antecedente traumático, de 3 horas de evolución.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.MOTIVO, title="Déficit motor hemicuerpo",
                content="Debilidad súbita de hemicuerpo derecho, de aproximadamente 2 horas de evolución, asociado a disartria y desviación de comisura labial.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.MOTIVO, title="Crisis convulsiva",
                content="Crisis convulsiva tónico-clónica generalizada, con pérdida del conocimiento, duración aproximada de 2 minutos, fase post-ictal con confusión.", is_active=1),

        # ANTECEDENTES (2)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.ANTECEDENTES, title="Epilepsia conocida",
                content="Antecedente de epilepsia desde hace 5 años, en tratamiento con ácido valproico 500mg c/12h, última crisis hace 6 meses. Buen control hasta el episodio actual.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.ANTECEDENTES, title="ACV previo",
                content="Antecedente de ACV isquémico hace 1 año, con secuela de hemiparesia derecha residual leve. En tratamiento antiagregante con AAS 100mg.", is_active=1),

        # EXAMEN (3)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.EXAMEN, title="Examen neurológico normal",
                content="Glasgow 15/15. Pupilas isocóricas, reactivas. Pares craneales sin alteraciones. Fuerza muscular 5/5 en cuatro extremidades. Reflejos osteotendinosos ++/++++ simétricos. Sensibilidad conservada. Coordinación y marcha normales. Romberg negativo.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.EXAMEN, title="Síndrome piramidal",
                content="Hemiplejía derecha. Fuerza muscular MSD 2/5, MID 1/5. Hiperreflexia en hemicuerpo derecho. Babinski positivo derecho. Hipoestesia hemicuerpo derecho.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.EXAMEN, title="Signos meníngeos",
                content="Rigidez de nuca presente. Kernig positivo. Brudzinski positivo. Paciente en posición antálgica. Fotofobia y fonofobia presentes.", is_active=1),

        # DX (3)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.DX, title="ACV isquémico agudo",
                content="Accidente cerebrovascular isquémico agudo, territorio de arteria cerebral media izquierda. NIHSS: 12 puntos. Ventana terapéutica para trombólisis.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.DX, title="Meningitis",
                content="Meningitis aguda bacteriana. Sospecha de etiología meningocócica. Requiere confirmación por punción lumbar.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.DX, title="Migraña con aura",
                content="Migraña con aura visual. Cefalea hemicraneal pulsátil. Cumple criterios ICHD-3 para migraña con aura.", is_active=1),

        # PLAN (2)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.PLAN, title="Manejo ACV agudo",
                content="1. Activación código ACV\n2. TC cerebral sin contraste urgente\n3. Trombólisis IV (rtPA) si dentro de ventana terapéutica\n4. Antiagregación posterior\n5. Monitoreo UCI neurológica\n6. Rehabilitación temprana", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.PLAN, title="Manejo crisis convulsiva",
                content="1. Lorazepam 4mg IV stat\n2. Fenitoína 18mg/kg dosis de carga\n3. EEG\n4. TC cerebral\n5. Laboratorio (electrolitos, glucosa, función hepática)\n6. Ajuste de anticonvulsivantes según niveles", is_active=1),

        # INDICACIONES (2)
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.INDICACIONES, title="Signos de alarma neurológicos",
                content="Acudir inmediatamente a emergencias si presenta: cefalea tipo trueno, debilidad súbita, alteración del habla, visión doble, pérdida de equilibrio, convulsiones, alteración de conciencia.", is_active=1),
        Snippet(specialty=MedicalSpecialty.NEUROLOGIA, category=SnippetCategory.INDICACIONES, title="Seguimiento neurología",
                content="Control por neurología en 10 días con: TC o RM cerebral de control, EEG, niveles séricos de anticonvulsivantes si corresponde.", is_active=1),
    ])

    # ========== DERMATOLOGIA (15 snippets) ==========
    snippets.extend([
        # MOTIVO (3)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.MOTIVO, title="Lesión cutánea pruriginosa",
                content="Lesiones eritematosas pruriginosas en tronco y extremidades, de 5 días de evolución, prurito intenso nocturno que interfiere con el sueño.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.MOTIVO, title="Nódulo cutáneo",
                content="Nódulo en piel de brazo izquierdo, de crecimiento progresivo en los últimos 3 meses, asintomático, sin cambios de coloración recientes.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.MOTIVO, title="Dermatosis facial",
                content="Lesiones faciales tipo pápulo-pustulosas en región centro-facial, eritema y telangiectasias, exacerbadas por exposición solar y alimentos picantes.", is_active=1),

        # ANTECEDENTES (2)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.ANTECEDENTES, title="Atopia",
                content="Antecedentes personales de dermatitis atópica en infancia, asma bronquial, rinitis alérgica. Antecedentes familiares de atopia en madre y hermano.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.ANTECEDENTES, title="Fototipo cutáneo",
                content="Fototipo II de Fitzpatrick. Piel clara, cabello rubio, ojos claros. Antecedente de quemaduras solares frecuentes en infancia. Múltiples nevos.", is_active=1),

        # EXAMEN (3)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.EXAMEN, title="Exantema maculopapular",
                content="Exantema maculopapular eritematoso, confluente, no pruriginoso, distribuido en tronco y extremidades, respeta palmas y plantas. No descamación.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.EXAMEN, title="Neoformación pigmentada",
                content="Lesión pigmentada de 8mm de diámetro, bordes irregulares, asimetría, coloración heterogénea (marrón claro y oscuro), superficie plana. ABCDE sospechoso.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.EXAMEN, title="Onicomicosis",
                content="Uñas de pies con distrofia ungueal, hiperqueratosis subungueal, coloración amarillenta, onicolisis distal. Afecta principalmente primer y quinto ortejo bilateral.", is_active=1),

        # DX (3)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.DX, title="Dermatitis atópica",
                content="Dermatitis atópica moderada. Lesiones eccematosas en pliegues antecubitales y poplíteos. SCORAD: 35 puntos.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.DX, title="Melanoma sospechoso",
                content="Lesión pigmentada sospechosa de melanoma. Criterios ABCDE presentes. Indicación de biopsia excisional con margen.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.DX, title="Psoriasis",
                content="Psoriasis vulgar en placas. Lesiones eritemato-descamativas en codos, rodillas y región sacra. PASI: 12.", is_active=1),

        # PLAN (2)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.PLAN, title="Tratamiento dermatitis",
                content="1. Corticoide tópico potencia media (Mometasona 0.1% crema) c/12h x 14 días\n2. Emolientes frecuentes\n3. Antihistamínico oral nocturno (Hidroxizina 25mg)\n4. Evitar jabones irritantes\n5. Control en 15 días", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.PLAN, title="Biopsia cutánea",
                content="1. Biopsia excisional de lesión con margen de 2mm\n2. Estudio histopatológico\n3. Según resultado: ampliación de márgenes si corresponde\n4. Resultado en 7-10 días\n5. Reevaluación con histopatología", is_active=1),

        # INDICACIONES (2)
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.INDICACIONES, title="Signos de alarma dermatológicos",
                content="Consultar urgente si presenta: crecimiento rápido de lesiones, sangrado espontáneo, cambio de coloración, úlceras que no cicatrizan, fiebre con rash.", is_active=1),
        Snippet(specialty=MedicalSpecialty.DERMATOLOGIA, category=SnippetCategory.INDICACIONES, title="Fotoprotección",
                content="Fotoprotección estricta: protector solar FPS 50+ cada 3 horas, evitar exposición solar 10am-4pm, uso de sombrero de ala ancha y ropa protectora. Autoexamen mensual de lunares.", is_active=1),
    ])

    # ========== CIRUGIA_CARDIOVASCULAR (15 snippets) ==========
    snippets.extend([
        # MOTIVO (3)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.MOTIVO, title="Evaluación preoperatoria cardíaca",
                content="Interconsulta para evaluación preoperatoria cardiovascular. Paciente programado para cirugía cardíaca electiva. Valoración de riesgo quirúrgico.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.MOTIVO, title="Claudicación intermitente",
                content="Claudicación intermitente de miembro inferior derecho, aparece a 100 metros de marcha, EVA 8/10, alivia con reposo. Evolución de 6 meses.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.MOTIVO, title="Aneurisma detectado",
                content="Hallazgo incidental de aneurisma de aorta abdominal en ecografía de rutina. Asintomático. Requiere evaluación para manejo quirúrgico vs observación.", is_active=1),

        # ANTECEDENTES (2)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.ANTECEDENTES, title="Cardiopatía valvular",
                content="Antecedente de estenosis aórtica severa (área valvular 0.8cm²) diagnosticada hace 1 año. Clase funcional NYHA II-III. Fracción de eyección conservada 60%.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.ANTECEDENTES, title="Enfermedad coronaria",
                content="Enfermedad coronaria multivaso: lesión significativa en DA proximal 80%, CX 70%, CD 60%. Angina CCS III refractaria a tratamiento médico óptimo.", is_active=1),

        # EXAMEN (3)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.EXAMEN, title="Soplo valvular",
                content="Soplo sistólico eyectivo grado IV/VI en foco aórtico, irradiado a carótidas. Pulso parvus et tardus. Presión diferencial estrecha. No signos de IC.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.EXAMEN, title="Isquemia arterial",
                content="Miembro inferior derecho pálido, frío. Pulso femoral +, poplíteo disminuido, pedio y tibial posterior no palpables. Llenado capilar >3 segundos. Claudicometría 100m.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.EXAMEN, title="Masa pulsátil abdominal",
                content="Masa pulsátil en mesogastrio, aprox 6cm de diámetro, no dolorosa, expansible, soplo sistólico audible. Compatible con aneurisma aórtico abdominal.", is_active=1),

        # DX (3)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.DX, title="Estenosis aórtica severa",
                content="Estenosis aórtica severa sintomática. Área valvular 0.7cm². Gradiente medio 50mmHg. Indicación clase I para reemplazo valvular aórtico.", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.DX, title="Enfermedad coronaria quirúrgica",
                content="Enfermedad coronaria multivaso no revascularizable por vía percutánea. SYNTAX score 35. Indicación de revascularización quirúrgica (CABG).", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.DX, title="AAA",
                content="Aneurisma de aorta abdominal infrarrenal de 5.8cm de diámetro máximo. Indicación quirúrgica por tamaño (>5.5cm). EuroSCORE II: 3.5%.", is_active=1),

        # PLAN (2)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.PLAN, title="CABG programada",
                content="1. Revascularización miocárdica quirúrgica (CABG) programada\n2. Cateterismo cardíaco actualizado\n3. Ecocardiograma transtorácico\n4. Laboratorio preoperatorio completo\n5. Evaluación preanestésica\n6. Consentimiento informado\n7. Programación quirúrgica", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.PLAN, title="Reemplazo valvular",
                content="1. Reemplazo valvular aórtico programado\n2. Decisión de tipo de prótesis (mecánica vs biológica)\n3. Ecocardiograma transesofágico\n4. Cateterismo cardíaco\n5. Evaluación dental preoperatoria\n6. Suspender antiagregantes según protocolo\n7. Ingreso programado", is_active=1),

        # INDICACIONES (2)
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.INDICACIONES, title="Preparación preoperatoria",
                content="Indicaciones preoperatorias:\n- Ayuno 8 horas\n- Baño con jabón antiséptico noche previa y mañana cirugía\n- Suspender antiagregantes según indicación\n- Continuar betabloqueante\n- Presentarse con familiar adulto\n- Traer estudios previos", is_active=1),
        Snippet(specialty=MedicalSpecialty.CIRUGIA_CARDIOVASCULAR, category=SnippetCategory.INDICACIONES, title="Cuidados postoperatorios",
                content="Post-quirúrgico:\n- UCO 48-72h\n- Extubación precoz (<6h)\n- Deambulación temprana 24h\n- Espirometría incentivada\n- Manejo del dolor\n- Rehabilitación cardíaca\n- Anticoagulación según tipo de válvula\n- Control ambulatorio 7 días", is_active=1),
    ])

    for snippet in snippets:
        db.add(snippet)

    db.commit()
    print(f"✓ Created {len(snippets)} professional snippets (15 per specialty)")


def init_db():
    """Initialize database with seed data."""
    print("=" * 60)
    print("INICIALIZANDO BASE DE DATOS - SPRINT 3")
    print("=" * 60)

    # Create tables
    print("\nCreando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")

    # Create session
    db = SessionLocal()

    try:
        # Seed data
        create_users(db)
        create_patients(db)
        create_templates(db)
        create_snippets(db)

        print("\n" + "=" * 60)
        print("BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("=" * 60)
        print("\n📋 Credenciales de prueba:\n")
        print("  👤 Admin:")
        print("     Username: admin")
        print("     Password: admin123")
        print("     Role:     ADMIN\n")
        print("  👨‍⚕️  Doctor:")
        print("     Username: doctor")
        print("     Password: doctor123")
        print("     Role:     DOCTOR\n")
        print("  👩‍💼  Secretaria:")
        print("     Username: secretaria")
        print("     Password: secretaria123")
        print("     Role:     SECRETARIA\n")
        print("=" * 60)
        print("\n💡 Siguiente paso: Ejecutar 'python run.py' para iniciar el servidor")
        print("   Luego visita: http://localhost:8000/docs\n")

    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
