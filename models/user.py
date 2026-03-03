"""
User module for CLI Inventory Management System.

Handles user management, authentication, and JSON persistence.
Uses utils/user_store.py for centralized file I/O operations.
"""

from __future__ import annotations  # Enable modern type hints for Python 3.8
import hashlib  # For SHA-256 password hashing
from typing import Optional  # For optional type hints
from utils import user_store  # Import centralized user store utilities


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
    def load_users(cls, fn: str = None) -> list:
        """
        Load users from data/users.json using the user_store utility.
        
        Args:
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            List of User objects. Empty list if file doesn't exist.
        """
        data = user_store.load_users()  # Load users from data/users.json
        return [cls.from_dict(user_data) for user_data in data]  # Convert each dict to User object
    
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
    def save_users(cls, users: list, fn: str = None) -> None:
        """
        Save users to data/users.json using the user_store utility.
        
        Args:
            users: List of User objects to persist.
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Raises:
            IOError: If file cannot be written.
        """
        user_dicts = [u.to_dict() if isinstance(u, cls) else u for u in users]  # Convert User objects to dicts
        user_store.save_users(user_dicts)  # Save to data/users.json
    
    @classmethod
    def authenticate(
        cls,
        username: str,
        password: str,
        fn: str = None
    ) -> Optional["User"]:
        """
        Authenticate user by username and password.
        
        Args:
            username: Username to authenticate.
            password: Plain text password to verify.
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            User instance if authentication successful, None otherwise.
        """
        users = cls.load_users()  # Load all users from data/users.json
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
        fn: str = None
    ) -> Optional["User"]:
        """
        Create a new user (public method for self-registration).
        
        Validates username uniqueness, hashes password, and persists to data/users.json.
        
        Args:
            username: Unique username.
            password: Plain text password.
            role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            User instance if created successfully, None if validation fails.
            
        Raises:
            ValueError: If username already exists.
        """
        users = cls.load_users()  # Load existing users from data/users.json
        
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
        
        # Save to data/users.json
        users.append(new_user)  # Add new user to list
        cls.save_users(users)  # Persist to data/users.json via user_store
        
        return new_user  # Return created user
    
    def add_user(
        self,
        username: str,
        password: str,
        role: str = "staff",
        fn: str = None
    ) -> Optional["User"]:
        """
        Add a new user (admin-only method).
        
        Args:
            username: Unique username.
            password: Plain text password.
            role: User role ('admin', 'staff', or 'viewer'). Defaults to 'staff'.
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            User instance if created successfully, None if validation fails.
            
        Raises:
            PermissionError: If caller is not an admin.
            ValueError: If username already exists.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can add users.")  # Deny if not admin
        
        return User.create_user(username, password, role)  # Call public create_user if authorized
    
    def delete_user(
        self,
        username: str,
        fn: str = None
    ) -> bool:
        """
        Delete a user by username (admin-only method).
        
        Args:
            username: Username of user to delete.
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            True if user was deleted, False if user not found.
            
        Raises:
            PermissionError: If caller is not an admin or attempting self-delete.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can delete users.")  # Deny if not admin
        
        if username == self.username:  # Prevent self-deletion
            raise PermissionError("Cannot delete your own account.")  # Deny self-delete
        
        users = User.load_users()  # Load all users from data/users.json
        initial_count = len(users)  # Record initial count
        users = [u for u in users if u.username != username]  # Remove target user
        
        if len(users) < initial_count:  # Check if user was deleted
            User.save_users(users)  # Save updated user list to data/users.json
            return True  # Deletion successful
        
        return False  # User not found
    
    def list_users(self, fn: str = None) -> list[dict]:
        """
        List all users (admin-only method).
        
        Returns all users with username, role, and id information.
        
        Args:
            fn: Deprecated parameter, ignored. Uses data/users.json via user_store.
            
        Returns:
            List of user dictionaries containing id, username, and role.
            
        Raises:
            PermissionError: If caller is not an admin.
        """
        if not self.is_admin():  # Check admin permission
            raise PermissionError("Only admins can list users.")  # Deny if not admin
        
        users = User.load_users()  # Load all users from data/users.json
        return [  # Return summary of each user
            {
                "id": u.id,  # Include user ID
                "username": u.username,  # Include username
                "role": u.role  # Include role
            }
            for u in users  # For each loaded user
        ]
