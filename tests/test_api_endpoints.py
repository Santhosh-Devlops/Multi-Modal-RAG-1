import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import app
from database import init_db

client = TestClient(app)

def setup_module():
    init_db()

def test_health_endpoint():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Healthy"
    assert len(data["components"]) >= 5

def test_documents_list_endpoint():
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["documents"], list)

def test_agents_list_endpoint():
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["agents"]) == 8

def test_benchmark_endpoint():
    response = client.get("/api/evaluation/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert len(data["benchmark_questions"]) >= 5

def test_auth_flow_endpoint():
    # Test Registration
    reg_response = client.post("/api/auth/register", json={
        "email": "test_operator@factory.com",
        "password": "securepassword123",
        "full_name": "Test Operator"
    })
    assert reg_response.status_code in [200, 400]

    # Test Login
    login_response = client.post("/api/auth/login", json={
        "email": "test_operator@factory.com",
        "password": "securepassword123"
    })
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["status"] == "success"
    assert "access_token" in data
