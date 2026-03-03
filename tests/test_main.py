import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import json
import os
import main


# Helper

def run_cli(args):
    with patch.object(sys, "argv", args):
        main.main()


class MockUser:
    def __init__(self, username="admin", role="admin"):
        self.username = username
        self.role = role

    def is_admin(self):
        return self.role == "admin"

    def list_users(self):
        return [{"id": 1, "username": "admin", "role": "admin"}]


# SESSION TESTS

@patch("main.os.makedirs")
@patch("main.open", new_callable=mock_open)
def test_save_session(mock_file, mock_makedirs):
    user = MockUser()
    main.save_session(user)

    mock_makedirs.assert_called_once()
    mock_file.assert_called_once_with(main.SESSION_FILE, "w")


@patch("main.os.path.exists", return_value=False)
def test_load_session_no_file(mock_exists):
    assert main.load_session() is None


@patch("main.os.path.exists", return_value=True)
@patch("main.open", new_callable=mock_open, read_data='{"username": "admin"}')
@patch("main.User.get_user_by_username")
def test_load_session_success(mock_get_user, mock_file, mock_exists):
    mock_get_user.return_value = MockUser()
    user = main.load_session()
    assert user.username == "admin"


@patch("main.os.path.exists", return_value=True)
@patch("main.os.remove")
def test_clear_session(mock_remove, mock_exists):
    main.clear_session()
    mock_remove.assert_called_once()


# DECORATOR TESTS

def test_login_required_blocks_access(capsys):
    @main.login_required
    def protected(ctx, args):
        print("SHOULD NOT RUN")

    protected({}, None)
    captured = capsys.readouterr()
    assert "must login" in captured.out


def test_admin_required_blocks_access(capsys):
    @main.admin_required
    def protected(ctx, args):
        print("SHOULD NOT RUN")

    protected({"user": MockUser(role="staff")}, None)
    captured = capsys.readouterr()
    assert "Admin privileges required" in captured.out


# REGISTER / LOGIN FAILURES

@patch("main.User.create_user", side_effect=ValueError("User exists"))
@patch("main.getpass", return_value="pass")
def test_register_failure(mock_getpass, mock_create, capsys):
    run_cli(["main.py", "register", "admin"])
    captured = capsys.readouterr()
    assert "User exists" in captured.out


@patch("main.User.authenticate", return_value=None)
@patch("main.getpass", return_value="wrong")
def test_login_failure(mock_getpass, mock_auth, capsys):
    run_cli(["main.py", "login", "admin"])
    captured = capsys.readouterr()
    assert "Invalid credentials" in captured.out


# PRODUCT EDGE CASES

@patch("main.load_session", return_value=MockUser())
@patch("main.load_products", return_value=[])
def test_sell_product_not_found(mock_load, mock_session, capsys):
    run_cli(["main.py", "sell-product", "1", "2"])
    captured = capsys.readouterr()
    assert "Product not found" in captured.out


@patch("main.load_session", return_value=MockUser())
def test_sell_product_value_error(mock_session, capsys):
    mock_product = MagicMock()
    mock_product.product_id = 1
    mock_product.decrease_stock.side_effect = ValueError("Insufficient stock")

    with patch("main.load_products", return_value=[mock_product]):
        run_cli(["main.py", "sell-product", "1", "5"])

    captured = capsys.readouterr()
    assert "Insufficient stock" in captured.out


@patch("main.load_session", return_value=MockUser(role="staff"))
def test_restock_non_admin(mock_session, capsys):
    run_cli(["main.py", "restock-product", "1", "5"])
    captured = capsys.readouterr()
    assert "Only admins can restock products" in captured.out


# LIST USERS EDGE CASE

@patch("main.load_session", return_value=MockUser(role="staff"))
def test_list_users_denied(mock_session, capsys):
    run_cli(["main.py", "list-users"])
    captured = capsys.readouterr()
    assert "Admin privileges required" in captured.out


# JSON HELPER COVERAGE

@patch("utils.storage_handler.load_from_file", return_value=[{"product_id": 1}])
@patch("main.Product.from_dict")
def test_load_products(mock_from_dict, mock_load):
    main.load_products("dummy.json")
    mock_from_dict.assert_called_once()


@patch("utils.storage_handler.save_to_file")
def test_save_products(mock_save):
    mock_product = MagicMock()
    mock_product.to_dict.return_value = {"id": 1}
    main.save_products("dummy.json", [mock_product])
    mock_save.assert_called_once()


# ARGPARSE HELP BRANCH

def test_no_command_prints_help(capsys):
    with patch.object(sys, "argv", ["main.py"]):
        main.main()
    captured = capsys.readouterr()
    assert "CLI Inventory Management System" in captured.out