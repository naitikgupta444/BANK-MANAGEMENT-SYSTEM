# Bank Management System

A simple console-based bank account management system written in Python. Accounts are stored locally in a CSV file — no external dependencies or database required.

## Features

- Create an account (with email and mobile number validation)
- Credit money
- Debit money (enforces a minimum balance)
- Check balance
- Update account details (name, email, mobile number, password)
- Delete an account

## Requirements

- Python 3.10+ (uses `match` syntax-free structure but relies on the `X | None` type hint style, so 3.10 or newer is recommended)
No third-party packages are required — everything uses the Python standard library.

## Getting Started

```bash
git clone https://github.com/<your-username>/bank-management-system.git
cd bank-management-system
python3 bank_management_system.py
```

On first run, a `data/accounts.csv` file is created automatically to store account records. This file is git-ignored so your local test data never gets committed.

## Security Notes

- Passwords are never stored in plain text — they are hashed with SHA-256 before being written to disk.
- Password entry uses `getpass`, so it isn't echoed to the terminal.
- This project is for learning/demo purposes. SHA-256 alone (without salting) is **not** considered sufficient for a production authentication system — for real-world use, use a salted password hash such as `bcrypt` or `argon2`.

## Project Structure

```
bank-management-system/
├── bank_management_system.py   # Main application
├── data/                       # Auto-created; stores accounts.csv (git-ignored)
├── .gitignore
├── LICENSE
└── README.md
```
