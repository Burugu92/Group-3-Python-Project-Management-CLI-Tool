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
    else:
        print_section("CLI Inventory Management System", Color.BOLD + Color.GREEN)
        #parser.print_help()
        menu_options = [["#", "Command", "Action", "Permission"],
    ["1", "register", "Create a new account", "Public"],
    ["2", "login", "Access your account", "Public"],
    ["3", "list-products", "View inventory", "Staff/Admin/Viewer"],
    ["4", "add-product", "Create new entry", "Admin Only"],
    ["5", "sell-product", "Register a sale", "Staff/Admin"],
    ["6", "restock-product", "Increase stock levels", "Admin Only"],
    ["7", "list-transactions", "View audit history", "Staff/Admin"],
    ["8", "list-users", "Manage team", "Admin Only"],
    ["9", "logout", "Exit current session", "Public"]
    
]
        
        print(tabulate(menu_options, headers="firstrow", tablefmt="simple"))
        print(f"\n{Color.YELLOW}💡 Hint: Use --help after any command for details.{Color.END}\n")

if __name__ == "__main__":
    main()