import random
import uuid
# Console Banking App


# Implement Account first with name, password, UUID, which then seperates to admin v customer. 
# Admin UUID will add A to the front of UUID and Customer add C to the front of UUID. 
# User will create savings, checking, with withdraw and deposit (this is done in BankAcount class below)
class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self._uuid = str(uuid.uuid4())[:8]

    @property
    def uuid(self):
        return self._uuid

class Admin(User):
    def __init__(self, name, password):
        super().__init__(name, password)
        self._uuid = f"A-{self._uuid}"
        
    def view_all_users(self, database):
        print("\n--- System User Registry ---")
        for user_id, user_obj in database.items():
            print(f"ID: {user_id} | Name: {user_obj.name} | Role: {type(user_obj).__name__}")

class Customer(User):
    def __init__(self, name, password):
        super().__init__(name, password)
        self._uuid = f"C-{self._uuid}"
        self.accounts = {} 

    def open_account(self, account_type):
        account_number = random.randint(1000, 9999)
        if account_type.lower() == "checking":
            if "checking" in self.accounts:
                print("You already have a checking account!")
                return
            self.accounts["checking"] = CheckingAccount(account_number, self.name)
            print(f"Checking account ({account_number}) opened successfully.")
        elif account_type.lower() == "savings":
            if "savings" in self.accounts:
                print("You already have a savings account!")
                return
            self.accounts["savings"] = SavingsAccount(account_number, self.name)
            print(f"Savings account ({account_number}) opened successfully.")
        else:
            print("Invalid account type.")


# Parent class for bank accounts, deposit and withdraw may be moved over to child classes 
# This class has the deposit, withdraw and transactions functions. Validation is done in
# deposit and withdraw to ensure the inputs are correct
# Future implemenation would be to make a time stamp of the transaction + UUID support for the account number

# Class for bank accounts created, makes account number and name read only. Balance is set to 0 at account creation, 
# and list of transcation is initiatalized for history tracking. Password implemenation pending...
class BankAccount:
    def __init__(self, account_number, account_holder):
        self._account_number = account_number
        self._account_holder = account_holder
        self.balance = 0.0
        self.transaction = []

    # Account number and holder are made read only
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def account_holder(self):
        return self._account_holder
    
    # Deposit and withdraw have validation, make sure it is above 0, and withdraw validates that it has sufficent funds.
    # Enables tracking of deposits and withdrawls
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Please enter a positive number")
        self.balance += amount
        self.transaction.append({"amount": amount, "type": "Deposit", "bal": self.balance})
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Please input a value greater than 0")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transaction.append({"amount": amount, "type": "Withdraw", "bal": self.balance})
        return self.balance

    # Prints to console the list of transactions make
    def transactionHistory(self):
        if not self.transaction:
            print("Account has made no transactions.")
        else:
            for i in self.transaction:
                print(i)
    
    def __str__(self):
        return f"Account Number: {self.account_number}, Account Holder: {self.account_holder}, Balance: ${self.balance:.2f}"

# Basic account types, more functionality will be added to differinetiate
class CheckingAccount(BankAccount):
    def __str__(self):
        return f"[Checking] Acct: {self.account_number} | Balance: ${self.balance:.2f}"

class SavingsAccount(BankAccount):
    def __str__(self):
        return f"[Savings] Acct: {self.account_number} | Balance: ${self.balance:.2f}"


# Main fucntion that runs the interactive CLI with user, gathers name from user and generates a random integer for account
# number. Loops until the sign out option is selected. makes a dictontionary as a database placeholder for future
# implementation. The loop function will also be moved into a class for better readilitbily
SYSTEM_DB = {}

# Hardcoded Admin for easy testing
default_admin = Admin("RootAdmin", "admin123")
SYSTEM_DB[default_admin.uuid] = default_admin

print("=== System Initialization ===")
print(f"Created Default Admin ID: {default_admin.uuid} | Password: admin123\n")

