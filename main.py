import argparse
import sys
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
        json.dump({
            "username": user.username,
            "role": user.role
        }, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
        # You MUST have this method in User model
        return User.get_user_by_username(data["username"])

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# Helper decorators

def login_required(func):
    def wrapper(cli_context, *args, **kwargs):
        if not cli_context.get("user"):
            print("❌ You must login first.")
            return
        return func(cli_context, *args, **kwargs)
    return wrapper

def admin_required(func):
    def wrapper(cli_context, *args, **kwargs):
        user = cli_context.get("user")
        if not user or not user.is_admin():
            print("❌ Admin privileges required.")
            return
        return func(cli_context, *args, **kwargs)
    return wrapper

# CLI Command Implementations

def register(cli_context, args):
    username = args.username
    password = getpass("Enter password: ")
    role = args.role or "staff"
    try:
        user = User.create_user(username, password, role)
        print(f"✅ User '{user.username}' created with role '{role}'.")
    except ValueError as ve:
        print(f"❌ {ve}")

def login(cli_context, args):
    username = args.username
    password = getpass("Enter password: ")
    user = User.authenticate(username, password)
    if user:
        save_session(user)
        print(f"✅ Logged in as {user.username} ({user.role})")
    else:
        print("❌ Invalid credentials.")

def logout(cli_context, args):
    clear_session()
    print("✅ Logged out successfully.")

@login_required
def add_product(cli_context, args):
    user = cli_context["user"]
    if not user.is_admin():
        print("❌ Only admins can add products.")
        return

    products_file = "data/products.json"
    products = load_products(products_file)

    product_id = max([p.product_id for p in products], default=0) + 1
    new_product = Product(product_id, args.name, args.category, args.price, args.quantity)
    products.append(new_product)
    save_products(products_file, products)

    print(f"✅ Product '{args.name}' added successfully.")

@login_required
def list_products(cli_context, args):
    print_section("Inventory Products", Color.CYAN)
    products_file = "data/products.json"
    products = load_products(products_file)

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
    
    products_file = "data/products.json"
    products = load_products(products_file)

    product = next((p for p in products if p.product_id == args.product_id), None)
    if not product:
        print("❌ Product not found.")
        return

    try:
        product.decrease_stock(args.quantity)
        save_products(products_file, products)

        transaction = Transaction(product.name, args.quantity, "sale")
        Transaction.save_transaction(transaction)

        print(f"✅ Sold {args.quantity} x {product.name}")
    except ValueError as ve:
        print(f"❌ {ve}")

@login_required
def restock_product(cli_context, args):
    user = cli_context["user"]
    if not user.is_admin():
        print("❌ Only admins can restock products.")
        return

    products_file = "data/products.json"
    products = load_products(products_file)

    product = next((p for p in products if p.product_id == args.product_id), None)
    if not product:
        print("❌ Product not found.")
        return

    product.increase_stock(args.quantity)
    save_products(products_file, products)

    transaction = Transaction(product.name, args.quantity, "restock")
    Transaction.save_transaction(transaction)

    print(f"✅ Restocked {args.quantity} x {product.name}")

@login_required
def list_transactions_cli(cli_context, args):
    print_section("All Transactions", Color.CYAN)
    user = cli_context["user"]
    if user.role == "viewer":
        print("❌ Viewers cannot view transaction history.")
        return
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

# JSON Helpers

def load_products(file_path="data/products.json"):
    from utils.storage_handler import load_from_file
    data = load_from_file(file_path)
    return [Product.from_dict(d) for d in data]

def save_products(file_path, products):
    from utils.storage_handler import save_to_file
    save_to_file([p.to_dict() for p in products], file_path)
    
#for menu styling and color output    
def print_section(title, color_code="\033[94m"):
    """
    Prints a styled header like: ══════════ TITLE ══════════
    Default color is Cyan.
    """
    width = 60
    # Clean up the title and center it
    styled_title = f" {title.upper()} "
    # Fill the rest with '=' or '═'
    padding = (width - len(styled_title)) // 2
    line = "═" * padding
    
    reset = "\033[0m"
    print(f"\n{color_code}{line}{styled_title}{line}{reset}\n")

# ANSI Color shortcuts
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# CLI Argument Parser

def main():
    cli_context = {"user": load_session()}  # Auto-load session

    parser = argparse.ArgumentParser(description="CLI Inventory Management System")
    subparsers = parser.add_subparsers(dest="command")

    reg_parser = subparsers.add_parser("register", help="Register a new user")
    reg_parser.add_argument("username")
    reg_parser.add_argument("--role", choices=["admin", "staff", "viewer"])
    reg_parser.set_defaults(func=register)

    login_parser = subparsers.add_parser("login", help="Login as user")
    login_parser.add_argument("username")
    login_parser.set_defaults(func=login)

    subparsers.add_parser("logout", help="Logout current user").set_defaults(func=logout)

    add_prod_parser = subparsers.add_parser("add-product", help="Add a new product (admin only)")
    add_prod_parser.add_argument("name")
    add_prod_parser.add_argument("category")
    add_prod_parser.add_argument("price", type=float)
    add_prod_parser.add_argument("quantity", type=int)
    add_prod_parser.set_defaults(func=add_product)

    subparsers.add_parser("list-products", help="List all products").set_defaults(func=list_products)

    sell_parser = subparsers.add_parser("sell-product", help="Sell a product")
    sell_parser.add_argument("product_id", type=int)
    sell_parser.add_argument("quantity", type=int)
    sell_parser.set_defaults(func=sell_product)

    restock_parser = subparsers.add_parser("restock-product", help="Restock a product (admin only)")
    restock_parser.add_argument("product_id", type=int)
    restock_parser.add_argument("quantity", type=int)
    restock_parser.set_defaults(func=restock_product)

    subparsers.add_parser("list-transactions", help="View all transactions").set_defaults(func=list_transactions_cli)

    subparsers.add_parser("list-users", help="List all users (admin only)").set_defaults(func=list_users_cli)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(cli_context, args)
    else:
        print_section("Inventory Management System", Color.BOLD + Color.GREEN)
        #parser.print_help()
        menu_options = [
            ["Command", "Action", "Permission"],
            ["1. login", "Access your account", "Public"],
            ["2. list-products", "View inventory", "Staff/Admin"],
            ["3. add-product", "Create new entry", "Admin Only"],
            ["4. sell-product", "Register a sale", "Staff/Admin"],
            ["5. list-users", "Manage team", "Admin Only"],
        ]
        print(tabulate(menu_options, headers="firstrow", tablefmt="simple"))
        print(f"\n{Color.YELLOW}💡 Hint: Use --help after any command for details.{Color.END}\n")

if __name__ == "__main__":
    main()