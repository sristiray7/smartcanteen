from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import json
from datetime import datetime
import random
import os
from dotenv import load_dotenv
from flask import session

load_dotenv()


UPLOAD_FOLDER      = "app/static/assets/images/menu_items"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

@app.context_processor
def inject_admin():
    return dict(admin_logged_in=session.get("admin_logged_in", False))

app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
csrf = CSRFProtect(app)


# ==============================
# DATABASE INITIALIZATION
# ==============================

def init_db():
    conn   = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no    TEXT,
            name        TEXT,
            mobile      TEXT,
            table_no    TEXT,
            items       TEXT,
            total_price REAL,
            order_time  TEXT,
            status      TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile   TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            category       TEXT NOT NULL,
            price          REAL NOT NULL,
            image_filename TEXT,
            created_at     TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            item_id  INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id),
            UNIQUE(user_id, item_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id),
            UNIQUE(user_id, item_id)
        )
    """)

    conn.commit()
    conn.close()


# ==============================
# HELPERS
# ==============================

def get_db():
    """Returns a DB connection with dict-like rows."""
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_user_id():
    """
    Returns the logged-in user's ID, or None.
    Admin sessions have logged_in=True but NO user_id — this keeps them separate.
    """
    return session.get("user_id")

def user_required():
    """
    Call at the top of any route that needs a real user (not admin).
    Returns a redirect Response if not logged in as user, else None.
    """
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return None


# ==============================
# BASIC ROUTES
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/my_profile")
def my_profile():
    return render_template("my_profile.html")

@app.route("/rewards")
def rewards():
    return render_template("rewards.html")

@app.route("/customer_care")
def customer_care():
    return render_template("customer_care.html")

@app.route("/notification")
def notification():
    return render_template("notification.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ==============================
# AUTH
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("home"))

    if request.method == "POST":
        role     = request.form.get("role")
        password = request.form.get("password")

        if role == "admin":
            email = request.form.get("admin_email")
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session["admin_logged_in"] = True
                session["logged_in"]       = True
                # NOTE: user_id is intentionally NOT set for admin
                return redirect(url_for("home"))
            return "Invalid admin credentials"

        if role == "user":
            mobile = request.form.get("user_mobile")
            conn   = get_db()
            user   = conn.execute(
                "SELECT * FROM users WHERE mobile=? AND password=?",
                (mobile, password)
            ).fetchone()
            conn.close()

            if user:
                session["logged_in"]   = True
                session["user_mobile"] = mobile
                session["user_id"]     = user["id"]   # only set for real users
                return redirect(url_for("home"))
            return "Invalid mobile or password"

    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    mobile   = request.form.get("mobile")
    password = request.form.get("password")

    conn   = get_db()
    exists = conn.execute("SELECT id FROM users WHERE mobile=?", (mobile,)).fetchone()

    if exists:
        conn.close()
        return "User already exists"

    conn.execute("INSERT INTO users (mobile, password) VALUES (?,?)", (mobile, password))
    conn.commit()
    conn.close()
    return "Signup successful"


# ==============================
# MENU
# ==============================

@app.route("/menu")
def menu():
    success = request.args.get("success")
    conn    = get_db()
    rows    = conn.execute(
        "SELECT * FROM menu_items ORDER BY category, name"
    ).fetchall()
    conn.close()

    items = [{
        'id':             r['id'],
        'name':           r['name'],
        'category':       r['category'],
        'price':          r['price'],
        'image_filename': r['image_filename']
    } for r in rows]

    # Only fetch wishlist/cart sets for real users (not admin, not guests)
    wishlist_ids = set()
    cart_ids     = set()
    user_id      = get_user_id()   # None for admin or unauthenticated visitors

    if user_id:
        conn  = get_db()
        wrows = conn.execute(
            "SELECT item_id FROM wishlist WHERE user_id=?", (user_id,)
        ).fetchall()
        crows = conn.execute(
            "SELECT item_id FROM cart WHERE user_id=?", (user_id,)
        ).fetchall()
        conn.close()
        wishlist_ids = {r["item_id"] for r in wrows}
        cart_ids     = {r["item_id"] for r in crows}

    return render_template(
        "menu.html",
        menu_items=items,
        success=success,
        wishlist_ids=wishlist_ids,
        cart_ids=cart_ids
    )


# ==============================
# CART ROUTES
# ==============================

@csrf.exempt
@app.route("/cart/add/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    if not get_user_id():
        return jsonify({"success": False, "redirect": url_for("login")}), 401

    user_id  = get_user_id()
    conn     = get_db()
    existing = conn.execute(
        "SELECT id, quantity FROM cart WHERE user_id=? AND item_id=?",
        (user_id, item_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE cart SET quantity=? WHERE user_id=? AND item_id=?",
            (existing["quantity"] + 1, user_id, item_id)
        )
    else:
        conn.execute(
            "INSERT INTO cart (user_id, item_id, quantity) VALUES (?,?,1)",
            (user_id, item_id)
        )

    conn.commit()
    conn.close()
    return jsonify({"success": True, "redirect": url_for("mycart")})


@csrf.exempt
@app.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    if not get_user_id():
        return jsonify({"success": False}), 401

    conn = get_db()
    conn.execute(
        "DELETE FROM cart WHERE user_id=? AND item_id=?",
        (get_user_id(), item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@csrf.exempt
@app.route("/cart/update/<int:item_id>", methods=["POST"])
def update_cart(item_id):
    if not get_user_id():
        return jsonify({"success": False}), 401

    qty     = int(request.json.get("quantity", 1))
    user_id = get_user_id()
    conn    = get_db()

    if qty <= 0:
        conn.execute(
            "DELETE FROM cart WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        )
    else:
        conn.execute(
            "UPDATE cart SET quantity=? WHERE user_id=? AND item_id=?",
            (qty, user_id, item_id)
        )

    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/mycart")
def mycart():
    guard = user_required()
    if guard: return guard

    user_id = get_user_id()
    conn    = get_db()
    rows    = conn.execute("""
        SELECT m.id, m.name, m.price, m.image_filename, c.quantity
        FROM cart c
        JOIN menu_items m ON c.item_id = m.id
        WHERE c.user_id = ?
    """, (user_id,)).fetchall()
    conn.close()

    cart_items = [{
        "id":             r["id"],
        "name":           r["name"],
        "price":          r["price"],
        "image_filename": r["image_filename"],
        "quantity":       r["quantity"],
        "subtotal":       r["price"] * r["quantity"]
    } for r in rows]

    subtotal = sum(i["subtotal"] for i in cart_items)
    delivery = 40 if subtotal > 0 else 0
    total    = subtotal + delivery

    return render_template(
        "my_cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        delivery=delivery,
        total=total
    )


# ==============================
# WISHLIST ROUTES
# ==============================

@csrf.exempt
@app.route("/wishlist/toggle/<int:item_id>", methods=["POST"])
def toggle_wishlist(item_id):
    if not get_user_id():
        return jsonify({"success": False, "redirect": url_for("login")}), 401

    user_id  = get_user_id()
    conn     = get_db()
    existing = conn.execute(
        "SELECT id FROM wishlist WHERE user_id=? AND item_id=?",
        (user_id, item_id)
    ).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM wishlist WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        )
        added = False
    else:
        conn.execute(
            "INSERT INTO wishlist (user_id, item_id) VALUES (?,?)",
            (user_id, item_id)
        )
        added = True

    conn.commit()
    conn.close()
    return jsonify({
        "success":  True,
        "added":    added,
        "redirect": url_for("wishlist") if added else None
    })


@csrf.exempt
@app.route("/wishlist/remove/<int:item_id>", methods=["POST"])
def remove_from_wishlist(item_id):
    if not get_user_id():
        return jsonify({"success": False}), 401

    conn = get_db()
    conn.execute(
        "DELETE FROM wishlist WHERE user_id=? AND item_id=?",
        (get_user_id(), item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@csrf.exempt
@app.route("/wishlist/move-to-cart/<int:item_id>", methods=["POST"])
def move_to_cart(item_id):
    if not get_user_id():
        return jsonify({"success": False}), 401

    user_id  = get_user_id()
    conn     = get_db()
    existing = conn.execute(
        "SELECT id, quantity FROM cart WHERE user_id=? AND item_id=?",
        (user_id, item_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE cart SET quantity=? WHERE user_id=? AND item_id=?",
            (existing["quantity"] + 1, user_id, item_id)
        )
    else:
        conn.execute(
            "INSERT INTO cart (user_id, item_id, quantity) VALUES (?,?,1)",
            (user_id, item_id)
        )

    conn.execute(
        "DELETE FROM wishlist WHERE user_id=? AND item_id=?",
        (user_id, item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "redirect": url_for("mycart")})


@app.route("/wishlist")
def wishlist():
    guard = user_required()
    if guard: return guard

    user_id = get_user_id()
    conn    = get_db()
    rows    = conn.execute("""
        SELECT m.id, m.name, m.price, m.image_filename
        FROM wishlist w
        JOIN menu_items m ON w.item_id = m.id
        WHERE w.user_id = ?
    """, (user_id,)).fetchall()
    conn.close()

    wish_items = [{
        "id":             r["id"],
        "name":           r["name"],
        "price":          r["price"],
        "image_filename": r["image_filename"]
    } for r in rows]

    return render_template("wishlist.html", wish_items=wish_items)


# ==============================
# ADMIN MENU MANAGEMENT
# ==============================

@app.route("/api/admin/menu/add", methods=["POST"])
def add_menu_item():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    name     = request.form.get("name")
    category = request.form.get("category")
    price    = request.form.get("price")
    file     = request.files.get("image")

    image_filename = None
    if file and file.filename != "":
        if allowed_file(file.filename):
            filename       = secure_filename(file.filename)
            timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename       = timestamp + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

    conn       = get_db()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO menu_items (name, category, price, image_filename, created_at)
        VALUES (?,?,?,?,?)
    """, (name, category, float(price), image_filename, created_at))
    conn.commit()
    conn.close()
    return redirect(url_for("menu", success="Menu item added successfully"))


