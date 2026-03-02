import json
import os
from models.Products import Product


class InventoryService:
    def __init__(self, file_path="data/products.json"):
        self.file_path = file_path

    def load_products(self):
        """
        Load products from JSON file.
        Returns a list of Product objects.
        """
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r") as file:
            data = json.load(file)

        return [Product.from_dict(item) for item in data]