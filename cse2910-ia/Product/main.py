# CSE2910 IA Members Portal

"""
Title: CSE2910 IA Members Portal
Author: Parth Sakpal
Date-Created: 15-12-2022
"""

# LIBRARIES #
from flask import Flask, render_template, request, redirect
import pathlib
import sqlite3

MEMBERS_DATABASE = "member_info.db" # Database for all the members in the organization

FIRST_RUN = True

# Checks to see if database file already exists
if (pathlib.Path.cwd() / MEMBERS_DATABASE).exists():
    FIRST_RUN = False

# FLASK #
app = Flask(__name__)  # makes Flask object

# Global Variables #
TOTAL_MEMBERS = 0
TOTAL_PAYMENTS = 0
USER_NAME = ""



## LOGIN PAGE ##
@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Login page of web app
    :return: html
    """
    global USER_NAME
    ALERT = ""
    if request.form:
        USER = request.form.get("user_name")
        PASSWORD = request.form.get("password")

        ## Checks to see if correct username and password was entered
        for i in range(len(LOGIN_INFO)):
            if USER == LOGIN_INFO[i][0] and PASSWORD == LOGIN_INFO[i][1]:
                USER_NAME = LOGIN_INFO[i][0]
                USER_NAME = USER_NAME.split("_")
                # Determines the name of the user using the username entered
                USER_NAME = f"{USER_NAME[0].capitalize()} {USER_NAME[1].capitalize()}"
                return redirect("/home")
            else:
                ALERT = "Incorrect username or password."

    return render_template("login.html", alert=ALERT)


## HOME PAGE ##
@app.route('/home')
def homePage():
    """
    Homepage of the web app
    :return: html
    """
    global TOTAL_MEMBERS, TOTAL_PAYMENTS

    ## Displays the total members and the total payments
    return render_template("home.html", totalmembers=TOTAL_MEMBERS, totalpayments=TOTAL_PAYMENTS, user=USER_NAME)


## ADD MEMBERS PAGE ##
@app.route('/addmembers', methods=['GET', 'POST'])
def addMembers():
    """
    Adds members page of the web app
    :return: html
    """

    global TOTAL_MEMBERS, TOTAL_PAYMENTS

    ALERT = ""
    PAYMENT = ""

    MEMBER_DATA = []
    if request.form:
        F_NAME = request.form.get("first_name")
        MEMBER_DATA.append(F_NAME)
        L_NAME = request.form.get("last_name")
        MEMBER_DATA.append(L_NAME)
        EMAIL = request.form.get("email")
        MEMBER_DATA.append(EMAIL)
        AGE = request.form.get("age")
        MEMBER_DATA.append(AGE)
        START_DATE = request.form.get("date")




        ## Checks to see if all fields are filled out

        if F_NAME == "" or L_NAME == "" or EMAIL == "" or START_DATE == "" or AGE == "Age":
            ALERT = "Fill in all the fields"

        else:

            ## Checks to see if email given already exists in the database

            if checkEmail(EMAIL) is None:

                ALERT = "Successfully added the member"

                if AGE == "6-16 years":
                    PAYMENT = 15
                elif AGE == "60+ years":
                    PAYMENT = 15
                else:
                    PAYMENT = 25

                YEAR = int(START_DATE[3])

                END_YEAR = f"{START_DATE[0]}{START_DATE[1]}{START_DATE[2]}{YEAR + 1}{START_DATE[4]}{START_DATE[5]}{START_DATE[6]}{START_DATE[7]}{START_DATE[8]}{START_DATE[9]} "

                MEMBER_DATA.append(PAYMENT)
                MEMBER_DATA.append(START_DATE)
                MEMBER_DATA.append(END_YEAR)

                TOTAL_MEMBERS = TOTAL_MEMBERS + 1
                TOTAL_PAYMENTS = TOTAL_PAYMENTS + PAYMENT

                addData(MEMBER_DATA)

            else:
                ALERT = "A member with the given email already exists."



    return render_template("addmembers.html", alert=ALERT, payment=PAYMENT,user=USER_NAME)


@app.route('/viewmembers', methods=['GET', 'POST'])
def viewMembers():
    """
    View members page of the web app
    :return: html
    """

    MEMBER_DATA = getAllData()

    global MEMBERS_DATABASE
    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()

    # Fuzzy searches the database to see if name is there

    USER_SEARCH = request.form.get("search")

    SEARCH = CURSOR.execute(f"""
            SELECT
                *
            FROM
                members
            WHERE
                first_name LIKE "%{USER_SEARCH}%"

        ;""").fetchall()

    if SEARCH is None:
        SEARCH = ["None"]


    return render_template("viewmembers.html", members=MEMBER_DATA, search=SEARCH,user=USER_NAME)



@app.route('/delete/<MEMBER>')
def deleteMember(MEMBER):
    """
    Deletes member from database
    :param MEMBER: str
    :return: html
    """
    global MEMBERS_DATABASE, TOTAL_MEMBERS, TOTAL_PAYMENTS
    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()

    # Deletes member

    PAYMENT = CURSOR.execute(f"""
        SELECT
            payment
        FROM
            members
        WHERE
            email = '{MEMBER}'
    
    ;""").fetchone()

    CURSOR.execute(f"""
        DELETE FROM
            members
        WHERE
            email = '{MEMBER}'
    
    ;""")
    CONNECTION.commit()
    CONNECTION.close()

    PAYMENT = PAYMENT[0]

    # Updates the total members and total payments after deleting a member

    TOTAL_MEMBERS = TOTAL_MEMBERS - 1
    TOTAL_PAYMENTS = TOTAL_PAYMENTS - PAYMENT

    return redirect('/viewmembers')

def checkEmail(EMAIL):
    """
    Checks to see if email already exists
    :param EMAIL: str
    :return: str
    """

    global MEMBERS_DATABASE
    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()


    CHECK = CURSOR.execute(f"""
        SELECT
            *
        FROM
            members
        WHERE
            email = "{EMAIL}"
    
    ;""").fetchone()

    CONNECTION.close()
    return CHECK



def getData(FILENAME):
    """
    Gets data from the login csv file
    :param FILENAME: csv file
    :return: list
    """

    FILE = open(FILENAME)
    TEXT_LIST = FILE.readlines()
    FILE.close()

    for i in range(len(TEXT_LIST)):
        if TEXT_LIST[i][-1] == "\n":
            TEXT_LIST[i] = TEXT_LIST[i][:-1]  # Removes the /n from the end of each line
        TEXT_LIST[i] = TEXT_LIST[i].split(",")

    TEXT_LIST = TEXT_LIST[1:]

    return (TEXT_LIST)


def createDatabase():
    """
    Creates a database for the members.
    :return: none
    """
    global MEMBERS_DATABASE
    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()

    CURSOR.execute("""
    CREATE TABLE
        members (
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INT NOT NULL,
            payment FLOAT NOT NULL,
            start_date NOT NULL,
            end_date NOT NULL
        )
    ;""")
    CONNECTION.commit()
    CONNECTION.close()


def addData(LIST):
    """
    Adds data to the database
    :param LIST: list
    :return: None
    """
    global MEMBERS_DATABASE

    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()

    CURSOR.execute("""
        INSERT INTO
            members
        VALUES (
            ?, ?, ?, ?, ?, ?, ?
            )
    ;""", LIST)

    CONNECTION.commit()
    CONNECTION.close()


def getAllData():
    """
    fetches all the data from the database
    :return: 2D array
    """
    global MEMBERS_DATABASE, TOTAL_MEMBERS, TOTAL_PAYMENTS
    CONNECTION = sqlite3.connect(MEMBERS_DATABASE)
    CURSOR = CONNECTION.cursor()

    MEMBER_DATA = CURSOR.execute("""
        SELECT
            *
        FROM
            members
        ORDER BY
            start_date
    ;""").fetchall()

    CONNECTION.close()
    return MEMBER_DATA



if __name__ == "__main__":

    LOGIN_INFO = getData("templates/Logins.csv")

    if FIRST_RUN:
        createDatabase()

    MEMBERS = getAllData()

    for i in range(len(MEMBERS)):
        TOTAL_MEMBERS = TOTAL_MEMBERS + 1
        TOTAL_PAYMENTS = TOTAL_PAYMENTS + MEMBERS[i][4]

    app.run(debug=True)

