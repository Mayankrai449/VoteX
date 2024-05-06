from fastapi.testclient import TestClient
from routes import auth_router
from fastapi import status

client = TestClient(auth_router)

def test_register_user():
    response = client.post("/user/register", json={
        "username": "testuser",
        "fullname": "Test User",
        "email": "user@gmail.com",
        "dob": "1990-01-01",
        "age": 30,
        "city": "Test City",
        "password": "testpassword",
        "disabled": False
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["location"] == "/login"

def test_successful_login():
    response = client.post("/user/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["location"] == "/dashboard"
    assert "flash_message" in response.cookies
    assert "flash_type" in response.cookies
    assert "access_token" in response.cookies

def test_failed_login():
    response = client.post("/user/login", data={
        "username": "invaliduser",
        "password": "invalidpassword"
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["location"] == "/"
    assert "flash_message" in response.cookies
    assert "flash_type" in response.cookies

def test_logout():
    response = client.get("/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["location"] == "/"
    assert "flash_message" in response.cookies
    assert "flash_type" in response.cookies
    assert response.cookies["access_token"] == ""

def test_expired_session_login():
    response = client.get("/", cookies={"message": "expired"})
    assert response.status_code == status.HTTP_200_OK
    assert "Your Session has Expired! Please Log In again." in response.text

def test_register_page():
    response = client.get("/register")
    assert response.status_code == status.HTTP_200_OK
    assert "Register" in response.text

def test_login_page():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Login" in response.text
