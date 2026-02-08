from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
import os

main = Flask(__name__)
main.secret_key = 'pogi_si_gm_123' # Required for session/cookies
DB_NAME = "messages.db"

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anonymous_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the DB on startup
init_db()

@main.route("/")
def home():
    return render_template("index.html")

# --- THIS WAS MISSING (The fix for your 404 error) ---
@main.route("/send", methods=["POST"])
def send_message():
    message_content = request.form.get("message")
    if not message_content:
        return jsonify({"status": "error", "message": "No message provided"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO anonymous_messages (content) VALUES (?)", (message_content,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ADMIN ROUTES ---
@main.route("/view-messages-99")
def view_messages():
    # Check if the user is "logged in" via session
    if not session.get('admin_logged_in'):
        return '''
            <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
                <h2>Admin Login</h2>
                <form action="/admin-login" method="post">
                    <input type="password" name="password" placeholder="Password?" style="padding:10px; border-radius:5px; border:1px solid #ccc;">
                    <button type="submit" style="padding:10px 20px; cursor:pointer;">Enter</button>
                </form>
            </div>
        '''

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT content, timestamp FROM anonymous_messages ORDER BY id DESC")
    messages = cursor.fetchall()
    conn.close()
    return render_template("admin.html", messages=messages)

@main.route("/admin-login", methods=["POST"])
def admin_login():
    if request.form.get("password") == "open-sesame":
        session['admin_logged_in'] = True
        return redirect("/view-messages-99")
    return "Mali password mo, lods. <a href='/view-messages-99'>Try again</a>"

if __name__ == "__main__":
    main.run(port=5000, debug=True)