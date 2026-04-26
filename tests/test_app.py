"""
Tests for the Mergington High School API (src/app.py).

Uses pytest and TestClient to verify the FastAPI backend.
Uses Arrange-Act-Assert structure for each test.
"""

import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

_initial_activities_state = copy.deepcopy(activities)


def reset_activity_state():
    activities.clear()
    activities.update(copy.deepcopy(_initial_activities_state))


def setup_function():
    reset_activity_state()


def teardown_function():
    reset_activity_state()


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == expected_activity_names
    assert isinstance(data["Chess Club"]["participants"], list)


def test_successful_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_delete_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_non_participant_returns_400(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "not_registered@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
