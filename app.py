from flask import Flask, request, redirect, render_template, jsonify
import sqlite3
import string
import random

app = Flask(__name__)

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            click_count INTEGER DEFAULT 0
        )
        """)
init_db()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":
        long_url = request.form["long_url"]
        code = generate_code()
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO urls (code, long_url) VALUES (?, ?)", (code, long_url))
        short_url = request.host_url + code
    return render_template("index.html", short_url=short_url)

@app.route("/<code>")
def redirect_to_url(code):
    with sqlite3.connect("database.db") as conn:
        result = conn.execute("SELECT long_url FROM urls WHERE code = ?", (code,)).fetchone()
        if result:
            conn.execute("UPDATE urls SET click_count = click_count + 1 WHERE code = ?", (code,))
            return redirect(result[0])
    return "URL not found", 404

@app.route("/admin")
def admin():
    with sqlite3.connect("database.db") as conn:
        urls = conn.execute("SELECT code, long_url, created_at, click_count FROM urls ORDER BY created_at DESC").fetchall()
    return render_template("admin.html", urls=urls)

@app.route("/chart-data")
def chart_data():
    with sqlite3.connect("database.db") as conn:
        data = conn.execute("SELECT code, click_count FROM urls").fetchall()
    labels = [row[0] for row in data]
    clicks = [row[1] for row in data]
    return jsonify({"labels": labels, "clicks": clicks})