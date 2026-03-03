import os
import sys
import json
import pytest

# ensure the project root is on sys.path so imports from models/ work
sys.path.insert(0, os.getcwd())

from models.transactions import Transaction


@pytest.fixture(autouse=True)
def isolate_transactions(tmp_path, monkeypatch):
    """Ensure each test runs with a clean, temporary transactions file."""
    temp_file = tmp_path / "transactions.json"
    # point the class at the temporary path
    monkeypatch.setattr(Transaction, "transactions_data", str(temp_file))
    # reset class state
    Transaction.transactions = []
    Transaction.id_counter = 0
    # make sure the file does not exist yet
    if temp_file.exists():
        temp_file.unlink()
    yield
    # cleanup not strictly necessary (tmp_path is ephemeral)


def test_transaction_to_dict_and_str():
    """`to_dict` should return a complete dictionary and `__str__` should include key fields."""
    t = Transaction("Widget", 10, "sale", transaction_id=42, timestamp="2026-01-01 00:00:00")
    assert t.to_dict() == {
        "item_name": "Widget",
        "quantity": 10,
        "type": "sale",
        "timestamp": "2026-01-01 00:00:00",
        "transaction_id": 42,
    }
    text = str(t)
    assert "Widget" in text
    assert "42" in text


def test_save_and_load_transactions(tmp_path, capsys):
    """Saving a transaction should write to the file and loading should restore it."""
    # create and persist a transaction
    t1 = Transaction("ItemA", 5, "purchase")
    Transaction.save_transaction(t1)
    captured = capsys.readouterr()
    assert "Saving transactions" in captured.out

    # verify on-disk content
    with open(Transaction.transactions_data, "r") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["item_name"] == "ItemA"

    # load from file and examine class state
    Transaction.load_transactions_from_file()
    assert len(Transaction.transactions) == 1
    loaded = Transaction.transactions[0]
    assert loaded.item_name == "ItemA"
    assert loaded.quantity == 5
    assert loaded.type == "purchase"
    assert loaded.transaction_id == 0

    # saving a second transaction should increment the ID
    t2 = Transaction("ItemB", 3, "sale")
    Transaction.save_transaction(t2)
    Transaction.load_transactions_from_file()
    assert len(Transaction.transactions) == 2
    assert Transaction.transactions[-1].transaction_id == 1
