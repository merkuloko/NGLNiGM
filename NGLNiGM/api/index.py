import os
from flask import Flask, render_template, request, jsonify, session, redirect
from supabase import create_client, Client

# Line 5: Corrected underscores and folders
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'pogi_si_gm_default')

# Pulling keys from Vercel Environment Variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Line 12: Added the missing closing parenthesis )
supabase: Client = create_client(url, key)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send_message():
    message_content = request.form.get("message")
    if not message_content:
        return jsonify({"status": "error", "message": "No message provided"}), 400

    try:
        # Saving to Supabase Cloud instead of local SQLite
        supabase.table("anonymous_messages").insert({"content": message_content}).execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Supabase Error: {e}")
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

@app.route("/view-messages-99")
def view_messages():
    if not session.get('admin_logged_in'):
        return '''
            <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
                <form action="/admin-login" method="post">
                    <input type="password" name="password" placeholder="Password?">
                    <button type="submit">Enter</button>
                </form>
            </div>
        '''
    try:
        response = supabase.table("anonymous_messages").select("*").order("timestamp", desc=True).execute()
        return render_template("admin.html", messages=response.data)
    except Exception as e:
        return f"Error fetching messages: {e}"

@app.route("/admin-login", methods=["POST"])
def admin_login():
    if request.form.get("password") == "open-sesame":
        session['admin_logged_in'] = True
        return redirect("/view-messages-99")
    return "Mali password! <a href='/view-messages-99'>Try again</a>"

# Vercel handles the running, but this is kept for local testing
if __name__ == "__main__":
    app.run(port=5000, debug=True)
