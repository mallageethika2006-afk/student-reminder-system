from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

def init_db():
    conn = sqlite3.connect("reminders.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS reminders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                type TEXT,
                due_date TEXT,
                status TEXT)""")
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("reminders.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("reminders.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password! Please try again."

    return render_template("login.html")
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("reminders.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        type_ = request.form["type"]
        due_date = request.form["due_date"]

        c.execute("INSERT INTO reminders (user_id,title,type,due_date,status) VALUES (?,?,?,?,?)",
                  (session["user_id"], title, type_, due_date, "Pending"))

        conn.commit()

    # Get reminders
    c.execute("SELECT * FROM reminders WHERE user_id=?", (session["user_id"],))
    data = c.fetchall()

    reminders = []
    today = datetime.today().date()

    for r in data:
        due = datetime.strptime(r[4], "%Y-%m-%d").date()
        days_left = (due - today).days

        if days_left < 0:
            alert = "Overdue"
        elif days_left <= 2:
            alert = "Due Soon"
        else:
            alert = "Normal"

        reminders.append((r[0], r[1], r[2], r[3], r[4], r[5], alert))

    conn.close()

    return render_template("dashboard.html", reminders=reminders)
@app.route("/complete/<int:id>")
def complete(id):
    conn = sqlite3.connect("reminders.db")
    c = conn.cursor()
    c.execute("UPDATE reminders SET status='Completed' WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("reminders.db")
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    init_db()
import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)