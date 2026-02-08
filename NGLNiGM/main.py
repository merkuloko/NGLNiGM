import os
from flask import Flask, render_template, request, jsonify, session, redirect
from supabase import create_client, Client

main = Flask(__name__)
main.secret_key = 'pogi_si_gm_123'

# --- Supabase Config ---
# For Vercel, it is better to use Environment Variables later
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/send", methods=["POST"])
def send_message():
    message_content = request.form.get("message")
    if not message_content:
        return jsonify({"status": "error", "message": "Walang message!"}), 400

    try:
        # Insert into Supabase
        data = supabase.table("anonymous_messages").insert({"content": message_content}).execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@main.route("/view-messages-99")
def view_messages():
    if not session.get('admin_logged_in'):
        return render_template("login.html") # Create a simple login page

    try:
        # Fetch from Supabase, newest first
        response = supabase.table("anonymous_messages").select("*").order("timestamp", desc=True).execute()
        messages = response.data
        return render_template("admin.html", messages=messages)
    except Exception as e:
        return f"Error: {e}"

@main.route("/admin-login", methods=["POST"])
def admin_login():
    if request.form.get("password") == "open-sesame":
        session['admin_logged_in'] = True
        return redirect("/view-messages-99")
    return "Mali password! <a href='/view-messages-99'>Try again</a>"

if __name__ == "__main__":
    main.run(port=5000, debug=True)
