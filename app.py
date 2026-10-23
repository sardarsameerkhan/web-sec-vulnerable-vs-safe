import sqlite3
import os
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "flex_academic_portal_secret_key"

def get_db():
    conn = sqlite3.connect('portal.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Users table (SQLi Level 1 & Level 3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            full_name TEXT,
            role TEXT
        );
    """)
    # 2. Students table (SQLi Level 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT PRIMARY KEY,
            department TEXT,
            name TEXT,
            gpa TEXT
        );
    """)
    # 3. Discussion Board table (Stored XSS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT
        );
    """)
    # 4. Courses table (Reflected XSS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            code TEXT,
            title TEXT
        );
    """)

    # Seed Database if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Default Portal Users
        cursor.execute("INSERT INTO users (username, password, email, full_name, role) VALUES ('admin', 'admin123', 'admin@flex.edu', 'System Administrator', 'Admin');")
        cursor.execute("INSERT INTO users (username, password, email, full_name, role) VALUES ('student1', 'pass123', 'student1@flex.edu', 'Sardar Rehman', 'Student');")
        cursor.execute("INSERT INTO users (username, password, email, full_name, role) VALUES ('sameerkhan', 'pass123', 'f223162@cfd.nu.edu.pk', 'sardar sameer', 'Student');")
        
        # Expanded Student Directory Records
        cursor.execute("INSERT INTO students VALUES (101, 'CS', 'Sardar Rehman', '3.8');")
        cursor.execute("INSERT INTO students VALUES (102, 'CS', 'Salman Khan', '3.5');")
        cursor.execute("INSERT INTO students VALUES (103, 'EE', 'Ali Ahmed', '3.2');")
        cursor.execute("INSERT INTO students VALUES (104, 'SE', 'Zaid Malik', '3.9');")
        cursor.execute("INSERT INTO students VALUES (105, 'ME', 'Hamza Tariq', '3.1');")
        cursor.execute("INSERT INTO students VALUES (106, 'CS', 'Ayesha Khan', '3.7');")

        # Default Courses
        cursor.execute("INSERT INTO courses VALUES (1, 'CS-301', 'Web Security & Software Engineering');")
        cursor.execute("INSERT INTO courses VALUES (2, 'CS-302', 'Database Systems');")
        cursor.execute("INSERT INTO courses VALUES (3, 'EE-201', 'Linear Circuit Analysis');")

        # Default Discussions
        cursor.execute("INSERT INTO discussions (author, content) VALUES ('Dr. Arshad', 'Welcome to the semester discussion board!');")
    
    conn.commit()
    return conn

# Shared persistent database connection instance
db_conn = get_db()

@app.before_request
def initialize_session_defaults():
    if "mode" not in session:
        session["mode"] = "vulnerable"
    if "csrf_token" not in session:
        session["csrf_token"] = "secure_random_token_98765"

@app.route("/toggle-mode/<new_mode>")
def toggle_mode(new_mode):
    if new_mode in ["vulnerable", "safe"]:
        session["mode"] = new_mode
    return redirect(request.referrer or url_for('dashboard'))

# --- AUTHENTICATION & REGISTRATION ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        cursor = db_conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, email, full_name, role) VALUES (?, ?, ?, ?, 'Student')",
                           (username, password, email, full_name))
            db_conn.commit()
            flash("Account registered successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
    return render_template("register.html")

# --- SQLi LEVEL 1: LOGIN MODULE ---
@app.route("/login", methods=["GET", "POST"])
def login():
    executed_query = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        cursor = db_conn.cursor()
        
        if session["mode"] == "vulnerable":
            executed_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            try:
                cursor.execute(executed_query)
                user = cursor.fetchone()
            except Exception as e:
                user = None
                executed_query += f" | DB ERROR: {str(e)}"
        else:
            executed_query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(executed_query, (username, password))
            user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            flash(f"Logged in as {user['full_name']}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html", executed_query=executed_query)

@app.route("/logout")
def logout():
    session.clear()
    flash("Successfully logged out.", "info")
    return redirect(url_for("login"))

@app.route("/")
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# --- SQLi LEVEL 2: STUDENT DIRECTORY SEARCH ---
@app.route("/students", methods=["GET", "POST"])
def students():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    student_records = None
    executed_query = ""
    if request.method == "POST":
        dept = request.form.get("dept", "")
        student_id = request.form.get("student_id", "")
        cursor = db_conn.cursor()

        if session["mode"] == "vulnerable":
            # Direct dynamic string format without type conversion or fallback
            executed_query = f"SELECT * FROM students WHERE department = '{dept}' AND student_id = {student_id}"
            try:
                cursor.execute(executed_query)
                student_records = cursor.fetchall()
            except Exception as e:
                executed_query += f" | DB ERROR: {str(e)}"
        else:
            executed_query = "SELECT * FROM students WHERE department = ? AND student_id = ?"
            cursor.execute(executed_query, (dept, student_id))
            student_records = cursor.fetchall()

    return render_template("students.html", student_records=student_records, executed_query=executed_query)

# --- SQLi LEVEL 3: FORUM RECORDS ADVANCED SEARCH ---
@app.route("/records", methods=["GET", "POST"])
def records():
    if "user_id" not in session:
        return redirect(url_for("login"))

    records_found = None
    executed_query = ""
    if request.method == "POST":
        search_term = request.form.get("search", "")
        cursor = db_conn.cursor()

        if session["mode"] == "vulnerable":
            executed_query = f"SELECT id, username, role FROM users WHERE username LIKE '%{search_term}%'"
            try:
                cursor.execute(executed_query)
                records_found = cursor.fetchall()
            except Exception as e:
                executed_query += f" | DB ERROR: {str(e)}"
        else:
            executed_query = "SELECT id, username, role FROM users WHERE username LIKE ?"
            cursor.execute(executed_query, (f"%{search_term}%",))
            records_found = cursor.fetchall()

    return render_template("records.html", records_found=records_found, executed_query=executed_query)

# --- REFLECTED XSS: COURSE DIRECTORY ---
@app.route("/courses")
def courses():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    search_query = request.args.get("q", "")
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM courses")
    course_list = cursor.fetchall()
    
    raw_html_response = f"<p>Search results for query: <b>{search_query}</b></p>" if search_query else ""
    return render_template("courses.html", courses=course_list, search_query=search_query, raw_html_response=raw_html_response)

# --- STORED XSS: DISCUSSION BOARD ---
@app.route("/forum", methods=["GET", "POST"])
def forum():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db_conn.cursor()
    if request.method == "POST":
        content = request.form.get("content", "")
        if content:
            cursor.execute("INSERT INTO discussions (author, content) VALUES (?, ?)", 
                           (session["full_name"], content))
            db_conn.commit()

    cursor.execute("SELECT * FROM discussions ORDER BY id DESC")
    posts = cursor.fetchall()
    return render_template("forum.html", posts=posts)

# --- DOM XSS: ANNOUNCEMENTS BOARD ---
@app.route("/announcements")
def announcements():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("announcements.html")

# --- CSRF: ACCOUNT PROFILE UPDATE ---
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if session["mode"] == "safe":
            token = request.form.get("csrf_token")
            if not token or token != session.get("csrf_token"):
                return "<h3>403 Forbidden: Missing or Invalid Anti-CSRF Token</h3>", 403

        new_email = request.form.get("email")
        cursor = db_conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, session["user_id"]))
        db_conn.commit()
        session["email"] = new_email
        flash("Email address updated successfully!", "success")

    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)