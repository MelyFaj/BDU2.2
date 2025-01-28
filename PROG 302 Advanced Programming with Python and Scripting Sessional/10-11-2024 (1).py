class BankAccount:
    def __init__(self, account_number, balance):
        self.account_number=account_number
        self.balance=balance
    
    def deposit(self,amount):
        if(amount<0):
            return False
        self.balance+=amount

    def withdraw(self, amount):
        if(amount>self.balance):
            print("Insufficient balance")
            return False
        self.balance-=amount

class SavingsAccount(BankAccount):
    def __init__(self, account_number, balance, interest_rate):
        super().__init__(account_number, balance)
        self.interest_rate=interest_rate

    def interest(self):
        return self.balance*(self.interest_rate/100)

class Customer:
    def __init__(self, customer_id, accounts=[]):
        self.customer_id=customer_id
        self.accounts=accounts
    def add_account(self, account_number):
        self.accounts.append(account_number)
    def display(self):
        print(self.accounts)


c1 = Customer(1, 0)
c1.display()
c1.add_account(1234)
c1.display()

acc1 = BankAccount(1234, 5000)
acc1.deposit(1000)
print(acc1.balance)
acc1.withdraw(100)
print(acc1.balance)



