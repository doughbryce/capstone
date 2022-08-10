from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://brycedoughman:mit12@localhost:5432/capstonedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.secret_key
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# form class flask wtforms
class SignupForm(FlaskForm):
    email = StringField('Enter your Email: ', validators=[DataRequired()])
    display_name = StringField('Enter your Display Name: ', validators=[DataRequired()])
    password = PasswordField('Enter a Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


# database creation
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), unique=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(255), nullable=True)
    font = db.Column(db.String(255), nullable=True)

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


db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base', methods=['GET'])
def base():
    return render_template('base.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    email = None
    password = None
    display_name = None
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        display_name = form.display_name.data
        password = form.password.data

        new_user = Users(email=form.email.data, password_hash=form.password.data, display_name=form.display_name.data)
        db.session.add(new_user)
        db.session.commit()

        form.email.data = ''
        form.password.data = ''

        return redirect(url_for('index'))


    return render_template('signup.html',
        email = email,
        display_name = display_name,
        password = password,
        form = form)



if __name__ == "__main__":
    app.run(debug=True)