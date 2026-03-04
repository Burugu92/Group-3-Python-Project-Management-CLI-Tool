import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch
from methods import Transaction

# Fixtures

@pytest.fixture(autouse=True)
def isolate_transactions(tmp_path, monkeypatch):
    temp_file = tmp_path / "transactions.json"
    monkeypatch.setattr(Transaction, "transactions_data", str(temp_file))
    Transaction.transactions = []
    Transaction.id_counter = 0
    yield

# Transaction tests

def test_transaction_to_dict_and_str():
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

def test_save_and_load_transactions(capsys):
    # First transaction
    t1 = Transaction("ItemA", 5, "purchase")
    Transaction.save_transaction(t1)
    captured = capsys.readouterr()
    assert "Saving transactions" in captured.out

    # Verify on-disk JSON
    with open(Transaction.transactions_data, "r") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["item_name"] == "ItemA"

    # Reload class state
    Transaction.load_transactions_from_file()
    loaded = Transaction.transactions[0]
    assert loaded.transaction_id == 1
    assert loaded.item_name == "ItemA"

    # Second transaction increments ID
    t2 = Transaction("ItemB", 3, "sale")
    Transaction.save_transaction(t2)
    Transaction.load_transactions_from_file()
    assert len(Transaction.transactions) == 2
    assert Transaction.transactions[-1].transaction_id == 1
