import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.routers import investigation_pipeline


def test_investigation_pipeline_end_to_end_api_flow():
    investigation_pipeline._datasets.clear()
    investigation_pipeline._investigations.clear()

    app = FastAPI()
    app.include_router(investigation_pipeline.router)
    client = TestClient(app)

    csv_content = "value,group\n10,A\n12,B\n11,A\n9,B\n".encode("utf-8")

    upload_response = client.post(
        "/investigation-pipeline/datasets/upload",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert upload_response.status_code == 200
    dataset_id = upload_response.json()["dataset_id"]

    profile_response = client.post(f"/investigation-pipeline/datasets/{dataset_id}/semantic-profile")
    assert profile_response.status_code == 200
    assert profile_response.json()["columns"] == 2

    goals_response = client.get("/investigation-pipeline/business-goals")
    assert goals_response.status_code == 200
    goals = goals_response.json()
    assert goals
    goal_id = goals[0]["goal_id"]

    start_response = client.post(
        "/investigation-pipeline/investigations",
        json={"dataset_id": dataset_id, "goal_id": goal_id},
    )
    assert start_response.status_code == 200
    investigation_id = start_response.json()["investigation_id"]

    status_response = client.get(f"/investigation-pipeline/investigations/{investigation_id}/status")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["status"] in {"queued", "running", "completed"}

    findings_response = client.get(f"/investigation-pipeline/investigations/{investigation_id}/findings")
    assert findings_response.status_code in {200, 409}

    if findings_response.status_code == 200:
        payload = findings_response.json()
        assert payload["findings_collection"]["investigation_id"]