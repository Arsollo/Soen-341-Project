from flask import (
    Flask,
    g,
    app,
    redirect,
    url_for,
    render_template,
    request,
    session
)
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.permanet_session_lifetime = timedelta(days=5)

#check for active session
@app.before_request
def check_session():
    g.user = None
    if "user" in session:
        g.user = session["user"]

#Home Page
@app.route("/")
def home():
    if "user" in session:
        return render_template("mainpage_si.html")
    else:
        return render_template("mainpage_so.html")

#Login Page
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        return render_template("login.html")

#user profile page
@app.route("/profile")
def profile():
    if "user" in session:
        return render_template("profile.html", user=user)
    else:
        print("No username found in session")
        return redirect(url_for("login"))
    
# Homepage after login
@app.route("/user")
def user():
    if "user" in session:
        # user = session["user"]
        return render_template("mainpage_si.html")
    else:
        return redirect(url_for("login"))

# Question Post page
@app.route("/ask/")
def post():
        return render_template("post.html")

@app.route("/logout")
def logout():
    session.pop("userr", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
        app.run(debug=True)