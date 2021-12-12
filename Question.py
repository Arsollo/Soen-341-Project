#Main python file responsible of the following tasks:
#   - Redirecting Users across the different pages of the website
#   - Updating and accessing the different databases to submit and retrieve information
#   - Controlling several HTML & CSS functionalites depending on User behaviour


#Important imports
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect,request
from flask_login import UserMixin, current_user, login_required, login_user, logout_user, LoginManager
from sqlalchemy.orm import query
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from forms import ProfileForm, RegistrationForm, LoginForm

#Setting-up the different functionalities
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

#Database class for the users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    questions = db.relationship('Question', backref='author', lazy=True)
  

################# Hash the password, feature #########################
    # @property
    # def user_password(self):
    #     raise AttributeError('Cannot view unhashed password!')

    # @user_password.setter
    # def user_password(self, user_password):
    #     self.password = generate_password_hash(user_password)

#Database class for the questions
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q_text = db.Column(db.Text)
    asked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_time = db.Column(db.DateTime)
    solved = db.Column(db.Boolean)
    answers = db.relationship('Answer', backref='question', lazy = True)

#Database class for the answers
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    a_text = db.Column(db.Text)
    answered_by_id = db.Column(db.String, db.ForeignKey('user.username'))
    answer_to = db.Column(db.Integer, db.ForeignKey('question.id'))
    post_time = db.Column(db.DateTime)
    votes = db.Column(db.Integer)
    voted_best = db.Column(db.Boolean)

#Database class for the votes
class Votes (db.Model):
    id = id = db.Column(db.Integer, primary_key=True)
    voted_by_id = db.Column(db.String, db.ForeignKey('user.id'))
    voted_on = db.Column(db.Integer, db.ForeignKey('answer.id'))

#cerating and updating the databases
db.create_all()
db.session.commit()

#Acknowledge current user accessing the website
@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(int(user_id))

login_manager.login_view = "login"




#**************************** Home/default page route ****************************#
@app.route("/home/")
@app.route("/")
def home():
    questions = Question.query.all()
    users = User.query.all()
    context = {
        'questions' : questions,
        'users' : users
    }
    return render_template('home.html', **context)




#**************************** About/Contact-us page route ****************************#
@app.route("/about/")
def about():
    return render_template('about.html', title='About')




#**************************** Registration page route ****************************#
@app.route("/register/", methods=['GET', 'POST'])
def register():
    #If user is logged-in -> skip
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()

    #If user submits form properly -> submit form & redirect to home page
    if form.validate_on_submit() and request.method =='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username = username, email = email, password = password)
        if User.query.filter_by(email=email).first() !=None:
            flash(f'Already a user? Sign in now')
            return redirect(url_for('login'))
        else:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)





#**************************** Login page route ****************************#
@app.route("/login/", methods=['GET', 'POST'])
def login(): 
    form = LoginForm()

    #If user enter the right account info --> redirect to home page & acknowledge his sign-in
    if form.validate_on_submit() and request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not (password==user.password):
            flash(u'Login Unsuccessful. Please check username and password', 'error')
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)





#**************************** User Profile page route ****************************#
@app.route("/profile")
@login_required
def profile():
        #Display the questions asked by user on the page 
        user = current_user
        email = user.email
        user_name = user.username
        user_id = user.id
        user_password = user.password
        questions = Question.query.filter_by(asked_by_id = user_id)
        context = {
            'questions' : questions,
            'email' : email,
            'user_name' : user_name,
            'user_password' : user_password
            }
        return render_template("profile.html", **context)




