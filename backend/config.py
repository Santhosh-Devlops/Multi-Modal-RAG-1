import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# ---------------------------------------------------------------------------
# Load environment variables from a .env file.
# NOTE: previously nothing in this codebase ever called load_dotenv() (and
# python-dotenv wasn't even a dependency), so every os.getenv() call below
# only ever saw real OS environment variables - a .env file sitting next to
# this config.py, however correctly filled in, was silently ignored. This is
# almost certainly why HUGGINGFACE_* settings appeared not to take effect
# locally. Both locations are supported so it works whether you keep your
# .env in backend/ (next to this file) or in the project root.
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(PROJECT_ROOT / ".env", override=False)
except ImportError:
    print(
        "WARNING: python-dotenv is not installed, so .env files are not being "
        "loaded automatically - run `pip install -r requirements.txt` (it is "
        "now included), or export the required environment variables manually."
    )

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
# ---------------------------------------------------------------------------
# NOTE: earlier revisions of this codebase read the token under three
# different names in three different files (HUGGINGFACE_API_KEY,
# HUGGINGFACE_API_TOKEN, HUGGINGFACE_TOKEN) which meant the key set in
# .env was never actually seen by the code that made the request. This is
# the single place the token is resolved now -- every service must import
# HUGGINGFACE_API_KEY (or HF_TOKEN, same value) from here.
HUGGINGFACE_API_KEY = (
    os.getenv("HF_TOKEN")
    or os.getenv("HUGGINGFACE_API_TOKEN")
    or os.getenv("HUGGINGFACE_TOKEN")
    or os.getenv("HUGGINGFACE_API_KEY")
    or ""
).strip()
HF_TOKEN = HUGGINGFACE_API_KEY  # alias, some modules import this name

# Chat/vision model used via the HF Router chat-completions API.
# IMPORTANT: HF's router only sends your request to a provider you have
# actually enabled at https://huggingface.co/settings/inference-providers -
# a model existing on the Hub does NOT mean your account can call it. If you
# see "not supported by any provider you have enabled", go enable a couple
# of providers there (Together, Novita, Fireworks, Hyperbolic, Nebius,
# Cerebras, SambaNova are all commonly available on the free tier) - no code
# change fixes that, it's an account setting.
#
# TEXT_GENERATION_MODEL default below is a plain text/instruct model
# confirmed reachable via the Together provider on a fresh HF account.
TEXT_GENERATION_MODEL = os.getenv("TEXT_GENERATION_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
HF_MODEL_FALLBACKS = [
    m.strip() for m in os.getenv(
        "HF_MODEL_FALLBACKS",
        "meta-llama/Llama-3.1-8B-Instruct,openai/gpt-oss-120b,Qwen/Qwen2.5-7B-Instruct"
    ).split(",") if m.strip()
]

# Vision-language model for image/figure captioning - kept as a SEPARATE
# chain from the text chain above. Sending image content to a text-only
# model always fails (400/405), so the two chains must never be mixed.
VISION_MODEL = os.getenv("VISION_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
HF_VISION_FALLBACKS = [
    m.strip() for m in os.getenv(
        "HF_VISION_FALLBACKS",
        "Qwen/Qwen2.5-VL-7B-Instruct,meta-llama/Llama-3.2-11B-Vision-Instruct"
    ).split(",") if m.strip()
]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# The free `hf-inference` provider only serves a curated, popularity-based
# list of models for feature-extraction, so a perfectly valid model id can
# still get "not supported by provider hf-inference". These are tried in
# order after EMBEDDING_MODEL if it isn't deployed there right now.
EMBEDDING_MODEL_FALLBACKS = [
    m.strip() for m in os.getenv(
        "EMBEDDING_MODEL_FALLBACKS",
        "BAAI/bge-base-en-v1.5,intfloat/e5-base-v2,sentence-transformers/all-mpnet-base-v2"
    ).split(",") if m.strip()
]
# If the `sentence-transformers` package is installed locally, embeddings are
# computed on-device instead of calling the HF API at all - no network
# dependency, no rate limits, no "not supported by provider" errors, and
# generally better retrieval quality. Entirely optional: pip install
# sentence-transformers (pulls in torch, ~1-2GB, so it's opt-in rather than
# a hard requirement - see requirements.txt comment).
USE_LOCAL_EMBEDDING_MODEL = os.getenv("USE_LOCAL_EMBEDDING_MODEL", "true").lower() == "true"
# IMAGE_MODEL is kept only for backward compatibility with older .env files/imports;
# real vision captioning now always uses VISION_MODEL / HF_VISION_FALLBACKS above.
IMAGE_MODEL = os.getenv("IMAGE_MODEL", VISION_MODEL)

# Fallback & Demo Mode Settings
ENABLE_LOCAL_FALLBACK = os.getenv("ENABLE_LOCAL_FALLBACK", "true").lower() == "true"
MOCK_EXTERNAL_APIS_IF_NO_KEY = os.getenv("MOCK_EXTERNAL_APIS_IF_NO_KEY", "true").lower() == "true"
HF_REQUEST_TIMEOUT = float(os.getenv("HF_REQUEST_TIMEOUT", "60"))

# Hybrid Retrieval Settings
HYBRID_SEMANTIC_WEIGHT = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", "0.7"))
HYBRID_KEYWORD_WEIGHT = float(os.getenv("HYBRID_KEYWORD_WEIGHT", "0.3"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# External Web Knowledge (crawling / "read more" / model suggestions)
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "4"))
WEB_SEARCH_TIMEOUT = float(os.getenv("WEB_SEARCH_TIMEOUT", "8"))

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
