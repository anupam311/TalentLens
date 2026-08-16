# backend/tests/test_jobs.py
from tests.helpers import signup_and_login


def test_create_and_list_job(client):
    signup_and_login(client)

    response = client.post("/api/jobs", json={"title": "Senior Backend Engineer"})
    assert response.status_code == 201
    assert response.json["title"] == "Senior Backend Engineer"
    assert response.json["status"] == "draft"

    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert len(response.json["jobs"]) == 1


def test_cannot_create_job_without_auth(client):
    response = client.post("/api/jobs", json={"title": "Should Not Work"})
    assert response.status_code == 401


def test_user_cannot_see_another_orgs_job(client):
    # Org A creates a job
    signup_and_login(client, email="usera@orga.com", org_name="Org A")
    response = client.post("/api/jobs", json={"title": "Org A's Secret Job"})
    job_id = response.json["id"]

    # Org B logs in (separate signup, separate org)
    signup_and_login(client, email="userb@orgb.com", org_name="Org B")

    # Org B tries to fetch Org A's job by ID directly
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 404  # not 403 — remember our earlier reasoning on this

    # Org B's own job list should be empty, not contain Org A's job
    response = client.get("/api/jobs")
    assert len(response.json["jobs"]) == 0