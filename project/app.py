import os
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mathcards.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    user_id = session["user_id"]

    if request.method == "POST":

        #if posting multiple things check if deck isn't null
        deck = request.form.get("deck")
        if deck != "":
            try:
                db.execute("INSERT INTO decks (user_id, deck) VALUES (?, ?)", user_id, deck)
                return redirect("/")

            except:
                #maybe change this to a pop up
                return apology("Deck already exists!", 400)


    decks = db.execute("SELECT * FROM decks WHERE user_id = ?", user_id)
    return render_template("homepage.html", decks=decks)




@app.route("/delete_deck", methods=["POST"])
@login_required
def delete_deck():
    id = request.form.get("deleted_deck")
    session['id'] = id
    return redirect("/check")


@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    id = session["id"]
    deck = db.execute("SELECT deck FROM decks WHERE id = ?", id)[0]
    deck = deck["deck"]

    if request.method == "POST":
        yes = request.form.get("yes")
        if yes:
            db.execute("DELETE FROM cards WHERE deck_id = ?", id)
            db.execute("DELETE FROM decks WHERE id = ?", id)
            flash("Deck Successfully Deleted")

        return redirect("/")

    else:
        return render_template("check.html", deck=deck)






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")





@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")






@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")


        if not username:
            return apology("Username missing!", 400)

        elif not password1:
            return apology("Password missing!", 400)

        elif password1 != password2:
            return apology("Passwords do not match", 400)


        try:
            password = generate_password_hash(password1)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password)
            return redirect("/")

        except:
            return apology("Username already exists!", 400)

    else:
        return render_template("register.html")





@app.route("/add", methods=["GET", "POST"])
@login_required
def adding_cards():
    user_id = session["user_id"]
    decks = db.execute("SELECT * FROM decks WHERE user_id = ?", user_id)
    session['maths'] = ''

    if request.method == "POST":
        deck = request.form.get("decks")
        front = request.form.get('front')
        back = request.form.get('back')

        deck_id = db.execute("SELECT id FROM decks WHERE deck = ? AND user_id = ?", deck, user_id)[0]
        deck_id = deck_id["id"]

        db.execute("INSERT INTO cards (user_id, deck_id, front, back) VALUES (?, ?, ?, ?)", user_id, deck_id, front, back)

        flash("Added card")

    return render_template("add.html", decks=decks)




@app.route("/maths")
@login_required
def maths():
    maths = request.args.get('q', '')
    print(maths)
    print(session['maths'])

    if maths == '':
        print('submission works')
        return session['maths']

    elif maths != '\\':
        if maths != ' ':
            session['maths'] += maths
        else:
            session['maths'] == ''

    else:
        session['maths'] = ''

    symbols = db.execute("SELECT code FROM math_symbols WHERE name LIKE ? LIMIT 10", '%' + session['maths'] + '%')
    html_symbols = ''


    if symbols:
        #The normal for symbol in symbols wasn't working (treated each letter as an element)
        for i in range (len(symbols)):
            symbols[i] = symbols[i]['code']
            html_symbols += f'''
            <button onclick="postSymbol('\\{symbols[i]}')">
                $$ {symbols[i]} $$
            </button>
            '''

        return html_symbols
    else:
        return ''


@app.route("/symbol_click", methods=["GET", "POST"])
@login_required
def symbol_clicked():
    symbol = request.form.get("symbol")
    html_symbol = f"\\( {symbol} \\)"
    return html_symbol





@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    #Getting the users decks
    user_id = session["user_id"]
    selected = False
    decks = db.execute("SELECT * FROM decks WHERE user_id = ?", user_id)

    #Getting an array of the decks
    decks = [list(deck.values())[2] for deck in decks]


    cards_search = db.execute("SELECT * FROM cards WHERE user_id = ?", user_id)

    if request.method == "POST":
        deck = request.form.get("decks")

        #Checking if a deck has been selected
        if deck:
            deck = db.execute("SELECT * FROM decks WHERE deck = ?", deck)[0]
            cards_search = db.execute("SELECT * FROM cards WHERE deck_id = ? AND user_id = ?", deck["id"], user_id)

        else:
            #if deck is null then the card to be edited must have been chosen
            card_id = request.form.get("cards")
            if not card_id:
                return apology("choose something", 400)


            else:
                #Initializing our variables for the editing function
                session['deck_id'] = db.execute("SELECT deck_id FROM cards WHERE id = ?", card_id)[0]
                session['card_id'] = card_id
                return redirect("/edit")


    return render_template("search.html", decks=decks, cards=cards_search, selected=selected)



