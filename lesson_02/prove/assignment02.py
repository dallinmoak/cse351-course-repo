"""
Course    : CSE 351
Assignment: 02
Student   : <your name here>

Instructions:
    - review instructions in the course
"""

# Don't import any other packages for this assignment
import os
import random
import threading
from money import *
from cse351 import *

# ---------------------------------------------------------------------------
def main(): 

    print('\nATM Processing Program:')
    print('=======================\n')

    create_data_files_if_needed()

    # Load ATM data files
    data_files: list = get_filenames('data_files')
    # print(data_files)
    
    log: Log = Log(show_terminal=True)
    log.start_timer()

    bank: Bank = Bank()

    test_data_files: list = [
        'test_file_01.dat'
    ]

    atm_readers = [
        # ATM_Reader(bank, target_file) for target_file in test_data_files
        ATM_Reader(bank, target_file) for target_file in data_files
    ]



    for atm_reader in atm_readers:
        atm_reader.start()

    print('waiting for ATM readers to finish')

    for atm_reader in atm_readers:
        atm_reader.join()

    print('all ATM readers have finished')
    for account_id in range(1, 21):
        balance: Money = bank.get_balance(account_id)
        print(f'  - account {account_id} balance is {str(balance)}')

    # TODO - Add a ATM_Reader for each data file

    test_balances(bank)

    log.stop_timer('Total time')




# ===========================================================================
class Bank():
    # TODO - implement this class here
    def __init__(self):
        print('intializing bank')
        self.accounts = {
            i: Account() for i in range(1, 21)
        }
        # for account_id, account in self.accounts.items():
        #     print(f'  - account {account_id} initialized with balance {account.get_balance()}')

    def deposit(self, account_id: int, amount: Money):
        self.accounts[account_id].deposit(amount)

    def withdraw(self, account_id: int, amount: Money):
        self.accounts[account_id].withdraw(amount)


    def get_balance(self, account_id: int)-> Money:
        account: Account = self.accounts[account_id]
        balance: Money = account.get_balance()
        return balance

# ===========================================================================
class ATM_Reader(threading.Thread):
    def __init__(self, bank: Bank, target_file: str):
        threading.Thread.__init__(self)
        self.bank = bank
        self.target_file = target_file
        print(f'initializing ATM reader for {target_file}')

    def run(self):
        print(f'Running ATM reader for {self.target_file}')
        with open(self.target_file, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) != 3:
                    continue
                account_number = int(parts[0])
                type = parts[1].lower()
                amount = Money(parts[2])
                if type == 'd':
                    self.bank.deposit(account_number, amount)
                elif type == 'w':
                    self.bank.withdraw(account_number, amount)


# ===========================================================================
class Account():
    # TODO - implement this class here
    def __init__(self):
        print('intializing account')
        self.balance: Money = Money('0.00')

    def deposit(self, amount: Money):
        self.balance.add(amount)

    def withdraw(self, amount: Money):
        self.balance.sub(amount)

    def get_balance(self)-> Money:
        return self.balance


# ---------------------------------------------------------------------------

def get_filenames(folder):
    """ Don't Change """
    filenames = []
    for filename in os.listdir(folder):
        if filename.endswith(".dat"):
            filenames.append(os.path.join(folder, filename))
    return filenames

# ---------------------------------------------------------------------------
def create_data_files_if_needed():
    """ Don't Change """
    ATMS = 10
    ACCOUNTS = 20
    TRANSACTIONS = 250000

    sub_dir = 'data_files'
    if os.path.exists(sub_dir):
        return

    print('Creating Data Files: (Only runs once)')
    os.makedirs(sub_dir)

    random.seed(102030)
    mean = 100.00
    std_dev = 50.00

    for atm in range(1, ATMS + 1):
        filename = f'{sub_dir}/atm-{atm:02d}.dat'
        print(f'- {filename}')
        with open(filename, 'w') as f:
            f.write(f'# Atm transactions from machine {atm:02d}\n')
            f.write('# format: account number, type, amount\n')

            # create random transactions
            for i in range(TRANSACTIONS):
                account = random.randint(1, ACCOUNTS)
                trans_type = 'd' if random.randint(0, 1) == 0 else 'w'
                amount = f'{(random.gauss(mean, std_dev)):0.2f}'
                f.write(f'{account},{trans_type},{amount}\n')

    print()

# ---------------------------------------------------------------------------
def test_balances(bank: Bank):
    """ Don't Change """

    # Verify balances for each account
    correct_results = (
        (1, '59362.93'),
        (2, '11988.60'),
        (3, '35982.34'),
        (4, '-22474.29'),
        (5, '11998.99'),
        (6, '-42110.72'),
        (7, '-3038.78'),
        (8, '18118.83'),
        (9, '35529.50'),
        (10, '2722.01'),
        (11, '11194.88'),
        (12, '-37512.97'),
        (13, '-21252.47'),
        (14, '41287.06'),
        (15, '7766.52'),
        (16, '-26820.11'),
        (17, '15792.78'),
        (18, '-12626.83'),
        (19, '-59303.54'),
        (20, '-47460.38'),
    )

    wrong = False
    for account_number, balance in correct_results:
        bal = bank.get_balance(account_number)
        print(f'{account_number:02d}: balance = {bal}')
        if Money(balance) != bal:
            wrong = True
            print(f'Wrong Balance: account = {account_number}, expected = {balance}, actual = {bal}')

    if not wrong:
        print('\nAll account balances are correct')



if __name__ == "__main__":
    main()

