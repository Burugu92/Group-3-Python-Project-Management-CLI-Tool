
# Group-3-Python-Project-Management-CLI-Tool
📦 Inventory Management CLI Tool

A fully interactive Python Command-Line Inventory Management System built using Object-Oriented Programming principles, modular architecture, authentication, and JSON-based persistent storage.

This project was developed as part of a summative group lab to simulate building a CLI-based startup product.

🚀 Project Overview

Small businesses often need a simple and lightweight way to manage stock without expensive software.

This CLI tool allows users to:

Register and log in securely

Add, update, delete inventory items (Admin only)

View and search items

Track stock levels

Store data persistently using JSON files

The system demonstrates:

Object-Oriented Programming (OOP)

Inheritance and encapsulation

Role-based access control

File-based persistence (CRUD operations)

Modular Python structure

Git collaboration workflow

👥 Target Users

Small business owners

Warehouse managers

School or lab inventory supervisors

🧠 System Features
🔐 Authentication System

User registration

User login

Password hashing using hashlib

Role-based access (Admin / Regular User)

📦 Inventory Management

Add new items

Update item quantity and price

Delete items

View all inventory

Search items by name or category

Low stock alerts

💾 Data Persistence

JSON-based file storage

Automatic load/save functionality

CRUD operations for:

Users

Inventory Items

🏗️ Object-Oriented Design

The system uses multiple interacting classes:

User

AdminUser (inherits from User)

Item

InventoryManager

AuthManager

StorageManager

CLI

OOP Concepts Implemented

✅ Classes

✅ Inheritance (AdminUser → User)

✅ Encapsulation (private password handling)

✅ Modular design

✅ Decorators for authentication & permissions

📁 Project Structure
inventory_cli_tool/
│
├── cli.py
├── models/
│   ├── user.py
│   ├── item.py
│
├── utils/
│   ├── auth.py
│   ├── storage.py
│   ├── validators.py
│
├── data/
│   ├── users.json
│   ├── items.json
│
├── tests/
│   ├── test_user.py
│   ├── test_item.py
│
├── requirements.txt
└── README.md
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/Burugu92/Group-3-Python-Project-Management-CLI-Tool.git
cd inventory-cli-tool
2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
Run 'pipenv shell' to enter the virtual environment.
3️⃣ Install Dependencies
Run 'pipenv install' to install all necessary dependencies.
▶️ Running the Application
python cli.py

Follow the on-screen prompts to register, login, and manage inventory.

🧪 Running Tests

This project uses pytest for testing.

pytest

Tests cover:

User authentication logic

Inventory CRUD operations

Input validation

🔄 Git Workflow

main branch for stable releases

Feature branches:

feature/authentication

feature/inventory

feature/cli

feature/tests

Pull Requests for merging features

Descriptive commit messages

🛠️ Technologies Used

Python 3.10+

JSON (File Persistence)

hashlib (Password hashing)

argparse (CLI handling)

pytest (Testing)

Git & GitHub (Version control)

📌 Future Improvements

SQLite database integration

Export reports to CSV

Barcode support

REST API version

Docker containerization

👨‍💻 Team Members

Member 1 – Role

Member 2 – Role

Member 3 – Role

📄 License

This project is developed for educational purposes.
