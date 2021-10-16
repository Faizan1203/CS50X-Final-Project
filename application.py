import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///buysell.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/")
def login_begin():
    if session.get("user_id") is None:
        return render_template("login_begin.html")
    else:
        return render_template("home.html")


@app.route("/login_seller", methods=["GET", "POST"])
def login_seller():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login_seller.html")

@app.route("/login_buyer", methods=["GET", "POST"])
def login_buyer():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_type"] = rows[0]["user_type"]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login_buyer.html")

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

    password = request.form.get("password")
    username = request.form.get("username")
    confirmation = request.form.get("confirmation")
    email = request.form.get("email")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confo was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        elif "@" not in email:
            return apology("Invalid Email")

        elif not request.form.get("register-type"):
            return apology("Choose Buyer/Seller")

        register_type = request.form.get("register-type")

        if password != confirmation:
            return apology("Passwords don't match")

        if password == confirmation:

            hashvalue = generate_password_hash(request.form.get("password"))

        try:
            db.execute("INSERT INTO users (username, hash, user_type, email) VALUES (?, ?, ?, ?)"
                       , username, hashvalue, register_type, email)
        except:
            return apology("username already taken", 400)

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/newlistings", methods=["GET", "POST"])
@login_required
def newlistigs():
    if request.method == "POST":
        property_type = request.form.get("property_type")
        price = request.form.get("price")
        property_place = request.form.get("property_place")
        if not property_type:
            return apology("Invalid Type")
        elif not price:
            return apology("Invalid Price")
        elif not property_place:
            return apology("Invalid Place")

        houses = db.execute("SELECT * FROM seller_info WHERE place = ? AND price <= ? AND property_type = ?", property_place, price, property_type)
        if houses is None:
            return apology("NO results found")
        else:
            return render_template("index.html", houses = houses)
    else:
        return render_template("newlistings.html")


@app.route("/upload details", methods=["GET", "POST"])
@login_required
def uploaddetails():
    if request.method == "POST":
        property_type = request.form.get("property_type")
        place = request.form.get("property_place")
        quotation = request.form.get("quotation")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        if not property_type:
            return apology("INVALID PROPERTY TYPE")
        elif not quotation:
            return apology("INVALID QUOTATION")
        elif not place:
            return apology("INVALID PLACE")
        elif not last_name:
            return apology("Must Provide Last Name")

        elif not first_name:
            return apology("Must Provide First Name")

        elif not phone_number:
            return apology("Must Provide Phone Number")

        elif len(phone_number) < 10:
            return apology("Invalid Phone Number")

        db.execute("INSERT INTO seller_info (users_id, property_type, price, place, owner_name, owner_phone) VALUES (?, ?, ? ,?, ?, ?)"
                    , session["user_id"], property_type, quotation , place, first_name, phone_number)

        return redirect("/")
        flash("You have successfully uploaded the details of your property")
    else:
        return render_template("uploaddetails.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)