import json
import os
from models.Products import Product


class InventoryService:
    def __init__(self, file_path="data/products.json"):
        self.file_path = file_path

    def load_products(self):
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r") as file:
            data = json.load(file)

        return [Product.from_dict(item) for item in data]

    def save_products(self, products):
        with open(self.file_path, "w") as file:
            json.dump([product.to_dict() for product in products], file, indent=4)

    def create_product(self, name, category, price, quantity):
        products = self.load_products()

        new_id = 1
        if products:
            new_id = max(product.product_id for product in products) + 1

        new_product = Product(new_id, name, category, price, quantity)
        products.append(new_product)

        self.save_products(products)
        return new_product

    def get_all_products(self):
        return self.load_products()

    def delete_product(self, product_id):
        products = self.load_products()
        products = [p for p in products if p.product_id != product_id]
        self.save_products(products)