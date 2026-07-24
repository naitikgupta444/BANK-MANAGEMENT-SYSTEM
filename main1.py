import csv
import random
import re
import sys
import time
import hashlib
from pathlib import Path
from getpass import getpass # Makes the password typed by the user on the terminal invisible

DATA_FILE = Path(__file__).parent / "data" / "accounts.csv"  # points to data/accounts.csv, next to this script, on any OS
FIELDS = ["Name", "Age", "Password", "Acc_No", "Balance", "E-Mail", "Mobile_Number"]  # CSV column names, in the order they're written
 
MIN_INITIAL_BALANCE = 1500  # initial deposit must be strictly greater than this amount
MIN_BALANCE_AFTER_DEBIT = 1500  # balance can never drop below this after a withdrawal
 
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")  # regex used to validate email format
MOBILE_PATTERN = re.compile(r"^[1-9][0-9]{9}$")  # regex used to validate a 10-digit mobile number
PASSWORD_PATTERN = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^\w\s]).{8,}$") # regex used to validate password of the customer
AGE_PATTERN = re.compile(r"^[0-9]{2,3}$") # regex used to validate age of the customer creating an account

# Creates accounts.csv with just a header row, but only if it doesn't already exist
def ensure_data_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()
            
 
# Reads the CSV and returns a list of dicts, one per account row
def read_accounts():
    ensure_data_file()
    with open(DATA_FILE, "r", newline="") as f:
        return list(csv.DictReader(f))
 
 
# Overwrites the whole file with the given rows (not an append)
def write_accounts(rows):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
 
 
# Hashes the password with SHA-256 before storing it — this is one-way and cannot be reversed,
# which is exactly what we want: we only ever need to compare, never recover the original
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
 
 
# Looks up an account by account number + password; returns the matching row, or None if not found
def find_account(rows, acc_no, password):
    hashed = hash_password(password)
    for row in rows:
        if row["Acc_No"] == str(acc_no).strip() and row["Password"] == hashed:
            return row
    return None
 
 
