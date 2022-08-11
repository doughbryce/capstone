from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, PasswordField
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://brycedoughman:mit12@localhost:5432/capstonedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.secret_key
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class RegisterForm(FlaskForm):
    email = StringField('Enter your Email: ', validators=[DataRequired()])
    display_name = StringField('Enter your Display Name: ', validators=[DataRequired()])
    password = PasswordField('Enter a Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Enter your Email: ', validators=[DataRequired()])
    password = PasswordField('Enter your Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    question = StringField('Enter your Question: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


# database creation
class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), unique=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(255), nullable=True)
    font = db.Column(db.String(255), nullable=True)

    def get_id(self):
           return (self.user_id)

    def __repr__(self):
        return f'<User {self.user_id}, name - {self.display_name}, email - {self.email}>'


class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), unique=True, nullable=False)
    date_asked = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Question {self.question_id}, date asked - {self.date_asked}, question type - {self.question_type}>'

class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_posted = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(Questions.question_id), nullable=False)

    def __repr__(self):
        return f'<Post {self.post_id}, user posted id - {self.user_posted}, date posted - {self.date}, question id - {self.question_id}>'


class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(Posts.post_id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Comment {self.comment_id}, post - {self.post_id}, user id - {self.user_id}, date - {self.date}>'



class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    
    def __repr__(self):
        return f'<Friend {self.id}, user id - {self.user_id}, friend id - {self.friend_id}>'


class FriendRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    
    def __repr__(self):
        return f'<FriendRequest {self.id}, user id - {self.user_id}, requesting friend id - {self.friend_id}>'


# db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():

    email = None
    password = None
    display_name = None
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        display_name = form.display_name.data
        password = form.password.data

        new_user = Users(email=form.email.data, password_hash=form.password.data, display_name=form.display_name.data)
        db.session.add(new_user)
        db.session.commit()

        form.email.data = ''
        form.password.data = ''

        return redirect(url_for('home'))


    return render_template('register.html',
        email = email,
        display_name = display_name,
        password = password,
        form = form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user:
            if user.password_hash == form.password.data:
                login_user(user)
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))

        return redirect(next or url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', display_name=current_user.display_name)

@app.route('/base', methods=['GET'])
def base():
    return render_template('base.html')

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')

@app.route('/friends', methods=['GET'])
@login_required
def friends():
    return render_template('friends.html')


@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionForm()
    return render_template('add_question.html', form=form)



if __name__ == "__main__":
    app.run(debug=True)