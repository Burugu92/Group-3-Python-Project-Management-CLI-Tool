class Product:
    def __init__(self, product_id, name, category, price, quantity):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = float(price)
        self.quantity = int(quantity)

    def increase_stock(self, amount):
        """Increase product quantity"""
        self.quantity += int(amount)

    def decrease_stock(self, amount):
        """Decrease product quantity if enough stock exists"""
        amount = int(amount)
        if amount > self.quantity:
            raise ValueError("Insufficient stock.")
        self.quantity -= amount

    def to_dict(self):
        """Convert product object to dictionary (for JSON storage)"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity
        }

    @staticmethod
    def from_dict(data):
        """Create Product object from dictionary"""
        return Product(
            data["product_id"],
            data["name"],
            data["category"],
            data["price"],
            data["quantity"]
        )