# Repeatedly prompts until the user enters a valid whole number (used for deposits, withdrawals, initial balance)
def ask_amount(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("\tThat doesn't look like a number, try again.")
 
 
# Generates a random account number that isn't already in use
def new_account_number(taken):
    acc_no = random.randint(100000, 999999)
    while acc_no in taken:
        acc_no = random.randint(100000, 999999)
    return acc_no
 
 
# Walks the user through creating a new account
def Create_Account():
    print("\n\tCreate Account")
    name = input("\tEnter your name: ").strip()
    if not name:
        print("\tName can't be blank.")
        return

    while True:
        age = input("\tEnter your Age: ").strip()
        if AGE_PATTERN.fullmatch(age) and int(age) >= 18:
            break
        print("\n\tAge can't be blank OR You are underage to create an account.\n") 

    while True:
        password = getpass("\tEnter a password for your account: ")
        if password and PASSWORD_PATTERN.fullmatch(password):
            break
        print("\n\tPassword can't be blank OR Incorrect password entered")
        print("\n\tPassword must be at least 8 character long and should contain 1 special character, 1 digit, 1 capital letter, 1 small letter\n")
 
    while True:
        email = input("\tEnter your email: ").strip()
        if EMAIL_PATTERN.fullmatch(email):
            break
        print("\tPlease enter a valid email address!")
 
    while True:
        mobile = input("\tEnter your mobile number: ").strip()
        if MOBILE_PATTERN.fullmatch(mobile):
            break
        print("\tPlease enter a valid 10 digit mobile number!")
 
    rows = read_accounts()
    for row in rows:
        if name == row["Name"] or email == row["E-Mail"] or mobile == row["Mobile_Number"]:
            print("\tAn account with that name, email or mobile number already exists.")
            return
 
    while True:
        balance = ask_amount("\tEnter initial deposit amount: ")
        if balance > MIN_INITIAL_BALANCE:
            break
        print(f"\tInitial deposit has to be more than {MIN_INITIAL_BALANCE}.")
 
    print("\tPlease wait, generating your account number...")
    time.sleep(1)
    taken_numbers = {int(r["Acc_No"]) for r in rows if r.get("Acc_No")}
    acc_no = new_account_number(taken_numbers)
 
    rows.append({
        "Name": name,
        "Age" : age,
        "Password": hash_password(password),
        "Acc_No": acc_no,
        "Balance": balance,
        "E-Mail": email,
        "Mobile_Number": mobile,
    })
    write_accounts(rows)
 
    print("\n\t------------CONGRATULATIONS Your Account Is Created--------------")
    print(f"\tYour account number is: {acc_no}")
    print("\tPlease make a note of it.")
    print("\t*Welcome to BANK MANAGEMENT SYSTEM*\n")
 
 
# Shows the current balance for the account, if the credentials match
def Check_Balance():
    rows = read_accounts()
    if not rows:
        print("\n\tNo records exist yet.")
        return
    acc_no = input("\n\tEnter Account Number : ")
    password = getpass("\tEnter password : ")
    account = find_account(rows, acc_no, password)
    if account:
        print(f"\tCurrent Balance in your account is : {account['Balance']} rupees")
    else:
        print("\tAccount does not exist, or the password is wrong.")
 
 
# Deposits money into an account
def Credit_Money():
    rows = read_accounts()
    if not rows:
        print("\n\tNo records exist yet.")
        return
    acc_no = input("\n\tEnter your account number : ")
    password = getpass("\tEnter the password of your account : ") 
    amount = ask_amount("\tEnter amount to deposit : ")
    if amount <= 0:
        print("\tDeposit has to be a positive amount.")
        return
 
    account = find_account(rows, acc_no, password)
    if not account:
        print("\tAccount does not exist or invalid credentials!")
        return
 
    account["Balance"] = str(int(account["Balance"]) + amount)
    write_accounts(rows)
    print(f"\tAmount Credited Successfully! New Balance: {account['Balance']} rupees")
 
 
# Withdraws money from an account, enforcing the minimum balance rule
def Debit_Money():
    rows = read_accounts()
    if not rows:
        print("\n\tNo records exist yet.")
        return
    acc_no = input("\n\tEnter Account Number : ")
    password = getpass("\tEnter Password : ")
    amount = ask_amount("\tEnter Amount to Withdraw : ")
 
    account = find_account(rows, acc_no, password)
    if not account:
        print("\tAccount does not exist or invalid credentials!")
        return
 
    balance = int(account["Balance"])
    if amount <= 0:
        print("\tWithdrawal amount has to be positive.")
    elif balance - amount < MIN_BALANCE_AFTER_DEBIT:
        print(f"\tCan't do that - balance can't drop below {MIN_BALANCE_AFTER_DEBIT}.")
    else:
        account["Balance"] = str(balance - amount)
        write_accounts(rows)
        print(f"\tAmount Debited Successfully! New Balance: {account['Balance']} rupees")
 
 
# Lets the user update their account details or password
def Update_Account():
    rows = read_accounts()
    if not rows:
        print("\n\tNo records exist yet.")
        return
    acc_no = input("\n\tEnter Account Number : ")
    password = getpass("\tEnter Password : ")
    account = find_account(rows, acc_no, password)
    if not account:
        print("\tAccount not found, or wrong password.")
        return
 
    while True:
        print("\n\t------Account Update------")
        print("\t1.Update Email")
        print("\t2.Update Password")
        print("\t3.Update Name")
        print("\t4.Update Phone Number")
        print("\t5.Back to Main Menu")
        choice = input("\tEnter the Update Number : ").strip()
 
        if choice == "1":
            new_email = input("\tEnter your new Email : ").strip()
            if not EMAIL_PATTERN.fullmatch(new_email):
                print("\tThat's not a valid email.")
                continue
            account["E-Mail"] = new_email
            write_accounts(rows)
            print("\tEmail updated successfully!")
 
        elif choice == "2":
            new_password = getpass("\tEnter your new password : ")
            if not new_password:
                print("\tPassword can't be blank.")
                continue
            account["Password"] = hash_password(new_password)
            write_accounts(rows)
            print("\tPassword updated successfully!")
 
        elif choice == "3":
            new_name = input("\tEnter your new name : ").strip()
            if not new_name:
                print("\tName can't be blank.")
                continue
            account["Name"] = new_name
            write_accounts(rows)
            print("\tName updated successfully!")
 
        elif choice == "4":
            new_mobile = input("\tEnter your new phone number : ").strip()
            if not MOBILE_PATTERN.fullmatch(new_mobile):
                print("\tThat's not a valid mobile number.")
                continue
            account["Mobile Number"] = new_mobile
            write_accounts(rows)
            print("\tPhone number updated successfully!")
 
        elif choice == "5":
            return
 
        else:
            print("\t----------Invalid Choice! Please Enter a valid Choice---------")
 
 
# Deletes an account from the system, after confirmation
def Delete_Account():
    rows = read_accounts()
    if not rows:
        print("\n\tNo records exist yet.")
        return
    acc_no = input("\n\tEnter Account Number : ")
    password = getpass("\tEnter Password : ")
    account = find_account(rows, acc_no, password)
    if not account:
        print("\tAccount not found, or wrong password.")
        return
 
    choice = input("\tARE YOU SURE YOU WANT TO DELETE YOUR ACCOUNT [y/n] : ").strip().lower()
    if choice == "y":
        rows.remove(account)
        write_accounts(rows)
        print("\tDeleted Account successfully!")
    else:
        print("\n\tOkay, nothing was deleted.")

MENU = {
    "1": Create_Account,
    "2": Credit_Money,
    "3": Debit_Money,
    "4": Check_Balance,
    "5": Update_Account,
    "6": Delete_Account,
}
 
# Runs the main menu loop
def main():
    ensure_data_file()
    while True:
        print("\n\tMain Menu")
        print("\t1.Create Account")
        print("\t2.Credit Money")
        print("\t3.Debit Money")
        print("\t4.Check Balance")
        print("\t5.Update Account")
        print("\t6.Delete Account")
        print("\t7.Exit")
 
        choice = input("\n\tEnter your choice : ").strip()
 
        if choice == "7":
            sys.exit("\n\tExiting....")
 
        action = MENU.get(choice)
        if action is None:
            print("\n\t---------Invalid operation number entered------------")
            continue
 
        try:
            action()
        except KeyboardInterrupt:
            # lets the user cancel an in-progress operation with Ctrl+C instead of crashing
            print("\n\tCancelled.")
 
if __name__ == "__main__":
    Bank_Name = "BANK MANAGEMENT SYSTEM"
    print(("*" * len(Bank_Name)).center(76))
    print(Bank_Name.center(76))
    print(("*" * len(Bank_Name)).center(76))
    try:
        main()
    except KeyboardInterrupt:
        print("\n\tExiting....\n")