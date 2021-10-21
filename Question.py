from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect,request
from flask_login import current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q_text = db.Column(db.Text)
    asked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_time = db.Column(db.DateTime)
    solved = db.Column(db.Boolean)
    answers = db.relationship('Answer', backref='question', lazy = True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    a_text = db.Column(db.Text)
    answered_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_to = db.Column(db.Integer, db.ForeignKey('question.id'))
    post_time = db.Column(db.DateTime)
    votes = db.Column(db.Integer)
    voted_best = db.Column(db.Boolean)

db.create_all()
db.session.commit()


##class Post(db.Model):
##    id = db.Column(db.Integer, primary_key=True)
####  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
##   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

##    def __repr__(self):
##        return f"Post('{self.title}', '{self.date_posted}')"


##posts = [
  ##  {
  ##      'author': 'Corey Schafer',
  ##      'title': 'Blog Post 1',
  ##      'content': 'First post content',
  ##      'date_posted': 'April 20, 2018'
  ##  },
  ##  {
  ##      'author': 'Jane Doe',
  ##      'title': 'Blog Post 2',
  ##      'content': 'Second post content',
   ##     'date_posted': 'April 21, 2018'
   ## }
##]


@app.route("/home/")
def home():
    questions = Question.query.all()

    context = {
        'questions' : questions
    }

    return render_template('home.html', **context)


@app.route("/about/")
def about():
    return render_template('about.html', title='About')

#Registration page route
@app.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

#Login page route
@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method=='POST':
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#user profile page
@app.route("/profile")
#@login_required
def profile():
        return render_template("profile.html")

# Question Post page route
#placeholder for user ID included
@app.route("/ask/", methods=['GET', 'POST'])
#@login_required
def ask():
    if request.method == 'POST':
        question = request.form['question']

        question = Question(
            q_text = question, 
            asked_by_id =1,
            post_time = datetime.now(),
            solved = False
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('ask.html')

#Question/Answer view page
#placeholder for user ID included
@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
#@login_required
def question(question_id):
        question = Question.query.get_or_404(question_id)
        question_id = question.id
        if request.method == 'POST' and Answer.query.all()!= None:
            answer = request.form['answer']
            answer = Answer(
                a_text = answer, 
                answered_by_id = 2,
                answer_to = question_id, 
                post_time = datetime.now(), 
                votes = 0, 
                voted_best = False
            )
            db.session.add(answer)
            db.session.commit()

            return redirect(url_for('answer', question_id=question_id))
        else:
            answers = Answer.query.filter_by(answer_to=question_id).all()
            context = {
            'question' : question,
            'answers' : answers
            }
            return render_template( 'question_view.html', **context)
    
            

@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
def answer(question_id):
    question = Question.query.get_or_404(question_id)
    question_id = question.id
    answers = Answer.query.filter_by(answer_to=question_id).all()
    context = {
            'question' : question,
            'answers' : answers
    }
    return render_template('question_view.html', **context)


# #Login Page
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
#         user = request.form["username"]
#         session["user"] = user
#         return redirect(url_for("user"))
#     else:
#         return render_template("login.html")

# #Profile Page
# @app.route("/profile")
# @login_required
# def profile():
#     return render_template("profile.html")
    
    
# # Homepage after login
# @app.route("/user")
# def user():
#     if "user" in session:
#         # user = session["user"]
#         return render_template("mainpage_si.html")
#     else:
#         return redirect(url_for("login"))


# @app.route("/logout")
# @login_required
# def logout():
#     session.pop("userr", None)
#     return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)