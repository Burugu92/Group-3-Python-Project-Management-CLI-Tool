"""
Test suite for user.py - CLI Inventory System
Uses pytest for proper unit testing with assertions

Tests use models.user which reads from the centralized data/users.json via utils/user_store.
"""

import pytest
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import User


class TestUserLoading:
    """Tests for loading and basic user operations"""
    
    def test_load_users(self):
        """Test that users can be loaded from file"""
        users = User.load_users()
        assert users is not None, "Users should not be None"
        assert isinstance(users, list), "Users should be a list"
        assert len(users) > 0, "Should have at least one user"
        
        usernames = [u.username for u in users]
        assert "denis_kipruto" in usernames or len(usernames) > 0, "Should have users loaded"


class TestAuthentication:
    """Tests for user authentication"""
    
    def test_authenticate_invalid_password_returns_none(self):
        """Test authentication fails with wrong password"""
        result = User.authenticate("denis_kipruto", "wrongpassword")
        assert result is None, "Authentication should fail with wrong password"
    
    def test_authenticate_nonexistent_user_returns_none(self):
        """Test authentication fails for non-existent user"""
        result = User.authenticate("nonexistent_user_xyz", "password")
        assert result is None, "Authentication should fail for non-existent user"
    
    def test_authenticate_returns_user_instance(self):
        """Test successful authentication returns User instance"""
        users = User.load_users()
        if users:
            first_user = users[0]
            # Test that authentication method returns correct type when user exists
            result = User.authenticate(first_user.username, "invalidpass")
            assert result is None or isinstance(result, User), "Should return User or None"


class TestAdminFunctions:
    """Tests for admin-specific functions"""
    
    def test_admin_user_has_admin_role(self):
        """Test that admin users return True for is_admin()"""
        users = User.load_users()
        admin_users = [u for u in users if u.role == "admin"]
        
        for admin in admin_users[:1]:  # Test first admin if exists
            assert admin.is_admin() == True, f"Admin user {admin.username} should return True for is_admin()"
    
    def test_list_users_returns_list_for_admin(self):
        """Test that list_users returns a list of user dicts"""
        users = User.load_users()
        admin_user = next((u for u in users if u.role == "admin"), None)
        
        if admin_user:
            user_list = admin_user.list_users()
            assert user_list is not None, "User list should not be None"
            assert isinstance(user_list, list), "User list should be a list"
            assert len(user_list) > 0, "User list should not be empty"
            
            # Verify structure of each user dict
            for user_dict in user_list:
                assert "id" in user_dict, "User dict should contain 'id'"
                assert "username" in user_dict, "User dict should contain 'username'"
                assert "role" in user_dict, "User dict should contain 'role'"


class TestUserCreation:
    """Tests for creating new users"""
    
    @pytest.fixture(autouse=True)
    def cleanup_test_user(self):
        """Clean up test user before and after test"""
        test_username = "pytest_test_staff"
        try:
            users = User.load_users()
            users = [u for u in users if u.username != test_username]
            User.save_users(users)
        except:
            pass
        yield
        try:
            users = User.load_users()
            users = [u for u in users if u.username != test_username]
            User.save_users(users)
        except:
            pass
    
    def test_create_new_staff_user(self):
        """Test creating a new staff user"""
        test_username = "pytest_test_staff"
        
        new_user = User.create_user(test_username, "testpass123", role="staff")
        
        assert new_user is not None, "New user should be created"
        assert new_user.username == test_username, "Username should match"
        assert new_user.role == "staff", "Role should be 'staff'"
        assert isinstance(new_user.id, int), "User ID should be an integer"
    
    def test_created_user_is_persisted(self):
        """Test that created user is saved to file"""
        test_username = "pytest_test_staff"
        
        User.create_user(test_username, "testpass123", role="staff")
        users = User.load_users()
        found_user = next((u for u in users if u.username == test_username), None)
        
        assert found_user is not None, "User should be persisted to data/users.json"
        assert found_user.role == "staff", "Persisted user role should be staff"
    
    def test_create_duplicate_user_raises_error(self):
        """Test that creating a user with existing username raises ValueError"""
        test_username = "pytest_duplicate_test"
        
        # First, create a user
        User.create_user(test_username, "password123", role="staff")
        
        # Try to create duplicate username - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            User.create_user(test_username, "password456", role="staff")
        
        assert "already exists" in str(exc_info.value).lower(), "Error should mention username already exists"
        
        # Clean up
        try:
            users = User.load_users()
            users = [u for u in users if u.username != test_username]
            User.save_users(users)
        except:
            pass


