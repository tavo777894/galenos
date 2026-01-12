import sys
from datetime import date, datetime
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import app  # noqa: F401
except Exception as exc:
    print(f"import app: FAIL ({exc})")
    sys.exit(1)

from app.services.pdf_service import PDFService
from app.models.patient import Patient
from app.models.user import User, UserRole

out_dir = Path(r"D:\galenos\out")
out_dir.mkdir(parents=True, exist_ok=True)

now = datetime.utcnow()

patient = Patient(
    first_name="Test",
    last_name="Patient",
    ci="CI-TEST-001",
    date_of_birth=date(1990, 1, 1),
    phone="555-0100",
    email="test.patient@example.com",
    address="123 Test St",
    created_at=now,
    updated_at=now,
)

user = User(
    id=1,
    email="doctor@example.com",
    username="doctor",
    full_name="Test Doctor",
    hashed_password="not_used",
    role=UserRole.DOCTOR,
    is_active=True,
)

service = PDFService()
try:
    pdf_bytes, _ = service.generate_patient_card(db=None, patient=patient, user=user, save_to_db=False)
except Exception as exc:
    print(f"patient card pdf: FAIL ({exc})")
    sys.exit(1)

out_path = out_dir / "patient_card_test.pdf"
out_path.write_bytes(pdf_bytes)

if not pdf_bytes.startswith(b"%PDF"):
    print("PDF header validation failed.")
    sys.exit(1)

print(f"PDF size: {len(pdf_bytes)} bytes")
print(f"PDF head: {pdf_bytes[:16]}")
print("test_patient_card_pdf: SUCCESS")
