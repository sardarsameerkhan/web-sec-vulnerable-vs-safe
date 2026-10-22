import sqlite3
import secrets
from flask import Flask, request, render_template, render_template_string, session

app = Flask(__name__)
app.secret_key = "super_secret_lab_key_2026"

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

@app.route("/")
def index():
    return render_template("index.html")

# --- 1. XSS ROUTES ---
@app.route("/vulnerable/xss/reflected")
def vuln_xss_reflected():
    q = request.args.get("q", "")
    template = f"""
    <h2>Vulnerable Reflected XSS</h2>
    <form method="GET"><input type="text" name="q" value="{q}"><button type="submit">Search</button></form>
    <p>Search Results for: {q}</p>
    <a href="/">Back Home</a>
    """
    return render_template_string(template)

@app.route("/safe/xss/reflected")
def safe_xss_reflected():
    q = request.args.get("q", "")
    return render_template("xss_reflected_safe.html", q=q)

@app.route("/vulnerable/xss/stored", methods=["GET", "POST"])
def vuln_xss_stored():
    conn = get_db_connection()
    if request.method == "POST":
        username = request.form.get("username", "Anonymous")
        comment = request.form.get("comment", "")
        conn.execute("INSERT INTO comments (username, comment) VALUES (?, ?)", (username, comment))
        conn.commit()
    comments = conn.execute("SELECT * FROM comments").fetchall()
    conn.close()
    return render_template("xss_stored_vuln.html", comments=comments)

@app.route("/safe/xss/stored", methods=["GET", "POST"])
def safe_xss_stored():
    conn = get_db_connection()
    if request.method == "POST":
        username = request.form.get("username", "Anonymous")
        comment = request.form.get("comment", "")
        conn.execute("INSERT INTO comments (username, comment) VALUES (?, ?)", (username, comment))
        conn.commit()
    comments = conn.execute("SELECT * FROM comments").fetchall()
    conn.close()
    return render_template("xss_stored_safe.html", comments=comments)

@app.route("/vulnerable/xss/dom")
def vuln_xss_dom():
    return render_template("xss_dom_vuln.html")

@app.route("/safe/xss/dom")
def safe_xss_dom():
    return render_template("xss_dom_safe.html")

# --- 2. CSRF ROUTES ---
@app.route("/vulnerable/csrf/change-email", methods=["GET", "POST"])
def vuln_csrf():
    if "user" not in session:
        session["user"] = "john_doe"
    msg = ""
    if request.method == "POST":
        new_email = request.form.get("email")
        conn = get_db_connection()
        conn.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, session["user"]))
        conn.commit()
        conn.close()
        msg = f"Email updated to {new_email}!"
    return render_template("csrf_vuln.html", msg=msg, user=session["user"])

@app.route("/safe/csrf/change-email", methods=["GET", "POST"])
def safe_csrf():
    if "user" not in session:
        session["user"] = "john_doe"
    msg = ""
    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            return "403 Forbidden: Invalid CSRF Token", 403
        new_email = request.form.get("email")
        conn = get_db_connection()
        conn.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, session["user"]))
        conn.commit()
        conn.close()
        msg = f"Email safely updated to {new_email}!"
    return render_template("csrf_safe.html", msg=msg, user=session["user"])

# --- 3. SQL INJECTION ROUTES ---
@app.route("/vulnerable/sqli/easy", methods=["GET", "POST"])
def vuln_sqli_easy():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = get_db_connection()
        try:
            user = conn.execute(query).fetchone()
            if user:
                msg = f"Logged in as {user['username']} ({user['role']})!"
            else:
                msg = "Invalid credentials."
        except Exception as e:
            msg = f"Database Error: {str(e)}"
        conn.close()
    return render_template("sqli_easy.html", msg=msg)

@app.route("/safe/sqli/easy", methods=["GET", "POST"])
def safe_sqli_easy():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        conn = get_db_connection()
        user = conn.execute(query, (username, password)).fetchone()
        conn.close()
        if user:
            msg = f"Logged in as {user['username']} ({user['role']})!"
        else:
            msg = "Invalid credentials."
    return render_template("sqli_easy.html", msg=msg)

@app.route("/vulnerable/sqli/intermediate")
def vuln_sqli_intermediate():
    user_id = request.args.get("id", "")
    conn = get_db_connection()
    query = f"SELECT id, username, email FROM users WHERE id = {user_id}" if user_id else "SELECT id, username, email FROM users"
    try:
        res = conn.execute(query).fetchall()
        result = [dict(row) for row in res]
    except Exception as e:
        result = f"SQL Syntax Error: {str(e)}"
    conn.close()
    return render_template("sqli_intermediate.html", result=result, user_id=user_id)

@app.route("/safe/sqli/intermediate")
def safe_sqli_intermediate():
    user_id = request.args.get("id", "")
    conn = get_db_connection()
    query = "SELECT id, username, email FROM users WHERE id = ?"
    try:
        if user_id:
            res = conn.execute(query, (user_id,)).fetchall()
        else:
            res = conn.execute("SELECT id, username, email FROM users").fetchall()
        result = [dict(row) for row in res]
    except Exception:
        result = "An error occurred processing your request."
    conn.close()
    return render_template("sqli_intermediate.html", result=result, user_id=user_id)

@app.route("/vulnerable/sqli/advanced")
def vuln_sqli_advanced():
    search = request.args.get("search", "")
    conn = get_db_connection()
    query = f"SELECT id, username, comment FROM comments WHERE comment LIKE '%{search}%'"
    try:
        res = conn.execute(query).fetchall()
        results = [dict(row) for row in res]
    except Exception:
        results = []
    conn.close()
    return render_template("sqli_advanced.html", results=results, search=search)

@app.route("/safe/sqli/advanced")
def safe_sqli_advanced():
    search = request.args.get("search", "")
    conn = get_db_connection()
    query = "SELECT id, username, comment FROM comments WHERE comment LIKE ?"
    try:
        res = conn.execute(query, (f"%{search}%",)).fetchall()
        results = [dict(row) for row in res]
    except Exception:
        results = []
    conn.close()
    return render_template("sqli_advanced.html", results=results, search=search)

if __name__ == "__main__":
    app.run(debug=True, port=5000)