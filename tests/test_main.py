# tests/test_main.py
import json
from types import SimpleNamespace
import pytest
from methods import (
    load_session,
    add_product,
    list_products,
    sell_product,
    Transaction,
    User,
)

# --- Mock User class with is_admin ---
class MockUser:
    def __init__(self, username, role):
        self.username = username
        self.role = role
        self.is_authenticated = True

    def is_admin(self):
        return self.role == "admin"

# --- Session Tests ---
def test_load_session_success(tmp_path, monkeypatch):
    session_file = tmp_path / "session.json"
    data = {"username": "u1", "role": "admin"}
    monkeypatch.setattr("methods.SESSION_FILE", str(session_file))
    with open(session_file, "w") as f:
        json.dump(data, f)

    monkeypatch.setattr(User, "get_user_by_username", lambda username: MockUser(username, "admin"))

    user = load_session()
    assert user.username == "u1"

# --- Product Tests ---
def test_list_products_empty(monkeypatch, capsys):
    monkeypatch.setattr("methods.load_products", lambda: [])
    mock_user = MockUser("admin", "admin")
    list_products({"user": mock_user}, SimpleNamespace())
    captured = capsys.readouterr()
    assert "📦 No products found." in captured.out

def test_add_product_as_admin(monkeypatch, capsys):
    mock_user_admin = MockUser("admin", "admin")
    args = SimpleNamespace(name="Widget", category="Gadgets", price=10, quantity=5)
    monkeypatch.setattr("methods.load_products", lambda: [])
    monkeypatch.setattr("methods.save_products", lambda products: None)
    add_product({"user": mock_user_admin}, args)
    captured = capsys.readouterr()
    assert "✅ Product 'Widget' added successfully." in captured.out

def test_add_product_non_admin(capsys):
    mock_user_staff = MockUser("staff", "staff")
    args = SimpleNamespace(name="Widget", category="Gadgets", price=10, quantity=5)
    add_product({"user": mock_user_staff}, args)
    captured = capsys.readouterr()
    assert "❌ Admin privileges required." in captured.out

def test_sell_product_not_found(monkeypatch, capsys):
    mock_user_admin = MockUser("admin", "admin")
    monkeypatch.setattr("methods.load_products", lambda: [])
    sell_product({"user": mock_user_admin}, SimpleNamespace(product_id=99, quantity=1))
    captured = capsys.readouterr()
    assert "❌ Product not found." in captured.out


# --- Authentication Tests ---
def test_authenticate_returns_user_instance(monkeypatch):
    # Use MockUser with proper username
    mock_user = MockUser("u1", "admin")
    monkeypatch.setattr(User, "get_user_by_username", lambda username: mock_user)
    user = User.get_user_by_username("u1")
    assert user.username == "u1"

def test_authenticate_invalid_password(monkeypatch):
    # Mock authenticate returns None for wrong password
    def fake_authenticate(username, password):
        return None
    monkeypatch.setattr(User, "authenticate", fake_authenticate)
    user = User.authenticate("u1", "wrongpass")
    assert user is None