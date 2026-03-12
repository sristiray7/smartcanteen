from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import datetime
import random
import os 
from dotenv import load_dotenv
from flask import session
load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.secret_key = "super-secret-key"
csrf = CSRFProtect(app)


# ==============================
# DATABASE INITIALIZATION
# ==============================

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT,
            name TEXT,
            mobile TEXT,
            table_no TEXT,
            items TEXT,
            total_price REAL,
            order_time TEXT,
            status TEXT
        )
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

# ==============================
# ROUTES
# ==============================

# Restaurant Homepage
@app.route("/")
def home():
    return render_template("index.html")
#contact page
@app.route("/contact")
def contact():
    return render_template("contact.html")

#---------------user login and admin login routes------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        role = request.form.get("role")
        password = request.form.get("password")

        # ======================
        # ADMIN LOGIN
        # ======================
        if role == "admin":

            email = request.form.get("email")

            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session["admin_logged_in"] = True
                return redirect(url_for("home"))
            else:
                return "Invalid admin credentials"

        # ======================
        # USER LOGIN
        # ======================
        if role == "user":

            mobile = request.form.get("email")

            conn = sqlite3.connect("orders.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE mobile=? AND password=?",
                (mobile, password)
            )

            user = cursor.fetchone()
            conn.close()

            if user:
                return redirect(url_for("home"))
            else:
                return "Invalid mobile or password"

    return render_template("login.html")
#---------------user login and admin login routes------

#------------signup routes-----------
@app.route("/signup", methods=["POST"])
def signup():

    mobile = request.form.get("mobile")
    password = request.form.get("password")

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    # check existing user
    cursor.execute("SELECT * FROM users WHERE mobile=?", (mobile,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return "User already exists"

    cursor.execute(
        "INSERT INTO users (mobile, password) VALUES (?,?)",
        (mobile, password)
    )

    conn.commit()
    conn.close()

    return "Signup successful"
#----------------other routes--------------
@app.route("/mycart")
def mycart():
    return render_template("my_cart.html")
@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")
@app.route("/rewards")
def rewards():
    return render_template("rewards.html")
@app.route("/customer_care")
def customer_care():
    return render_template("customer_care.html")
@app.route("/notification")
def notification():
    return render_template("notification.html")
# Menu Page
@app.route("/menu")
def menu():
    return render_template("menu.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/my_profile")
def my_profile():
    return render_template("my_profile.html")



# ==============================
# PLACE ORDER
# ==============================

@app.route("/place_order", methods=["POST"])
def place_order():

    name = request.form["name"]
    mobile = request.form["mobile"]
    table_no = request.form["table_no"]
    items = request.form.getlist("items")  # list of items
    total_price = request.form["total_price"]

    order_no = "ORD" + str(random.randint(1000, 9999))
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Preparing"

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (order_no, name, mobile, table_no, items, total_price, order_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_no,
        name,
        mobile,
        table_no,
        json.dumps(items),
        total_price,
        order_time,
        status
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("my_order", order_no=order_no))
# ==============================
# ORDER TRACKING PAGE
# ==============================

@app.route("/my_order")
def my_order_page():
    return render_template("myorder.html")


# ==============================
# USER ORDER PAGE
# ==============================

@app.route("/my_order/<order_no>")
def my_order(order_no):

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_no = ?", (order_no,))
    order = cursor.fetchone()

    conn.close()

    if order:
        items = json.loads(order[5])  # decode stored items
        return render_template("myorder.html", order=order, items=items)
    else:
        return "Order not found"


# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", orders=orders)


# ==============================
# RUN APP
# ==============================

# ==============================
# RUN APP
# ==============================

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)