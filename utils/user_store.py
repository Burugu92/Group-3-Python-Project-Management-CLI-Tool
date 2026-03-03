"""
User data storage utility module.

Provides centralized functions for loading and saving users from/to data/users.json.
This module ensures a single source of truth for user data across the application.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any


def get_users_file_path() -> Path:
    """
    Get the absolute path to data/users.json.
    
    Uses Path.resolve() to ensure the path works regardless of where the CLI is run from.
    
    Returns:
        Path object pointing to data/users.json
    """
    # Get the project root by finding the parent of the utils directory
    utils_dir = Path(__file__).resolve().parent
    project_root = utils_dir.parent
    users_file = project_root / "data" / "users.json"
    
    return users_file


def load_users() -> List[Dict[str, Any]]:
    """
    Load all users from data/users.json.
    
    Returns:
        List of user dictionaries. Empty list if file doesn't exist or is empty.
        
    Raises:
        json.JSONDecodeError: If file is invalid JSON
        IOError: If file cannot be read
    """
    users_file = get_users_file_path()
    
    if not users_file.exists():
        return []
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError) as e:
        # Log error but return empty list to prevent crashes
        print(f"Warning: Could not load users file: {e}")
        return []


def save_users(users: List[Dict[str, Any]]) -> bool:
    """
    Save users to data/users.json.
    
    Ensures the data directory exists before writing.
    
    Args:
        users: List of user dictionaries to save
        
    Returns:
        True if save was successful, False otherwise
        
    Raises:
        IOError: If file cannot be written
        json.JSONEncodeError: If users data cannot be serialized to JSON
    """
    users_file = get_users_file_path()
    
    # Ensure data directory exists
    users_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, json.JSONEncodeError) as e:
        print(f"Error: Could not save users file: {e}")
        return False


def add_user(new_user: Dict[str, Any]) -> bool:
    """
    Add a new user to data/users.json.
    
    Loads existing users, appends the new user, then saves back to file.
    
    Args:
        new_user: Dictionary containing the new user data
        
    Returns:
        True if user was added successfully, False otherwise
    """
    try:
        users = load_users()
        users.append(new_user)
        return save_users(users)
    except Exception as e:
        print(f"Error: Could not add user: {e}")
        return False


def user_exists(username: str) -> bool:
    """
    Check if a user with the given username already exists.
    
    Args:
        username: Username to check
        
    Returns:
        True if user exists, False otherwise
    """
    users = load_users()
    return any(user.get("username") == username for user in users)


def email_exists(email: str) -> bool:
    """
    Check if a user with the given email already exists.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is registered, False otherwise
    """
    users = load_users()
    return any(user.get("email") == email for user in users)


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Find a user by username.
    
    Args:
        username: Username to search for
        
    Returns:
        User dictionary if found, None otherwise
    """
    users = load_users()
    for user in users:
        if user.get("username") == username:
            return user
    return None


def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Find a user by ID.
    
    Args:
        user_id: User ID to search for
        
    Returns:
        User dictionary if found, None otherwise
    """
    users = load_users()
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


def remove_user(username: str) -> bool:
    """
    Remove a user by username from data/users.json.
    
    Args:
        username: Username to remove
        
    Returns:
        True if user was removed, False if user wasn't found or save failed
    """
    users = load_users()
    original_count = len(users)
    users = [u for u in users if u.get("username") != username]
    
    if len(users) == original_count:
        return False  # User not found
    
    return save_users(users)


def update_user(username: str, updated_data: Dict[str, Any]) -> bool:
    """
    Update a user's data in data/users.json.
    
    Args:
        username: Username of the user to update
        updated_data: Dictionary with fields to update
        
    Returns:
        True if user was updated, False if user wasn't found or save failed
    """
    users = load_users()
    user_found = False
    
    for user in users:
        if user.get("username") == username:
            user.update(updated_data)
            user_found = True
            break
    
    if not user_found:
        return False
    
    return save_users(users)


def get_next_user_id() -> int:
    """
    Get the next available user ID.
    
    Returns:
        Next ID (max existing ID + 1)
    """
    users = load_users()
    if not users:
        return 1
    
    max_id = max(user.get("id", 0) for user in users if isinstance(user.get("id"), int))
    return max_id + 1
