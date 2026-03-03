import pytest
from models.Products import Product
from services.inventory_service import InventoryService


# -------------------------
# PRODUCT MODEL TESTS
# -------------------------

def test_product_creation():
    product = Product(1, "MacBook Pro", "Laptops", 2500, 5)

    assert product.product_id == 1
    assert product.name == "MacBook Pro"
    assert product.category == "Laptops"
    assert product.price == 2500.0
    assert product.quantity == 5


def test_increase_stock():
    product = Product(1, "iPad Pro", "Tablets", 1200, 3)
    product.increase_stock(2)

    assert product.quantity == 5


def test_decrease_stock():
    product = Product(1, "4G Modem", "Networking", 150, 10)
    product.decrease_stock(4)

    assert product.quantity == 6


def test_decrease_stock_insufficient():
    product = Product(1, "Gaming Laptop", "Laptops", 3000, 2)

    with pytest.raises(ValueError):
        product.decrease_stock(5)


def test_to_dict():
    product = Product(1, "iPhone 15", "Smartphones", 999, 8)
    data = product.to_dict()

    assert data["name"] == "iPhone 15"
    assert data["quantity"] == 8


# -------------------------
# INVENTORY SERVICE TESTS
# -------------------------

def test_create_and_get_product(tmp_path):
    test_file = tmp_path / "products.json"
    service = InventoryService(file_path=str(test_file))

    service.create_product("Dell XPS 13", "Laptops", 1800, 4)
    products = service.get_all_products()

    assert len(products) == 1
    assert products[0].name == "Dell XPS 13"


def test_delete_product(tmp_path):
    test_file = tmp_path / "products.json"
    service = InventoryService(file_path=str(test_file))

    product = service.create_product("Huawei Modem", "Networking", 120, 10)
    service.delete_product(product.product_id)

    products = service.get_all_products()
    assert len(products) == 0


def test_update_product(tmp_path):
    test_file = tmp_path / "products.json"
    service = InventoryService(file_path=str(test_file))

    product = service.create_product("Surface Pro", "Tablets", 1500, 6)
    service.update_product(product.product_id, quantity=12)

    updated = service.get_all_products()[0]
    assert updated.quantity == 12