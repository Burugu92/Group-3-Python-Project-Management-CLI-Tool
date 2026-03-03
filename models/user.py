"""
User module for CLI Inventory Management System.

Handles user management, authentication, and JSON persistence.
"""

from __future__ import annotations  # Enable modern type hints for Python 3.8
import json  # For reading/writing JSON file
import hashlib  # For SHA-256 password hashing
import os  # For file system operations
from typing import Optional  # For optional type hints


# Configuration
USERS_FILE = os.path.join("data", "users.json") # Default filename for user storage


class User:
    """
    Represents a system user with authentication and role-based access.
    
    Attributes:
        id: Unique integer identifier for the user.
        username: Unique username for login.
        hashed_password: SHA-256 hashed password.
        role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
    """
    
    def __init__(
        self,
        id: int,
        username: str,
        hashed_password: str,
        role: str = "staff"
    ) -> None:
        """
        Initialize a User object.
        
        Args:
            id: Unique integer identifier.
            username: Unique username for login.
            hashed_password: Pre-hashed password.
            role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
        """
        self.id = id  # Store unique user identifier
        self.username = username  # Store login username
        self.hashed_password = hashed_password  # Store SHA-256 hashed password
        self.role = role  # Store user role (admin/staff/viewer)
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Hashed password as hexadecimal string.
        """
        return hashlib.sha256(password.encode()).hexdigest()  # Convert password to SHA-256 hex hash
    
    def verify_password(self, password: str) -> bool:
        """
        Verify if provided password matches the hashed password.
        
        Args:
            password: Plain text password to verify.
            
        Returns:
            True if password is correct, False otherwise.
        """
        return self.hashed_password == self._hash_password(password)  # Compare stored hash with input hash
    
    def is_admin(self) -> bool:
        """
        Check if user has admin role.
        
        Returns:
            True if user is admin, False otherwise.
        """
        return self.role == "admin"  # Check if role matches admin
    
    def is_authenticated(self) -> bool:
        """
        Check if user object represents authenticated user.
        
        Returns:
            True if user has valid credentials, False otherwise.
        """
        return self.id is not None and self.username is not None  # Check if user has required fields
    
    def to_dict(self) -> dict:
        """
        Convert user to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of user.
        """
        return {  # Convert user object to dictionary for JSON storage
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, user_dict: dict) -> "User":
        """
        Create a User instance from a dictionary.
        
        Args:
            user_dict: Dictionary containing user data.
            
        Returns:
            User instance.
        """
        return cls(  # Create User object from dictionary
            id=user_dict.get("id"),
            username=user_dict.get("username"),
            hashed_password=user_dict.get("hashed_password"),
            role=user_dict.get("role", "staff")  # Default role to 'staff' if not provided
        )
    
    @classmethod
    def load_users(cls, fn: str = USERS_FILE) -> list:
        """
        Load users from JSON file.
        
        Args:
            fn: Filename to load from. Defaults to USERS_FILE.
            
        Returns:
            List of User objects. Empty list if file doesn't exist.
        """
        if not os.path.exists(fn):  # Check if users file exists
            return []  # Return empty list if file not found
        
        try:
            with open(fn, 'r') as f:  # Open users file
                data = json.load(f)  # Parse JSON data
                return [cls.from_dict(user_data) for user_data in data]  # Convert each dict to User object
        except (json.JSONDecodeError, IOError):  # Handle file read/parse errors
            return []  # Return empty list on error
    
    @classmethod
    def get_user_by_username(cls, username):
      """
      Retrieve a user object by username.
      """
      users = cls.load_users()  # This should return a list of User objects
      for user in users:
        if user.username == username:
            return user
      return None
    @classmethod
    def save_users(cls, users: list, fn: str = USERS_FILE) -> None:
        """
        Save users to JSON file.
        
        Args:
            users: List of User objects to persist.
            fn: Filename to save to. Defaults to USERS_FILE.
            
        Raises:
            IOError: If file cannot be written.
        """
        user_dicts = [u.to_dict() if isinstance(u, cls) else u for u in users]  # Convert User objects to dicts
        with open(fn, 'w') as f:  # Open users file for writing
            json.dump(user_dicts, f, indent=2)  # Write formatted JSON to file
    
    @classmethod
    def authenticate(
        cls,
        username: str,
        password: str,
        fn: str = USERS_FILE
    ) -> Optional["User"]:
        """
        Authenticate user by username and password.
        
        Args:
            username: Username to authenticate.
            password: Plain text password to verify.
            fn: Filename to load users from. Defaults to USERS_FILE.
            
        Returns:
            User instance if authentication successful, None otherwise.
        """
        users = cls.load_users(fn)  # Load all users from file
        for user in users:  # Loop through each user
            if user.username == username and user.verify_password(password):  # Match username and password
                return user  # Return authenticated user
        return None  # Return None if no match found
    
    @classmethod
    def create_user(
        cls,
        username: str,
        password: str,
        role: str = "staff",
        fn: str = USERS_FILE
    ) -> Optional["User"]:
        """
        Create a new user (public method for self-registration).
        
        Validates username uniqueness, hashes password, and persists.
        
        Args:
            username: Unique username.
            password: Plain text password.
            role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
            fn: Filename to save to. Defaults to USERS_FILE.
            
        Returns:
            User instance if created successfully, None if validation fails.
            
        Raises:
            ValueError: If username already exists.
        """
        users = cls.load_users(fn)  # Load existing users
        
        # Validate username uniqueness
        for user in users:  # Check each user
            if user.username == username:  # Ensure username not taken
                raise ValueError(f"Username '{username}' already exists.")  # Raise error if duplicate
        
        # Create new user with next available id
        user_id = max([u.id for u in users], default=0) + 1  # Get highest ID and increment
        
        # Hash password
        temp_user = cls(id=user_id, username=username, hashed_password="")  # Temp object for hashing
        hashed_pw = temp_user._hash_password(password)  # Hash plain password
        
        new_user = cls(  # Create new User object
            id=user_id,
            username=username,
            hashed_password=hashed_pw,  # Use hashed password
            role=role  # Assign role
        )
        
        # Save to JSON
        users.append(new_user)  # Add new user to list
        cls.save_users(users, fn)  # Persist to file
        
        return new_user  # Return created user
    
    def add_user(
        self,
        username: str,
        password: str,
        role: str = "staff",
        fn: str = USERS_FILE
    ) -> Optional["User"]:
        """
        Add a new user (admin-only method).
        
        Args:
            username: Unique username.
            password: Plain text password.
            role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
            fn: Filename to save to. Defaults to USERS_FILE.
            
        Returns:
            User instance if created successfully, None if validation fails.
            
        Raises:
            PermissionError: If caller is not an admin.
            ValueError: If username already exists.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can add users.")  # Deny if not admin
        
        return User.create_user(username, password, role, fn)  # Call public create_user if authorized
    
    def delete_user(
        self,
        username: str,
        fn: str = USERS_FILE
    ) -> bool:
        """
        Delete a user by username (admin-only method).
        
        Args:
            username: Username of user to delete.
            fn: Filename to load/save users. Defaults to USERS_FILE.
            
        Returns:
            True if user was deleted, False if user not found.
            
        Raises:
            PermissionError: If caller is not an admin or attempting self-delete.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can delete users.")  # Deny if not admin
        
        if username == self.username:  # Prevent self-deletion
            raise PermissionError("Cannot delete your own account.")  # Deny self-delete
        
        users = User.load_users(fn)  # Load all users
        initial_count = len(users)  # Record initial count
        users = [u for u in users if u.username != username]  # Remove target user
        
        if len(users) < initial_count:  # Check if user was deleted
            User.save_users(users, fn)  # Save updated user list
            return True  # Deletion successful
        
        return False  # User not found
    
    def list_users(self, fn: str = USERS_FILE) -> list[dict]:
        """
        List all users (admin-only method).
        
        Returns all users with username, role, and id information.
        
        Args:
            fn: Filename to load users from. Defaults to USERS_FILE.
            
        Returns:
            List of user dictionaries containing id, username, and role.
            
        Raises:
            PermissionError: If caller is not an admin.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can list users.")  # Deny if not admin
        
        users = User.load_users(fn)  # Load all users
        return [  # Return summary of each user
            {
                "id": u.id,  # Include user ID
                "username": u.username,  # Include username
                "role": u.role  # Include role
            }
            for u in users  # For each loaded user
        ]