@csrf.exempt
@app.route("/api/admin/menu/delete/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        conn   = get_db()
        result = conn.execute(
            "SELECT image_filename FROM menu_items WHERE id=?", (item_id,)
        ).fetchone()

        if result and result["image_filename"]:
            path = os.path.join(app.config['UPLOAD_FOLDER'], result["image_filename"])
            if os.path.exists(path):
                os.remove(path)

        conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/menu/items", methods=["GET"])
def get_menu_items():
    try:
        conn  = get_db()
        rows  = conn.execute(
            "SELECT id, name, category, price, image_filename FROM menu_items ORDER BY id DESC"
        ).fetchall()
        conn.close()

        items = [{
            "id":        r["id"],
            "name":      r["name"],
            "category":  r["category"],
            "price":     r["price"],
            "image_url": f"/static/assets/images/menu_items/{r['image_filename']}" if r["image_filename"] else None
        } for r in rows]

        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==============================
# ORDERS
# ==============================

@app.route("/place_order", methods=["POST"])
def place_order():
    name        = request.form["name"]
    mobile      = request.form["mobile"]
    table_no    = request.form["table_no"]
    items       = request.form.getlist("items")
    total_price = request.form["total_price"]

    order_no   = "ORD" + str(random.randint(1000, 9999))
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("""
        INSERT INTO orders (order_no, name, mobile, table_no, items, total_price, order_time, status)
        VALUES (?,?,?,?,?,?,?,?)
    """, (order_no, name, mobile, table_no, json.dumps(items), total_price, order_time, "Preparing"))
    conn.commit()
    conn.close()
    return redirect(url_for("my_order", order_no=order_no))


@app.route("/my_order")
def my_order_page():
    return render_template("myorder.html")


@app.route("/my_order/<order_no>")
def my_order(order_no):
    conn  = get_db()
    order = conn.execute(
        "SELECT * FROM orders WHERE order_no=?", (order_no,)
    ).fetchone()
    conn.close()

    if order:
        items = json.loads(order["items"])
        return render_template("myorder.html", order=order, items=items)
    return "Order not found"


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn   = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("dashboard.html", orders=orders)


# ==============================
# RUN
# ==============================

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)