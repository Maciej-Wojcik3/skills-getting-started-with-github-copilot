"""
Integration tests for Mergington High School Activities API.
Tests use the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_all_activities_success(self, client, reset_activities):
        """
        Arrange: Fresh activities fixture
        Act: GET /activities
        Assert: 200 status and activities returned
        """
        # Arrange
        # (activities fixture provides known state)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) > 0
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data
    
    def test_get_activities_contains_expected_fields(self, client, reset_activities):
        """
        Arrange: Known activities
        Act: GET /activities
        Assert: Each activity has required fields
        """
        # Arrange
        # (activities fixture provides known state)
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
            assert activity_details["max_participants"] > 0


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """
        Arrange: Fresh app, existing activity, new email
        Act: POST /activities/Chess%20Club/signup?email=newstudent@mergington.edu
        Assert: 200 status, success message, participant added
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert new_email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """
        Arrange: Fresh app, activity with participant (michael@mergington.edu)
        Act: POST /activities/Chess%20Club/signup?email=michael@mergington.edu
        Assert: 400 status, error indicates already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Fresh app
        Act: POST /activities/NonExistent%20Club/signup?email=student@mergington.edu
        Assert: 404 status, error indicates activity not found
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_participant_count_updates(self, client, reset_activities):
        """
        Arrange: Get initial participant count for Chess Club
        Act: Sign up new participant
        Assert: Participant list includes new email
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent2@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert signup_response.status_code == 200
        
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        assert len(updated_participants) == initial_count + 1
        assert new_email in updated_participants


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participant/{email} endpoint."""
    
    def test_remove_participant_success(self, client, reset_activities):
        """
        Arrange: Fresh app with Chess Club having michael@mergington.edu
        Act: DELETE /activities/Chess%20Club/participant/michael@mergington.edu
        Assert: 200 status, success message, participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]
    
    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        """
        Arrange: Fresh app, Chess Club without nonexistent@mergington.edu
        Act: DELETE /activities/Chess%20Club/participant/nonexistent@mergington.edu
        Assert: 404 status, error indicates participant not found
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Fresh app
        Act: DELETE /activities/NonExistent%20Club/participant/student@mergington.edu
        Assert: 404 status, error indicates activity not found
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_remove_participant_count_updates(self, client, reset_activities):
        """
        Arrange: Get initial participant count for Chess Club
        Act: Remove a participant
        Assert: Participant count decreases by 1, email removed from list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act
        delete_response = client.delete(
            f"/activities/{activity_name}/participant/{email_to_remove}"
        )
        
        # Assert
        assert delete_response.status_code == 200
        
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        assert len(updated_participants) == initial_count - 1
        assert email_to_remove not in updated_participants