while True:
    print("==============================")
    print("      MAIN SYSTEM GATEWAY     ")
    print("==============================")
    print("1: Register New Customer Account")
    print("2: Log In (Customer or Admin)")
    print("3: Shutdown System")
    
    choice = input("Select an option: ").strip()
    
    if choice == "3":
        print("System shutting down safely. Goodbye!")
        break
        
    # Registration for new customer users
    # Adds the users to the dictonary, password is also just a field for now, but encoding will be added later
    if choice == "1":
        name = input("Enter your name: ").strip()
        pwd = input("Create a password: ").strip()
        if not name or not pwd:
            print("Name and password cannot be blank.")
            continue
        
        new_customer = Customer(name, pwd)
        SYSTEM_DB[new_customer.uuid] = new_customer
        print(f"\nSuccess! Registration completed.")
        print(f"YOUR UNIQUE LOGIN ID IS: {new_customer.uuid}")
        print("Keep this ID safe; you will need it to log in.\n")

    # Login for existing users
    # Ensures that the user exist and the password field matches
    elif choice == "2":
        user_id = input("Enter your Unique ID (e.g., C-XXXX or A-XXXX): ").strip()
        password = input("Enter your password: ").strip()
        
        if user_id not in SYSTEM_DB or SYSTEM_DB[user_id].password != password:
            print("Authentication failed. Invalid ID or Password.\n")
            continue
            
        current_user = SYSTEM_DB[user_id]
        print(f"\nAccess Granted. Welcome, {current_user.name}!")
        
        # ------------------------------------------
        # ADMIN PANEL INTERFACE
        # ------------------------------------------
        # Loops until 2 is selected to sign out and 1 to print all users
        if isinstance(current_user, Admin):
            admin_opt = 0
            while admin_opt != 2:
                print("\n--- Administrative Control Dashboard ---")
                print("1: View All Registered Users")
                print("2: Log Out")
                try:
                    admin_opt = int(input("Select choice: "))
                except ValueError:
                    continue
                
                if admin_opt == 1:
                    current_user.view_all_users(SYSTEM_DB)
                elif admin_opt == 2:
                    print("Admin session securely terminated.")
                    
        # ------------------------------------------
        # BRANCH B: CUSTOMER BANKING INTERFACE
        # ------------------------------------------
        # Main loops will 
        elif isinstance(current_user, Customer):
            cust_opt = 0
            while cust_opt != 3:
                print("\n--- Customer Banking Hub ---")
                print("1: Open a New Bank Account (Checking/Savings)")
                print("2: Access Active Bank Accounts")
                print("3: Log Out")
                try:
                    cust_opt = int(input("Select choice: "))
                except ValueError:
                    continue
                
                if cust_opt == 1:
                    acct_type = input("Enter account type to open ('checking' or 'savings'): ").strip()
                    current_user.open_account(acct_type)
                    
                elif cust_opt == 2:
                    if not current_user.accounts:
                        print("You do not have any open accounts yet. Please open one first.")
                        continue
                    
                    print("\nYour Active Accounts:")
                    for key in current_user.accounts:
                        print(f"- {key.capitalize()}")
                    
                    select_type = input("Type the name of the account to access: ").strip().lower()
                    if select_type not in current_user.accounts:
                        print("Invalid account selection.")
                        continue
                        
                    active_account = current_user.accounts[select_type]
                    
                    # Core Banking Operations Loop
                    bank_opt = 0
                    while bank_opt != 5:
                        print(f"\n--- Managing {select_type.upper()} Account ---")
                        print("1: Check account details\n2: Deposit\n3: Withdraw\n4: Check transaction history\n5: Go Back")
                        try:
                            bank_opt = int(input("Select choice: "))
                        except ValueError:
                            continue
                            
                        match bank_opt:
                            case 1:
                                print(active_account)
                            case 2:
                                try:
                                    amt = float(input("Enter amount to deposit: $"))
                                    active_account.deposit(amt)
                                except ValueError as e:
                                    print(f"Transaction Denied: {e}")
                            case 3:
                                try:
                                    amt = float(input("Enter amount to withdraw: $"))
                                    active_account.withdraw(amt)
                                except ValueError as e:
                                    print(f"Transaction Denied: {e}")
                            case 4:
                                active_account.transactionHistory()
                            case 5:
                                print("Returning to main banking hub...")
                                
                    print("Customer session logged out.")