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

    def save_products(self, products):
        """
        Save list of Product objects to JSON file.
        """
        with open(self.file_path, "w") as file:
            json.dump([product.to_dict() for product in products], file, indent=4)

    def create_product(self, name, category, price, quantity):
        """
        Create and store a new product.
        """
        products = self.load_products()

        new_id = 1
        if products:
            new_id = max(product.product_id for product in products) + 1

        new_product = Product(new_id, name, category, price, quantity)
        products.append(new_product)

        self.save_products(products)
        return new_product

    def get_all_products(self):
        """
        Return all products.
        """
        return self.load_products()

    def update_product(self, product_id, name=None, category=None, price=None, quantity=None):
        """
        Update an existing product.
        """
        products = self.load_products()

        for product in products:
            if product.product_id == product_id:
                if name is not None:
                    product.name = name
                if category is not None:
                    product.category = category
                if price is not None:
                    product.price = float(price)
                if quantity is not None:
                    product.quantity = int(quantity)

                self.save_products(products)
                return product

        return None

    def delete_product(self, product_id):
        """
        Delete a product by ID.
        """
        products = self.load_products()
        updated_products = [p for p in products if p.product_id != product_id]

        self.save_products(updated_products)