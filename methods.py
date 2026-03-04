import os
import json
from getpass import getpass
from tabulate import tabulate
from models.Products import Product
from models.transactions import Transaction
from models.user import User

SESSION_FILE = "data/session.json"

# Session Helpers

def save_session(user):
    os.makedirs("data", exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"username": user.username, "role": user.role}, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
        return User.get_user_by_username(data["username"])

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# Decorators

def login_required(func):
    def wrapper(cli_context, args):
        if not cli_context.get("user"):
            print("❌ You must login first.")
            return
        return func(cli_context, args)
    return wrapper

def admin_required(func):
    def wrapper(cli_context, args):
        user = cli_context.get("user")
        if not user or not user.is_admin():
            print("❌ Admin privileges required.")
            return
        return func(cli_context, args)
    return wrapper

# CLI Handlers

def register(cli_context, args):
    password = getpass("Enter password: ")
    try:
        user = User.create_user(args.username, password, args.role or "staff")
        print(f"✅ User '{user.username}' created with role '{user.role}'.")
    except ValueError as ve:
        print(f"❌ {ve}")

def login(cli_context, args):
    if cli_context.get("user"):
        print(f"❌ Already logged in as {cli_context['user'].username} ({cli_context['user'].role})")
        return
    password = getpass("Enter password: ")
    user = User.authenticate(args.username, password)
    if user:
        save_session(user)
        cli_context["user"] = user
        print(f"✅ Logged in as {user.username} ({user.role})")
    else:
        print("❌ Invalid credentials.")

def logout(cli_context, args):
    if not cli_context.get("user"):
        print("❌ No user is currently logged in.")
        return
    clear_session()
    print(f"✅ Logged out successfully ({cli_context['user'].username})")
    cli_context["user"] = None

@login_required
@admin_required
def add_product(cli_context, args):
    if args.price <= 0 or args.quantity <= 0:
        print("❌ Price and quantity must be greater than zero.")
        return
    products = load_products()
    product_id = max([p.product_id for p in products], default=0) + 1
    new_product = Product(
        product_id,
        args.name.strip(),
        args.category.strip(),
        args.price,
        args.quantity
    )
    products.append(new_product)
    save_products(products)
    print(f"✅ Product '{args.name}' added successfully.")

@login_required
def list_products(cli_context, args):
    print_section("Inventory Products", Color.CYAN)
    products = load_products()
    if not products:
        print("📦 No products found.")
        return
    table = [[p.product_id, p.name, p.category, p.price, p.quantity] for p in products]
    print(tabulate(table, headers=["ID", "Name", "Category", "Price", "Qty"], tablefmt="grid"))

@login_required
def sell_product(cli_context, args):
    user = cli_context["user"]
    if user.role == "viewer":
        print("❌ Viewers can only view products.")
        return
    products = load_products()
    product = next((p for p in products if p.product_id == args.product_id), None)
    if not product:
        print("❌ Product not found.")
        return
    try:
        product.decrease_stock(args.quantity)
        save_products(products)
        transaction = Transaction(product.name, args.quantity, "sale")
        Transaction.save_transaction(transaction)
        print(f"✅ Sold {args.quantity} x {product.name}")
    except ValueError as ve:
        print(f"❌ {ve}")

@login_required
@admin_required
def restock_product(cli_context, args):
    products = load_products()
    product = next((p for p in products if p.product_id == args.product_id), None)
    if not product:
        print("❌ Product not found.")
        return
    product.increase_stock(args.quantity)
    save_products(products)
    transaction = Transaction(product.name, args.quantity, "restock")
    Transaction.save_transaction(transaction)
    print(f"✅ Restocked {args.quantity} x {product.name}")

@login_required
def list_transactions_cli(cli_context, args):
    user = cli_context["user"]
    if user.role == "viewer":
        print("❌ Viewers cannot view transaction history.")
        return
    print_section("All Transactions", Color.CYAN)
    Transaction.load_transactions_from_file()
    Transaction.list_transactions()

@login_required
@admin_required
def list_users_cli(cli_context, args):
    print_section("All Registered Users", Color.PURPLE)
    user = cli_context["user"]
    users = user.list_users()
    table = [[u["id"], u["username"], u["role"]] for u in users]
    print(tabulate(table, headers=["ID", "Username", "Role"], tablefmt="grid"))

# Storage Helpers

def load_products():
    from utils.storage_handler import load_from_file
    data = load_from_file("data/products.json")
    return [Product.from_dict(d) for d in data]

def save_products(products):
    from utils.storage_handler import save_to_file
    save_to_file([p.to_dict() for p in products], "data/products.json")

# UI Helpers

def print_section(title, color_code="\033[94m"):
    width = 60
    styled_title = f" {title.upper()} "
    padding = (width - len(styled_title)) // 2
    line = "═" * padding
    reset = "\033[0m"
    print(f"\n{color_code}{line}{styled_title}{line}{reset}\n")

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'