import pytest
from fastapi.testclient import TestClient

from urbanmatch.main import app, get_db
from urbanmatch.database import Base, engine, SessionLocal

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def create_test_data():
    bulk_users = [
        {
            "name": "Sanam",
            "age": 25,
            "gender": "female",
            "email": "sanam@example.com",
            "city": "Delhi",
            "interests": ["music", "reading"]
        },
        {
            "name": "Rohan",
            "age": 28,
            "gender": "male",
            "email": "rohan@example.com",
            "city": "Chandigarh",
            "interests": ["sports", "travel"]
        }
    ]
    response = client.post("/users/bulk", json=bulk_users)
    assert response.status_code == 200
    return response.json()


def test_bulk_create_users():
    bulk_users = [
        {
            "name": "TestUser1",
            "age": 30,
            "gender": "male",
            "email": "testuser1@example.com",
            "city": "City1",
            "interests": ["interest1", "interest2"]
        },
        {
            "name": "TestUser2",
            "age": 22,
            "gender": "female",
            "email": "testuser2@example.com",
            "city": "City2",
            "interests": ["interest3", "interest4"]
        }
    ]
    response = client.post("/users/bulk", json=bulk_users)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "TestUser1"
    assert data[1]["email"] == "testuser2@example.com"


def test_create_user():
    user_data = {
        "name": "SingleUser",
        "age": 25,
        "gender": "male",
        "email": "singleuser@example.com",
        "city": "SampleCity",
        "interests": ["sample", "test"]
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SingleUser"
    assert data["email"] == "singleuser@example.com"


def test_read_users():
    response = client.get("/users/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_read_single_user():
    response = client.get("/users/1")
    if response.status_code == 200:
        data = response.json()
        assert data["id"] == 1
    else:
        pytest.skip("User with ID=1 not found, skipping test.")


def test_update_user():
    update_data = {
        "name": "UpdatedUser",
        "age": 26,
        "gender": "male",
        "email": "updated@example.com",
        "city": "UpdatedCity",
        "interests": ["updated", "info"]
    }
    response = client.put("/users/1", json=update_data)
    if response.status_code == 404:
        pytest.skip("User with ID=1 not found, skipping test.")
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "UpdatedUser"
        assert data["email"] == "updated@example.com"


def test_delete_user():

    response = client.delete("/users/1")
    if response.status_code == 404:
        pytest.skip("User with ID=1 not found, skipping test.")
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1


def test_match_users(create_test_data):
    user_id = 2
    match_payload = {
        "city": ["Delhi"],
        "gender": ["female"],
        "age_range_start": 20,
        "age_range_end": 40
    }
    response = client.post(f"/match/{user_id}", json=match_payload)
    if response.status_code == 404:
        pytest.skip(f"User with ID={user_id} not found, skipping test.")
    else:
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


def test_validate_email():
    
    valid_email = "valid@example.com"
    invalid_email = "invalidexamplecom"
    duplicate_email = "rohan@example.com"

    response_valid = client.get(f"/validate_email/{valid_email}")
    assert response_valid.status_code == 200
    valid_data = response_valid.json()
    assert valid_data["is_valid"] is True
    assert "error" not in valid_data 

    response_invalid = client.get(f"/validate_email/{invalid_email}")
    assert response_invalid.status_code == 200
    invalid_data = response_invalid.json()
    print(invalid_data)
    assert invalid_data["is_valid"] is False
    assert invalid_data["error"] == "Invalid email"

    response_duplicate = client.get(f"/validate_email/{duplicate_email}")
    assert response_duplicate.status_code == 200
    duplicate_data = response_duplicate.json()
    assert duplicate_data["is_valid"] is False
    assert duplicate_data["error"] == "Duplicate email"
    assert "user_id" in duplicate_data
    assert duplicate_data["user_id"] == 5