import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")  
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        flash("Please fill out both fields.")
        return redirect(url_for("index"))

    data = {"name": name, "email": email}

    try:
        response = supabase.table("user").insert(data).execute()

        error = None
        if hasattr(response, "error"):
            error = response.error
        elif isinstance(response, dict) and response.get("error"):
            error = response.get("error")

        if error:
            app.logger.error("Supabase insert error: %s", error)
            flash("Failed to save to database. Check server logs.")
        else:
            flash("Saved successfully!")
    except Exception as e:
        app.logger.exception("Unexpected error inserting to Supabase")
        flash("Unexpected error. See server logs.")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