#**************************** Ask page route ****************************#
@app.route("/ask/", methods=['GET', 'POST'])
@login_required
def ask():
    #when suer submits an answer -> save Question to database & redirect to home 
    if request.method == 'POST':
        question = request.form['question']
        question = Question(
            q_text = question, 
            asked_by_id =current_user.id,
            post_time = datetime.now(),
            solved = False
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('ask.html')




#**************************** Answers to a specific question View page route ****************************#
@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
#There is 3 different scenarios handled on this page:
#   - User submits a new answer to the question
#   - User (who has to be the owner of the question) selects the best answer
#   - User votes Up/Down on an answer
#   Important Note: The answers are sorted by votes on this page (also handled in this function)

def question(question_id):
    question = Question.query.get_or_404(question_id)
    question_id = question.id

    #If form is submitted by clicking one of the buttons
    if request.method == 'POST' and Answer.query.all()!= None:

        #If an answer is submitted by user
        if request.form.get("answer"):
            answer = request.form['answer']
            answer = Answer(
                a_text = answer, 
                answered_by_id = current_user.username,
                answer_to = question_id, 
                post_time = datetime.now(), 
                votes = 0,
                voted_best = False
            )
            db.session.add(answer)
            db.session.commit()
            return redirect(url_for('answer', question_id=question_id))

        #if the solved button is pressed    
        elif request.form.get("solved"):
            answer_id = request.form.get("solved")
            current_answer = Answer.query.get_or_404(answer_id)
            current_answer.voted_best = True
            question.solved = True
            db.session.commit()
            return redirect(url_for('answer', question_id=question_id))


        #if the Upvote button is pressed
        elif request.form.get("voteUp"):
            answer_id = request.form['voteUp']
            current_answer = Answer.query.get_or_404(answer_id)
            voted_by_user = Votes.query.filter_by(voted_by_id = current_user.id, voted_on = answer_id).first()

            #check if user has voted already. If not, user vote can be captured
            if voted_by_user == None:
                voted_by_user = True
                #current_answer = Answer.query.get_or_404(answer_id)
                current_answer.votes = (current_answer.votes + 1)
                vote_pressed = Votes(voted_by_id = current_user.id, 
                    voted_on = answer_id)
                db.session.add(vote_pressed)
                db.session.commit()

                #sorting answers according to number of votes
                q1 = Answer.query.filter_by(answer_to=question_id)
                q1.all()
                q1.order_by(Answer.votes).all()
                answers = q1.order_by(Answer.votes.desc()).all()
                context = {
                'question' : question,
                'current_answer' : current_answer,
                'answers' : answers
                }
                return render_template( 'question_view.html', voted_by_user = False, question_id=question_id, **context)  

            else:
                voted_by_user = True

                #sorting answers according to number of votes
                q1 = Answer.query.filter_by(answer_to=question_id)
                q1.all()
                q1.order_by(Answer.votes).all()
                answers = q1.order_by(Answer.votes.desc()).all()
                context = {
                'question' : question,
                'current_answer' : current_answer,
                'answers' : answers
                }
                return render_template( 'question_view.html', voted_by_user = voted_by_user, question_id=question_id, **context)  

            

        #if the DownVote button is pressed
        elif request.form.get("voteDown"):
            answer_id = request.form['voteDown']
            current_answer = Answer.query.get_or_404(answer_id)
            voted_by_user = Votes.query.filter_by(voted_by_id = current_user.id, voted_on = answer_id).first()

            #check if user has voted already. If not, user vote can be captured
            if voted_by_user == None:
                voted_by_user = True
                current_answer = Answer.query.get_or_404(answer_id)
                current_answer.votes = (current_answer.votes - 1)
                vote_pressed = Votes(voted_by_id = current_user.id, 
                    voted_on = answer_id)
                db.session.add(vote_pressed)
                db.session.commit()

                #sorting answers according to number of votes
                q1 = Answer.query.filter_by(answer_to=question_id)
                q1.all()
                q1.order_by(Answer.votes).all()
                answers = q1.order_by(Answer.votes.desc()).all()
                context = {
                'question' : question,
                'current_answer' : current_answer,
                'answers' : answers
                }
                return render_template( 'question_view.html', voted_by_user = False, question_id=question_id, **context)

            else:
                voted_by_user = True

                #sorting answers according to number of votes
                q1 = Answer.query.filter_by(answer_to=question_id)
                q1.all()
                q1.order_by(Answer.votes).all()
                answers = q1.order_by(Answer.votes.desc()).all()
                context = {
                'question' : question,
                'current_answer' : current_answer,
                'answers' : answers
                }
                return render_template( 'question_view.html', voted_by_user = voted_by_user, question_id=question_id, **context)

        else:
            answers = Answer.query.filter_by(answer_to=question_id).all()
            context = {
            'question' : question,
            'answers' : answers
            }
            return render_template( 'question_view.html', **context)   


    else:
        answers = Answer.query.filter_by(answer_to=question_id).all()
        context = {
        'question' : question,
        'answers' : answers
        }
        return render_template( 'question_view.html', **context)       




#**************************** reroute when there is a change to the question page to prevent new entries on refresh ****************************#
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




#**************************** Logout page route ****************************#
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))




#**************************** Edit User Profile page(Account Info) route #1 ****************************#
#This function is simply to redirect to edit_profile.html
@app.route("/edit_user_profile/")
def edit_user_profile():
    form = ProfileForm()
    user = current_user
    email = user.email
    username = user.username
    password = user.password
    context = {
        'email' : email,
        'user_name' : username,
        'user_password' : password
        }
    return render_template('edit_profile.html', **context, form = form)

#**************************** Edit User Profile page(Account Info) route #2 ****************************#
#This function allows user to modify their login info & redirect to user profile page
@app.route("/update_user_profile/", methods=['POST'])
def update_user_profile():
    user_to_update = current_user
    form = ProfileForm()
    if form.validate_on_submit() and request.method =='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_to_update.username = username
        user_to_update.email = email
        user_to_update.password = password
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('edit_user_profile'))






#**************************** Edit User Profile page(Questions asked) route #1 ****************************#
#This function is simply to redirect to edit_quesitons.html
@app.route("/go_to_edit_questions/")
def go_to_edit_questions():
    user = current_user
    questions = Question.query.filter_by(asked_by_id = user.id)
    context = {
        'questions' : questions
        }
    return render_template("edit_questions.html", **context)

#**************************** Edit User Profile page(Questions asked) route #2 ****************************#
#This function allows user to delete a previously asked question then redirect to User profile page
@app.route("/edit_questions/", methods=['POST'])
def edit_questions():
    user = current_user
    questions = Question.query.filter_by(asked_by_id = user.id)
    context = {
        'questions' : questions
        }
    if request.method =='POST':
        question_id = request.form['question_id']

        question_to_delete = Question.query.get_or_404(question_id)
        db.session.delete(question_to_delete)
        db.session.commit()
        return render_template("edit_questions.html", **context)





if __name__ == '__main__':
    app.run(debug=True)