@app.route("/searching", methods=["GET", "POST"])
@login_required
def searching():
    #Automatically showing the cards hat are similar to what is being searched for
    front = request.args.get('q', '')
    searching = db.execute("SELECT * FROM cards WHERE front LIKE ? AND user_id = ?", '%' + front + '%', session['user_id'])
    return render_template("searching.html", cards=searching)



@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    #Getting variables from previous function
    id = session['card_id']
    user_id = session['user_id']
    deck_id = session['deck_id']
    #Getting the value from the dictionary
    deck_id = deck_id['deck_id']
    card = db.execute("SELECT * FROM cards WHERE id = ?", id)[0]


    if request.method == "POST":
        #Getting the users inputs
        front = request.form.get('front')
        back = request.form.get('back')


        try:
            #Deleting the card to be edited and replacing it with the new inputs
            db.execute("DELETE FROM cards WHERE id = ?", id)
            db.execute("INSERT INTO cards (id, user_id, deck_id, front, back) VALUES (?, ?, ?, ?, ?)",id, user_id, deck_id, front, back)
            flash("Card Successfully Changed")
            return redirect("/")
        except:
            return apology("something went wrong", 400)

    return render_template("edit.html", card=card)


@app.route("/delete_card", methods=["POST"])
@login_required
def delete_card():
    id = session['card_id']
    db.execute("DELETE FROM cards WHERE id = ?", id)
    flash("Card Successfully Deleted")
    return redirect("/")



@app.route("/revision_decks", methods=["GET", "POST"])
@login_required
def revision_decks():
    #Getting the users decks
    user_id = session["user_id"]
    decks = db.execute("SELECT deck FROM decks WHERE user_id = ?", user_id)
    tags = db.execute("SELECT DISTINCT tags FROM cards WHERE user_id = ?", user_id)

    if request.method == "POST":
        #Decks to be revised
        decks = request.form.getlist("decks[]")

        if not decks:
            return apology("something went wrong", 400)

        cards = []

        #Collecting all the cards in those decks
        if len(decks) == 1:
            cards = db.execute("SELECT * FROM cards WHERE deck_id = (SELECT id FROM decks WHERE user_id = ? AND deck = ?)", user_id, decks[0])

        else:
            for deck in decks:
                cards_in_deck = db.execute("SELECT * FROM cards WHERE deck_id IN (SELECT id FROM decks WHERE user_id = ? AND deck = ?)", user_id, deck)

                #Ensures that cards are not added as a list
                for card in cards_in_deck:
                    cards.append(card)


        #Checking if the deck has cards to revise
        if not cards:
            return apology("There are no cards in these decks", 400)
        else:
            #Initialising variables for revision
            random.shuffle(cards)
            session['cards'] = cards
            session['checked'] = False
            session['i'] = 0

            return redirect("/revision")


    return render_template("revision_decks.html", decks=decks, tags=tags)


@app.route("/revision", methods=["GET", "POST"])
@login_required
def revision():

    cards = session['cards']


    while session['i'] < len(cards):

        #If data is posted, the user either wants to check the answer or move on
        if request.method == "POST":
            check = request.form.get("check")

            #If we aren't checking, then we are moving to the next card
            if not check:
                session['checked'] = False
                session['i'] += 1
            else:
                session['checked'] = True


        if session['i'] != len(cards):
            return render_template("revision.html", card=cards[session['i']], checked = session['checked'])
        else:
            #If we've revised every card
            return redirect("/revision_decks")








