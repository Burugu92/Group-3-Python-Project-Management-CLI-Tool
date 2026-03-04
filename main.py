import argparse
from methods import *

def main():
    cli_context = {"user": load_session()}

    parser = argparse.ArgumentParser(description="CLI Inventory Management System")
    subparsers = parser.add_subparsers(dest="command")

    # Argparse commands

    reg = subparsers.add_parser("register")
    reg.add_argument("username")
    reg.add_argument("--role", choices=["admin", "staff", "viewer"])
    reg.set_defaults(func=register)

    login_parser = subparsers.add_parser("login")
    login_parser.add_argument("username")
    login_parser.set_defaults(func=login)

    subparsers.add_parser("logout").set_defaults(func=logout)

    add_prod = subparsers.add_parser("add-product")
    add_prod.add_argument("name")
    add_prod.add_argument("category")
    add_prod.add_argument("price", type=float)
    add_prod.add_argument("quantity", type=int)
    add_prod.set_defaults(func=add_product)

    subparsers.add_parser("list-products").set_defaults(func=list_products)

    sell = subparsers.add_parser("sell-product")
    sell.add_argument("product_id", type=int)
    sell.add_argument("quantity", type=int)
    sell.set_defaults(func=sell_product)

    restock = subparsers.add_parser("restock-product")
    restock.add_argument("product_id", type=int)
    restock.add_argument("quantity", type=int)
    restock.set_defaults(func=restock_product)

    subparsers.add_parser("list-transactions").set_defaults(func=list_transactions_cli)
    subparsers.add_parser("list-users").set_defaults(func=list_users_cli)

    args = parser.parse_args()

    # Run argparse commands
    if hasattr(args, "func"):
        args.func(cli_context, args)
        return

    # Interactive Menu
    
    while True:
        user = cli_context.get("user")
        login_status = f"(Logged in as: {user.username} - {user.role})" if user else ""
        print_section("CLI Inventory Management System", Color.BOLD + Color.GREEN)

        menu = [
            ["1", "Register"],
            ["2", f"Login {login_status}"],
            ["3", "List Products"],
            ["4", "Add Product (Admin)"],
            ["5", "Sell Product"],
            ["6", "Restock Product (Admin)"],
            ["7", "List Transactions"],
            ["8", "List Users (Admin)"],
            ["9", "Logout"],
            ["0", "Exit"]
        ]
        print(tabulate(menu, headers=["#", "Action"], tablefmt="simple"))

        choice = input("\nSelect option: ").strip()

        try:
            if choice == "1":
                username = input("Username: ").strip()
                role = input("Role (admin/staff/viewer) [default=staff]: ").strip() or "staff"
                register(cli_context, argparse.Namespace(username=username, role=role))

            elif choice == "2":
                if user:
                    print(f"❌ Already logged in as {user.username} ({user.role})")
                    continue
                username = input("Username: ").strip()
                login(cli_context, argparse.Namespace(username=username))

            elif choice == "3":
                list_products(cli_context, argparse.Namespace())

            elif choice == "4":
                if not user or not user.is_admin():
                    print("❌ Admin privileges required.")
                    continue
                name = input("Name: ").strip()
                category = input("Category: ").strip()
                try:
                    price = float(input("Price: ").strip())
                    quantity = int(input("Quantity: ").strip())
                except ValueError:
                    print("❌ Price and quantity must be numbers.")
                    continue
                add_product(cli_context, argparse.Namespace(name=name, category=category, price=price, quantity=quantity))

            elif choice == "5":
                if not user:
                    print("❌ You must login first.")
                    continue
                try:
                    product_id = int(input("Product ID: ").strip())
                    quantity = int(input("Quantity: ").strip())
                except ValueError:
                    print("❌ Product ID and quantity must be numbers.")
                    continue
                sell_product(cli_context, argparse.Namespace(product_id=product_id, quantity=quantity))

            elif choice == "6":
                if not user or not user.is_admin():
                    print("❌ Admin privileges required.")
                    continue
                try:
                    product_id = int(input("Product ID: ").strip())
                    quantity = int(input("Quantity: ").strip())
                except ValueError:
                    print("❌ Product ID and quantity must be numbers.")
                    continue
                restock_product(cli_context, argparse.Namespace(product_id=product_id, quantity=quantity))

            elif choice == "7":
                list_transactions_cli(cli_context, argparse.Namespace())

            elif choice == "8":
                if not user or not user.is_admin():
                    print("❌ Admin privileges required.")
                    continue
                list_users_cli(cli_context, argparse.Namespace())

            elif choice == "9":
                logout(cli_context, argparse.Namespace())

            elif choice == "0":
                print("Goodbye 👋")
                break

            else:
                print("❌ Invalid option.")

        except Exception as e:
            print(f"❌ {e}")

if __name__ == "__main__":
    main()