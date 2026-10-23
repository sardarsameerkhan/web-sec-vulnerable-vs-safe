# Dual-Engine Web Application Security Portal

A vulnerable-by-design University Student Portal built with Python (Flask), SQLite, and Bootstrap 5. This application demonstrates 7 core web application vulnerabilities alongside their secure coding remediations, controlled dynamically via a global session-based switcher.

---

## 🛠️ Tech Stack & Architecture
- **Backend:** Python / Flask
- **Database:** SQLite (`portal.db`)
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Security Engine:** Dual-mode architecture
  - **Vulnerable Engine:** Dynamic string concatenation, unescaped Jinja2 output, missing anti-CSRF validation.
  - **Safe Engine:** Parameterized SQL queries, Jinja2 auto-escaping, safe DOM assignment, anti-CSRF token verification.

---

## 🚀 Quick Start & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git](https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git)
   cd web-sec-vulnerable-vs-safe
   python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install flask
python app.py
Test 1: SQL Injection Level 1 (Authentication Bypass)
Target Page: Login (/login)

Objective: Bypass authentication without knowing valid user credentials.

Payload: Username: ' OR '1'='1 | Password: any

Vulnerable Behavior: Grants unauthorized administrative access due to raw string formatting.

Safe Behavior: Rejects input; parameterized placeholders treat the payload as a literal string.

Test 2: SQL Injection Level 2 (Multi-Filter Logic Overriding)
Target Page: Student Directory (/students)

Objective: Override department filters and return all database records.

Payload: Department: CS | Student ID: 101 OR 1=1

Vulnerable Behavior: Evaluates OR 1=1 as TRUE, leaking all student records across departments.

Safe Behavior: Returns 0 records; queries expect exact literal matches for 101 OR 1=1.

Test 3: SQL Injection Level 3 (UNION-Based Data Extraction)
Target Page: Forum Lookup (/records)

Objective: Extract user credentials from secondary database tables.

Payload: ' UNION SELECT id, password, email FROM users --

Vulnerable Behavior: Appends sensitive user passwords and emails directly to public search results.

Safe Behavior: Returns 0 records; blocks query structure expansion.

Test 4: Reflected Cross-Site Scripting (XSS)
Target Page: Course Directory (/courses)

Objective: Execute arbitrary client-side script via URL parameters.

Payload: <script>alert('Reflected XSS Execution Successful!')</script>

Vulnerable Behavior: Displays JavaScript modal alert immediately upon page load.

Safe Behavior: Renders raw text without executing code due to HTML entity auto-escaping.

Test 5: Stored Cross-Site Scripting (XSS)
Target Page: Discussion Board (/forum)

Objective: Permanently store malicious scripts in the database to impact all future visitors.

Payload: <script>alert('Stored XSS: Session Cookie - ' + document.cookie);</script>

Vulnerable Behavior: Script executes automatically on every page refresh for all logged-in users.

Safe Behavior: Stores and renders sanitized text using Jinja2 context-aware escaping.

Test 6: DOM-Based Cross-Site Scripting (XSS)
Target Page: Announcements (/announcements)

Objective: Execute malicious script through client-side DOM manipulation.

Payload URL: http://127.0.0.1:5000/announcements#<img src=x onerror=alert('DOM_XSS_Executed')>

Vulnerable Behavior: Client-side JavaScript writes location hash into unsafe innerHTML sinks.

Safe Behavior: Uses .textContent or innerText to prevent HTML interpretation.

Test 7: Cross-Site Request Forgery (CSRF)
Target Page: Profile Settings (/profile)

Objective: Force an authenticated user to perform unauthorized state-changing actions.

Payload: Unauthenticated POST request from external HTML form.

Vulnerable Behavior: Accepts ambient session cookies and updates profile email without consent.

Safe Behavior: Returns 403 Forbidden due to missing valid Anti-CSRF synchronizer token.