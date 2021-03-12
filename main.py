from fpdf import FPDF
import random
import sqlite3





class User:

    def __init__(self, name):
        self.name = name

    def buy(self, seat, card):
        connection = sqlite3.connect(card.database)
        connection.execute("""
                  UPDATE "Card" SET "balance"=? WHERE "cvc"=? AND "number"=? AND "type"=? AND "holder"=?
                  """, [card.get_balance() - seat.get_price(), card.cvc, card.number, card.type, card.holder])
        connection.commit()
        connection.close()



class Seat:
    database = "cinema.db"


    def __init__(self, seat_id):
        self.seat_id = seat_id


    def get_price(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
                SELECT "price" FROM "Seat" WHERE "seat_id"=?
                 """, [self.seat_id])
        price = cursor.fetchall()[0][0]
        return price


    def is_free(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT "taken" FROM "Seat" WHERE "seat_id"=?
         """, [self.seat_id])
        result = cursor.fetchall()

        if result[0][0] == 1:
            availability = False
        else:
            availability = True
        return availability

    def occupy(self):
        connection = sqlite3.connect(self.database)

        connection.execute("""
            UPDATE "Seat" SET "Taken"=1 WHERE "seat_id"=?
            """, [self.seat_id])
        connection.commit()
        connection.close()



class Card:
    database = "banking.db"

    def __init__(self, type, number, cvc, holder):
        self.holder = holder
        self.cvc = cvc
        self.number = number
        self.type = type


    def get_balance(self):

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT "balance" FROM "Card" WHERE "cvc"=? AND "number"=? AND "type"=? AND "holder"=?
        """, [self.cvc, self.number, self.type, self.holder])
        balance = cursor.fetchall()[0][0]
        return balance


    def validate(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT "balance" FROM "Card" WHERE "cvc"=? AND "number"=? AND "type"=? AND "holder"=?
             """, [self.cvc, self.number, self.type, self.holder])
            balance = cursor.fetchall()[0][0]

            validated = True
            return validated


        except:
            validated = False
            return validated



class Ticket:


    def __init__(self, user, seat):
        self.seat = seat
        self.user = user


    def to_pdf(self):
        random_id = ''.join((random.choice('abcdxyzpqr') for i in range(5)))
        pdf = FPDF(orientation='P', unit='pt', format='A4')
        pdf.add_page()

        pdf.set_font(family='Times', size=24, style='B')
        pdf.cell(w=400, h=100, border=1, txt="Your Digital Ticket", align="C", ln=1)

        pdf.cell(w=200, h=80, border=1, txt="Name:")
        pdf.cell(w=200, h=80, border=1, txt=f"{self.user.name}", ln=1)

        pdf.cell(w=200, h=80, border=1, txt="Ticket ID")
        pdf.cell(w=200, h=80, border=1, txt=f"{random_id}", ln=1)

        pdf.cell(w=200, h=80, border=1, txt="Price")
        pdf.cell(w=200, h=80, border=1, txt=f"{self.seat.get_price()}", ln=1)

        pdf.cell(w=200, h=80, border=1, txt="Seat Number")
        pdf.cell(w=200, h=80, border=1, txt=f"{self.seat.seat_id}", ln=1)

        pdf.output(f"ticket {random_id}.pdf")





inp_name = input("Your full name: ")
inp_card_type = input("Your card type: ")
inp_seat_no = input("Seat number: ")

inp_card_no = int(input("Card number: "))
inp_card_cvc = int(input("Card cvc: "))
inp_card_holder = input("Card holder name: ")



zidle = Seat(inp_seat_no)


card1 = Card(inp_card_type, inp_card_no, inp_card_cvc, inp_card_holder)

validation = card1.validate()
if validation == True:
    availability = zidle.is_free()
    if availability == True:
        user = User(inp_name)
        if card1.get_balance() > zidle.get_price():
            user.buy(zidle, card1)
            zidle.occupy()
            listek = Ticket(user, zidle)
            listek.to_pdf()
            print("Transaction successful")
        else:
            print("Your card has insufficient balance")

    else:
        print("The seat is taken, please choose a different one")
else:
    print("There was an issue validating your card")
