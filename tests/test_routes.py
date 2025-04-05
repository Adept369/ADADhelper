import json
import pytest
from app import create_app  # Ensure you have a create_app factory in __init__.py

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_llm_endpoint(client):
    response = client.post("/llm", json={"prompt": "Hello Caelum!"})
    assert response.status_code == 200
    assert "Caelum" in response.get_data(as_text=True)

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_respond_minimal(client):
    response = client.post("/respond", json={
        "input": "I feel foggy",
        "user_id": "test001"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert "archetype_used" in data

def test_archetype_create_and_list(client):
    payload = {
        "name": "TestArchetype",
        "traits": ["test", "calm"],
        "tags": ["debug", "sample"]
    }
    post_resp = client.post("/custom-archetype", json=payload)
    assert post_resp.status_code == 200

    list_resp = client.get("/custom-archetypes")
    assert list_resp.status_code == 200
    found = any(a['name'] == "TestArchetype" for a in list_resp.get_json())
    assert found

def test_version_history(client):
    resp = client.get("/version-history?name=TestArchetype")
    assert resp.status_code in [200, 404]  # May not exist if version was not saved
