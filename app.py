from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.secret_key = "super-secret-key"
csrf = CSRFProtect(app)


# Restaurant Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Login Page
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

if __name__ == "__main__":
    app.run(debug=True)