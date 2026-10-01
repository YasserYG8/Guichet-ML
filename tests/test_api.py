from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_health_mode_mock():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["mode"] == "mock"
def test_detection_francais():
    r = client.post("/detect-language",
    json={"text": "Je ne peux plus acceder a mon compte."})
    assert r.status_code == 200
    assert r.json()["language"] == "fr"
    
def test_detection_arabe():
    r = client.post("/detect-language",
    json={"text": "حسابي إلى الدخول أستطيع ال"})
    assert r.json()["language"] == "ar"
    
def test_texte_trop_court_rejete():
 assert client.post("/detect-language", json={"text": "ab"}).status_code == 422