from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

# SQLite connect_args for multithreaded FastAPI access
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import (
        user_model,
        document_model,
        query_model,
        agent_model,
        evaluation_model
    )
    Base.metadata.create_all(bind=engine)
    
    # Ensure migration columns exist
    with engine.connect() as conn:
        for col_sql in [
            "ALTER TABLE documents ADD COLUMN user_id INTEGER",
            "ALTER TABLE documents ADD COLUMN graph_count INTEGER DEFAULT 0",
            "ALTER TABLE documents ADD COLUMN numerical_count INTEGER DEFAULT 0",
            "ALTER TABLE document_pages ADD COLUMN graph_count INTEGER DEFAULT 0",
            "ALTER TABLE document_pages ADD COLUMN numerical_count INTEGER DEFAULT 0",
            "ALTER TABLE document_images ADD COLUMN ocr_text TEXT DEFAULT ''",
            "ALTER TABLE document_tables ADD COLUMN title VARCHAR(255) DEFAULT 'Extracted Table'",
            "ALTER TABLE query_records ADD COLUMN session_id VARCHAR(100) DEFAULT 'default_session'",
            "ALTER TABLE query_records ADD COLUMN external_suggestions TEXT"
        ]:
            try:
                conn.execute(text(col_sql))
                conn.commit()
            except Exception:
                pass
