import datetime
from tabulate import tabulate
import os
from utils.storage_handler import save_to_file, load_from_file


class Transaction:
    id_counter = 0  # Class variable to auto-increment transaction IDs
    transactions = []
    transactions_data = "data/transactions.json"

    def __init__(self, item_name, quantity, transaction_type, transaction_id=None, timestamp=None):
        if transaction_id is None:
            self.transaction_id = Transaction.id_counter
            Transaction.id_counter += 1
        else:
            self.transaction_id = transaction_id
        
        self.item_name = item_name
        self.quantity = quantity
        self.type = transaction_type
        if not timestamp:
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.timestamp = timestamp

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "quantity": self.quantity,
            "type": self.type,
            "timestamp": self.timestamp,
            "transaction_id": self.transaction_id,
        }
    
    #provides a dictionary representation of the transaction, which is useful for saving to JSON.   
    def __repr__(self):
        return f"{self.to_dict()}"
    #a string representation of the transaction for easy debugging and display
    def __str__(self):
        return f"{self.timestamp} | {self.transaction_id} | {self.item_name} | {self.type} | {self.quantity}"
    
    #refers to the class rather than an instance which allows modifying data at class level like adding a transaction and writing to file.    
    @classmethod
    def save_transaction(cls, transaction):
        cls.transactions.append(transaction)
        cls._write_transactions_to_file()
    
    #loads transactions from the JSON file and populates the transactions list. 
    # It also updates the id_counter to ensure unique transaction IDs for new transactions.
    @classmethod
    def load_transactions_from_file(cls):
        data = load_from_file(cls.transactions_data)
        cls.transactions = []
        max_id = -1
        for item in data:
            # Update max_id to ensure the next transaction gets a unique ID
            max_id = max(max_id, item["transaction_id"])
            t = cls(
                item["item_name"],
                item["quantity"],
                item["type"],
                item["transaction_id"],
                item["timestamp"]
            )
            cls.transactions.append(t)
            
            if t.transaction_id > max_id:
                max_id = t.transaction_id
        cls.id_counter = max_id + 1


    @classmethod
    def _write_transactions_to_file(cls):
        print("Saving transactions...")
        save_to_file(cls.transactions, cls.transactions_data)
        
    @classmethod
    def list_transactions(cls):
        if not cls.transactions:
            print("\n📂 No transactions recorded yet.")
            return
        #using tabulate library to display transactions in a formatted table(pretty printing)
        headers = ["Item", "Quantity", "Type", "Timestamp", "ID"]
        table_data = []
        for item in cls.transactions:
            table_data.append([item.item_name, item.quantity, item.type, item.timestamp, item.transaction_id])
        print(tabulate(table_data, headers=headers, tablefmt="grid" ))
        

    