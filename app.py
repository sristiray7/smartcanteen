from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import sqlite3
import json
from datetime import datetime
import random

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

# Login Page
@app.route("/login")
def login():
    return render_template("login.html")


# Menu Page
@app.route("/menu")
def menu():
    return render_template("menu.html")


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
    return render_template("track_order.html")


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

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", orders=orders)


# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)