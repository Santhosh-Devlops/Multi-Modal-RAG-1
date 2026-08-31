import os
import shutil
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from database import init_db, SessionLocal, engine, Base
from models import User, Document, DocumentPage, DocumentChunk, DocumentImage, DocumentTable, QueryRecord, QueryEvidence, AgentStatus, AgentActivityLog, EvaluationRun, EvaluationItem
from agents.agent_orchestrator import AgentOrchestrator
from config import DATA_DIR, UPLOADS_DIR, EXTRACTED_IMAGES_DIR, EXTRACTED_TABLES_DIR, VECTOR_INDEX_DIR

def reset():
    print("Resetting database and vector index for clean real-time operation...")
    
    # 1. Clear database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. Clear vector index files
    meta_file = VECTOR_INDEX_DIR / "vector_metadata.json"
    vec_file = VECTOR_INDEX_DIR / "vectors.npy"
    if meta_file.exists():
        os.remove(meta_file)
    if vec_file.exists():
        os.remove(vec_file)
        
    # 3. Clean extracted images and uploads runtime cache (keep directory structure)
    for folder in [EXTRACTED_IMAGES_DIR, EXTRACTED_TABLES_DIR, UPLOADS_DIR]:
        for file in folder.glob("*"):
            if file.is_file() and not file.name.startswith("."):
                try:
                    os.remove(file)
                except Exception:
                    pass

    # 4. Initialize agent registry
    db = SessionLocal()
    AgentOrchestrator.initialize_agent_registry(db)
    db.close()
    
    # Reload vector store singleton
    from services.vector_store import vector_store
    vector_store.clear()
    
    print("Clean state ready. Zero sample data. All user operations will be 100% real-time.")

if __name__ == "__main__":
    reset()
