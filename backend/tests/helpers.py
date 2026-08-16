# backend/tests/helpers.py
def signup_and_login(client, email="test@example.com", org_name="Test Org"):
    client.post("/api/auth/signup", json={
        "email": email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "organization_name": org_name,
    })
    response = client.post("/api/auth/login", json={
        "email": email,
        "password": "testpassword123",
    })
    return response