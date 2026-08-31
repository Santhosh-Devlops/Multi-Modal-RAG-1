import os
import shutil
from pathlib import Path
import sys

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from database import init_db, SessionLocal
from models.document_model import Document
from models.user_model import User
from agents.document_agent import DocumentProcessingAgent
from agents.agent_orchestrator import AgentOrchestrator
from config import UPLOADS_DIR, DEMO_2FA_CODE
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SAMPLE_FILES = [
    {
        "filename": "industrial_cnc_machining_manual.pdf",
        "domain": "Manufacturing",
        "doc_type": "Equipment Operations & Maintenance Manual",
        "path": BASE_DIR / "manufacturing" / "industrial_cnc_machining_manual.pdf"
    },
    {
        "filename": "mri_medical_diagnostic_system_manual.pdf",
        "domain": "Healthcare",
        "doc_type": "Clinical Diagnostic System Specification",
        "path": BASE_DIR / "healthcare" / "mri_medical_diagnostic_system_manual.pdf"
    },
    {
        "filename": "annual_financial_performance_report.pdf",
        "domain": "Finance",
        "doc_type": "Annual Financial & CAPEX Statement",
        "path": BASE_DIR / "finance" / "annual_financial_performance_report.pdf"
    },
    {
        "filename": "applied_robotics_engineering_handbook.pdf",
        "domain": "Education",
        "doc_type": "Robotics Engineering Technical Textbook",
        "path": BASE_DIR / "education" / "applied_robotics_engineering_handbook.pdf"
    },
    {
        "filename": "aerospace_avionics_maintenance_spec.pdf",
        "domain": "Defence",
        "doc_type": "Aerospace Avionics Technical Specification",
        "path": BASE_DIR / "defence" / "aerospace_avionics_maintenance_spec.pdf"
    }
]

def seed():
    print("Seeding SQLite database & initializing vector index...")
    init_db()
    db = SessionLocal()
    
    # 1. Initialize default student demo user
    demo_user = db.query(User).filter(User.email == "student@university.edu").first()
    if not demo_user:
        hashed = pwd_context.hash("internship2026")
        demo_user = User(
            email="student@university.edu",
            hashed_password=hashed,
            full_name="Internship Candidate",
            role="student",
            is_verified_2fa=True,
            two_fa_secret=DEMO_2FA_CODE
        )
        db.add(demo_user)
        db.commit()
        print("Created demo user: student@university.edu / internship2026 (2FA Code: 123456)")

    # 2. Register 8 Agents
    AgentOrchestrator.initialize_agent_registry(db)
    print("Registered 8 multi-modal agents in database.")

    # 3. Ingest Sample Documents
    for s in SAMPLE_FILES:
        if not s["path"].exists():
            print(f"File not found: {s['path']}")
            continue
            
        existing = db.query(Document).filter(Document.filename == s["filename"]).first()
        if existing and existing.status == "Completed":
            print(f"Document '{s['filename']}' already indexed. Skipping.")
            continue
            
        # Copy to uploads
        target_upload = UPLOADS_DIR / s["filename"]
        shutil.copyfile(str(s["path"]), str(target_upload))
        file_size = os.path.getsize(target_upload)

        if not existing:
            doc = Document(
                filename=s["filename"],
                file_path=str(target_upload),
                file_type="pdf",
                file_size=file_size,
                domain=s["domain"],
                doc_type=s["doc_type"],
                status="Processing"
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
        else:
            doc = existing
            doc.status = "Processing"
            db.commit()

        trace_id = f"trace_seed_{doc.id}"
        print(f"Processing and indexing 15-page document: {s['filename']} ({s['domain']})...")
        res = DocumentProcessingAgent.process_document(db, doc.id, trace_id)
        print(f"Indexed {s['filename']}: {res}")

    db.close()
    print("Database seeding and vector index build complete!")

if __name__ == "__main__":
    seed()
