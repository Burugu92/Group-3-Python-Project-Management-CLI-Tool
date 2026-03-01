"""
Test script for user.py - CLI Inventory System
"""

from user import User

# Load admins
users = User.load_users()
print("✓ Loaded users:", [u.username for u in users])
print(f"  Total users: {len(users)}\n")

# Login as Denis (admin)
dennis = User.authenticate("Denis kipruto", "@2026")
print(f"✓ Denis authenticated: {dennis is not None}")
if dennis:
    print(f"  Username: {dennis.username}")
    print(f"  Email: {dennis.email}")
    print(f"  Is admin: {dennis.is_admin()}")
    print(f"  Is authenticated: {dennis.is_authenticated()}\n")

# List all users (admin only)
if dennis and dennis.is_admin():
    print("✓ All users (admin listing):")
    user_list = dennis.list_users()
    for user in user_list:
        print(f"  ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
    print()

# Self-register staff user
try:
    new_user = User.create_user("test_staff", "test.staff@company.com", "testpass123", role="staff")
    print(f"✓ New staff user created: {new_user.username}")
    print(f"  ID: {new_user.id}, Email: {new_user.email}, Role: {new_user.role}\n")
except ValueError as e:
    print(f"✗ Error creating user: {e}\n")

# List users again
if dennis and dennis.is_admin():
    print("✓ All users after registration:")
    user_list = dennis.list_users()
    for user in user_list:
        print(f"  ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
    print()

# Admin delete user
try:
    deleted = dennis.delete_user("test_staff")
    print(f"✓ Delete test_staff: {deleted}\n")
except PermissionError as e:
    print(f"✗ Permission error: {e}\n")

# Test permission errors
try:
    test_user = User.authenticate("test_staff", "testpass123")
    if test_user:
        test_user.list_users()
except PermissionError as e:
    print(f"✓ Permission denied (expected): {e}\n")

# Test failed authentication
failed_auth = User.authenticate("Denis kipruto", "wrongpassword")
print(f"✓ Failed authentication (wrong password): {failed_auth is None}\n")

# Test duplicate username
try:
    User.create_user("Edwin Burugu", "edwin.duplicate@company.com", "newpass", role="staff")
except ValueError as e:
    print(f"✓ Duplicate username error (expected): {e}\n")

# Test duplicate email
try:
    User.create_user("unique_user", "edwin.ceo@company.com", "newpass", role="staff")
except ValueError as e:
    print(f"✓ Duplicate email error (expected): {e}\n")

# Test invalid email
try:
    User.create_user("another_user", "invalid-email", "newpass", role="staff")
except ValueError as e:
    print(f"✓ Invalid email format error (expected): {e}\n")

print("=" * 50)
print("Test suite completed successfully!")

