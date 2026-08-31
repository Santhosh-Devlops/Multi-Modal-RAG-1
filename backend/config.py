import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Storage directories
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
EXTRACTED_IMAGES_DIR = BASE_DIR / "extracted_images"
EXTRACTED_TABLES_DIR = BASE_DIR / "extracted_tables"
VECTOR_INDEX_DIR = BASE_DIR / "vector_index"

# Create directories if they do not exist
for directory in [DATA_DIR, UPLOADS_DIR, EXTRACTED_IMAGES_DIR, EXTRACTED_TABLES_DIR, VECTOR_INDEX_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/multimodal_rag.db")

# Security & Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "university-internship-multimodal-rag-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
DEMO_2FA_CODE = os.getenv("DEMO_2FA_CODE", "123456")

# Hugging Face & AI Model Settings
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
TEXT_GENERATION_MODEL = os.getenv("TEXT_GENERATION_MODEL", "Qwen/Qwen2.5-7B-Instruct")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "Salesforce/blip-image-captioning-large")

# Fallback & Demo Mode Settings
ENABLE_LOCAL_FALLBACK = os.getenv("ENABLE_LOCAL_FALLBACK", "true").lower() == "true"
MOCK_EXTERNAL_APIS_IF_NO_KEY = os.getenv("MOCK_EXTERNAL_APIS_IF_NO_KEY", "true").lower() == "true"

# Hybrid Retrieval Settings
HYBRID_SEMANTIC_WEIGHT = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", "0.7"))
HYBRID_KEYWORD_WEIGHT = float(os.getenv("HYBRID_KEYWORD_WEIGHT", "0.3"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# Multi-Domain Configurations
SUPPORTED_DOMAINS = [
    "Manufacturing",
    "Healthcare",
    "Finance",
    "Education",
    "Defence",
    "Engineering",
    "Research",
    "Business",
    "Social Media",
    "General"
]
