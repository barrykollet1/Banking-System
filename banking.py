import random
import sqlite3


class BankingSystem:

    def __init__(self):
        self.MII = '4'
        self.IIN = '00000'
        self.BIN = self.MII + self.IIN
        self.conn = sqlite3.connect('card.s3db')
        cur = self.conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS CARD (ID INTEGER, NUMBER TEXT, PIN TEXT, BALANCE INTEGER)")
        self.conn.commit()

    def get_id(self):
        cur = self.conn.cursor()
        cur.execute("SELECT ID FROM CARD ORDER BY ID DESC LIMIT 1")
        res = cur.fetchone()

        return 0 if res is None else res[0] + 1

    def get_checksum(self, bin_card):
        if len(bin_card) != 15:
            print("Bad Card Number")
            checksum = ''
        else:
            # ALGO DE LUNH
            bin_card = [int(i) for i in bin_card]
            bin_card = [j * 2 if not i % 2 else j for i, j in enumerate(bin_card)]
            bin_card = [i if i <= 9 else i - 9 for i in bin_card]
            checksum = [i for i in range(10) if not (i + sum(bin_card)) % 10][0]
        return checksum

    def lunh_algo(self, bin_card):
        if len(bin_card) != 16:
            # print("Bad Card Number")
            return False
        else:
            checksum = bin_card[15:16]
            bin_card = bin_card[:15]

            bin_card = [int(i) for i in bin_card]
            bin_card = [j * 2 if not i % 2 else j for i, j in enumerate(bin_card)]
            bin_card = [i if i <= 9 else i - 9 for i in bin_card]

            return not (sum(bin_card) + int(checksum)) % 10

    def create_account(self):
        while True:
            account_identifier = str(random.randrange(0, 999999999)).zfill(9)
            checksum = self.get_checksum(self.BIN + account_identifier)
            card_pin = str(random.randrange(0, 9999)).zfill(4)
            card_num = self.BIN + account_identifier + str(checksum)
            if not self.card_exist(card_num):
                break

        # CardAnatomy.list_of_card[card_num] = {'solde': 0, 'code': card_pin}
        cur = self.conn.cursor()
        cur.execute("INSERT INTO CARD VALUES({},{},{},{})".format(self.get_id(), card_num, card_pin, 0))
        self.conn.commit()

        print()
        print("Your card has been created")
        print("Your card number:")
        print(card_num)
        print("Your card number:")
        print(card_pin)

    def card_exist(self, num_card):
        cur = self.conn.cursor()
        cur.execute("SELECT NUMBER FROM CARD WHERE NUMBER = {}".format(num_card))
        return False if cur.fetchone() is None else True

    def login_account(self, num_card, code_pin):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM CARD WHERE NUMBER = {}".format(num_card))
        resultat = cur.fetchone()

        # if num_card in CardAnatomy.list_of_card and CardAnatomy.list_of_card[num_card]['code'] == code_pin:
        if resultat is not None and num_card == resultat[1] and code_pin == resultat[2]:
            print()
            print("You have successfully logged in!")
            return True
        else:
            print()
            print("Wrong card number or PIN!")
            return False

    def balance(self, num_card):
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM CARD WHERE NUMBER = {}".format(num_card))
        return cur.fetchone()[0]

    def add_income(self, num_card):
        montant = int(input("Enter income: "))
        solde = self.balance(num_card)
        cur = self.conn.cursor()
        cur.execute("UPDATE CARD SET BALANCE = {} WHERE NUMBER = {}".format(solde + montant, num_card))
        self.conn.commit()
        print("Income was added!")

    def transfert(self, num_card_src):
        print("Transfer")
        num_card_dst = input("Enter card number: ")

        if num_card_src == num_card_dst:
            print("You can't transfer money to the same account!")
        elif not self.lunh_algo(num_card_dst):
            print("Probably you made a mistake in the card number. Please try again!")
        elif not self.card_exist(num_card_dst):
            print("Such a card does not exist.")
        else:
            montant = int(input("Enter how much money you want to transfer: "))
            if montant > self.balance(num_card_src):
                print("Not enough money!")
            else:
                solde_src = self.balance(num_card_src)
                solde_dst = self.balance(num_card_dst)
                cur = self.conn.cursor()
                cur.execute("UPDATE CARD SET BALANCE = {} WHERE NUMBER = {}".format(solde_src - montant, num_card_src))
                cur.execute("UPDATE CARD SET BALANCE = {} WHERE NUMBER = {}".format(solde_dst + montant, num_card_dst))
                self.conn.commit()
                print('Success!')

    def close_account(self, num_card):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM CARD WHERE NUMBER = {}".format(num_card))
        self.conn.commit()
        print("\nThe account has been closed!")

    def account_menu(self, num_card):
        while True:
            print()
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            mng_choice = input()

            if mng_choice == '1':
                print("\n", self.balance(num_card))
            if mng_choice == '2':
                self.add_income(num_card)
            if mng_choice == '3':
                self.transfert(num_card)
            if mng_choice == '4':
                self.close_account(num_card)
                break
            elif mng_choice == '5':
                print("\nYou have successfully logged out!")
                break
            elif mng_choice == '0':
                print('\nBye!')
                exit(0)
    
    # Fonction permattant d'afficher tous les comptes
    def all_count(self):
        cur = self.conn.cursor()
        cur.execute("select * from card")
        for res in cur.fetchall():
            print(res[0], res[1], res[2], res[3],)

    def bank_menu(self):
        while True:
            print()
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
            trans_choice = input()
            if trans_choice == '1':
                self.create_account()
            elif trans_choice == '2':
                print()
                num_card = input("Enter your card number: ")
                code_pin = input("Enter your PIN: ")
                if self.login_account(num_card, code_pin):
                    self.account_menu(num_card)
            elif trans_choice == '3':
                # self.all_count()
                pass
            elif trans_choice == '0':
                print()
                print('Bye!')
                break


# Instanciation de la classe
my_card = BankingSystem()
# Execution du programme
my_card.bank_menu()