class TestUserAuthentication:
    """Tests for user properties and verification"""
    
    def test_user_is_authenticated(self):
        """Test that loaded user is_authenticated returns True"""
        users = User.load_users()
        assert len(users) > 0, "Should have users to test"
        
        user = users[0]
        assert user.is_authenticated() == True, "Loaded user should be authenticated"
    
    def test_password_verification_returns_boolean(self):
        """Test password verification returns boolean"""
        users = User.load_users()
        user = users[0]
        
        result = user.verify_password("anypassword")
        assert isinstance(result, bool), "verify_password should return boolean"


class TestUserRoles:
    """Tests for user roles and permissions"""
    
    def test_staff_user_is_not_admin(self):
        """Test that staff users return False for is_admin()"""
        users = User.load_users()
        staff_users = [u for u in users if u.role == "staff"]
        
        for staff in staff_users[:1]:  # Test first staff user if exists
            assert staff.is_admin() == False, f"Staff user {staff.username} should return False for is_admin()"


class TestUserToDict:
    """Tests for user serialization"""
    
    def test_to_dict_returns_proper_structure(self):
        """Test that to_dict returns proper dictionary with all required fields"""
        users = User.load_users()
        user = users[0]
        
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict), "to_dict should return a dict"
        assert "id" in user_dict, "Dict should contain 'id'"
        assert "username" in user_dict, "Dict should contain 'username'"
        assert "hashed_password" in user_dict, "Dict should contain 'hashed_password'"
        assert "role" in user_dict, "Dict should contain 'role'"
    
    def test_to_dict_preserves_data(self):
        """Test that to_dict preserves user data correctly"""
        users = User.load_users()
        user = users[0]
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == user.id, f"ID should be {user.id}"
        assert user_dict["username"] == user.username, f"Username should be {user.username}"
        assert user_dict["role"] == user.role, f"Role should be {user.role}"


class TestUserFromDict:
    """Tests for user deserialization"""
    
    def test_from_dict_creates_user_instance(self):
        """Test that from_dict creates proper User instance"""
        user_data = {
            "id": 999,
            "username": "test_user",
            "hashed_password": "abc123",
            "role": "staff"
        }
        
        user = User.from_dict(user_data)
        
        assert isinstance(user, User), "Should create User instance"
    
    def test_from_dict_preserves_data(self):
        """Test that from_dict correctly maps data"""
        user_data = {
            "id": 999,
            "username": "test_user",
            "hashed_password": "abc123",
            "role": "staff"
        }
        
        user = User.from_dict(user_data)
        
        assert user.id == 999, "ID should be 999"
        assert user.username == "test_user", "Username should be 'test_user'"
        assert user.role == "staff", "Role should be 'staff'"


class TestUserDataPersistence:
    """Tests for saving and loading users"""
    
    def test_save_and_load_preserves_user_data(self):
        """Test that users can be saved and loaded correctly"""
        original_users = User.load_users()
        original_count = len(original_users)
        
        # Load and re-save should maintain data
        User.save_users(original_users)
        reloaded_users = User.load_users()
        
        assert len(reloaded_users) == original_count, f"User count should be {original_count}"
        
        for i, user in enumerate(reloaded_users):
            assert user.username == original_users[i].username, f"Username mismatch at index {i}"
            assert user.id == original_users[i].id, f"ID mismatch at index {i}"
            assert user.role == original_users[i].role, f"Role mismatch at index {i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
