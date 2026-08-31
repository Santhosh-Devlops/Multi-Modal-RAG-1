import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config import EXTRACTED_IMAGES_DIR, UPLOADS_DIR
from database import init_db, SessionLocal
from agents.agent_orchestrator import AgentOrchestrator

from routes.auth_routes import router as auth_router
from routes.document_routes import router as document_router
from routes.query_routes import router as query_router
from routes.agent_routes import router as agent_router
from routes.evaluation_routes import router as evaluation_router
from routes.system_routes import router as system_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    # Initialize 8 agents in DB
    db = SessionLocal()
    try:
        AgentOrchestrator.initialize_agent_registry(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Universal Multimodal RAG Multi-Agent Document Intelligence API",
    description="Full-stack AI assistant for multimodal documents (text, images, tables) across Manufacturing, Healthcare, Finance, and other domains.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file endpoints for extracted images and uploaded documents
app.mount("/api/static/images", StaticFiles(directory=str(EXTRACTED_IMAGES_DIR)), name="images")
app.mount("/api/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Register API Routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(query_router)
app.include_router(agent_router)
app.include_router(evaluation_router)
app.include_router(system_router)

@app.get("/")
def root_status():
    return {
        "status": "Online",
        "service": "Universal Multimodal RAG Multi-Agent Document Intelligence Assistant",
        "documentation": "/docs",
        "health_check": "/api/system/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
