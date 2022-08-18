import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, PasswordField, SearchField, TextAreaField
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

class FriendSearchForm(FlaskForm):
    search = StringField('Search by id or display name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddFriendForm(FlaskForm):
    submit = SubmitField('Add Friend')

class RemoveFriendForm(FlaskForm):
    submit = SubmitField('Remove Friend')

class RemoveFriendRequestForm(FlaskForm):
    submit = SubmitField('Remove Request')

class AnswerForm(FlaskForm):
    answer = TextAreaField('Enter your Answer: ', validators=[DataRequired()])
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
        return f'<USER({self.user_id}), NAME({self.display_name}), EMAIL({self.email})>'


class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), unique=True, nullable=False)
    date_asked = db.Column(db.DateTime, nullable=True)
    question_type = db.Column(db.String(255), nullable=True)

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
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id'),
      )
    
    def __repr__(self):
        self_name = Users.query.filter_by(user_id=self.user_id).first().display_name
        friend_name = Users.query.filter_by(user_id=self.friend_id).first().display_name
        return f'<Friend {self.id}, USER ({self_name}({self.user_id})), FRIEND ({friend_name}({self.friend_id}))>'


class FriendRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey(Users.user_id), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id'),
      )
    
    def __repr__(self):
        self_name = Users.query.filter_by(user_id=self.friend_id).first().display_name
        friend_name = Users.query.filter_by(user_id=self.user_id).first().display_name
        return f'<Friend Request {self.id}, USER ({self_name}), REQUESTING FRIEND ({friend_name})>'

class AskedQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    original_id = db.Column(db.Integer, db.ForeignKey(Questions.question_id))
    
    def __repr__(self):
        return f'<Question: {self.question}>'


db.create_all()


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

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    question = AskedQuestions.query.order_by(AskedQuestions.id.desc()).first()
    answer = Posts.query.filter(Posts.user_posted == current_user.user_id).order_by(Posts.date.desc()).first()
    friends = Friends.query.filter_by(user_id=current_user.user_id).all()
    friends.append(Friends.query.filter_by(friend_id=current_user.user_id).all())
    friends = [friends[0]]
    posts = []
    display_names = []
    # for friend in friends:
    #     display_names.append(Users.query.filter_by(user_id=friend.user_id).first().display_name)
    #     post = Posts.query.filter_by(user_posted=friend.user_id).first().content
    #     posts.append(post)
    length = len(friends)
    return render_template('home.html', 
        display_name=current_user.display_name,
        display_names=display_names,
        question=question,
        answer=answer,
        friends=friends,
        posts=posts,
        length=length)

@app.route('/answer', methods=['GET', 'POST'])
@login_required
def answer():
    form = AnswerForm()
    question = AskedQuestions.query.order_by(AskedQuestions.id.desc()).first()
    if form.validate_on_submit():
        answer = form.answer.data
        new_post = Posts(user_posted=current_user.user_id, content=answer, date=datetime.datetime.now(), question_id=question.original_id)
        db.session.add(new_post)
        db.session.commit()
        form.answer.data = ''
        return redirect(url_for('home'))
    return render_template('answer.html', 
        form=form, 
        question=question)

@app.route('/base', methods=['GET'])
def base():
    return render_template('base.html')

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html',
        display_name = current_user.display_name,
        email = current_user.email,
        user_id = current_user.user_id,)

@app.route('/friends', methods=['GET'])
@login_required
def friends():
    form = AddFriendForm()
    form2 = RemoveFriendForm()
    form3 = RemoveFriendRequestForm()
    list_of_friends = Friends.query.filter_by(user_id=current_user.user_id).all()
    list_of_friends.extend(Friends.query.filter_by(friend_id=current_user.user_id).all())
    received_requests = FriendRequests.query.filter_by(friend_id=current_user.user_id).all()
    sent_requests = FriendRequests.query.filter_by(user_id=current_user.user_id).all()
    return render_template('friends.html',
        form=form,
        form2=form2,
        form3=form3,
        list_of_friends=list_of_friends,
        received_requests=received_requests, 
        sent_requests=sent_requests)

@app.route('/search_friends', methods=['GET', 'POST'])
@login_required
def search_friends():
    form = FriendSearchForm()
    form2 = AddFriendForm()
    if form.validate_on_submit():
        term = form.search.data 
        list_of_friends = Friends.query.filter_by(user_id=current_user.user_id).all()
        list_of_friends.extend(Friends.query.filter_by(friend_id=current_user.user_id).all())
        list_of_users = []
        for friend in list_of_friends:
            list_of_users.extend(Users.query.filter_by(user_id=friend.friend_id).all())
            list_of_users.extend(Users.query.filter_by(user_id=friend.user_id).all())
        list_of_users = set(list_of_users)
        search_results = Users.query.filter_by(display_name=term).all()
        for friend in search_results:
            if friend in list_of_users:
                search_results.remove(friend)
        return render_template('search_friends.html', 
        form=form,
        form2=form2,
        term = term,
        search_results = search_results)
    return render_template('search_friends.html', form=form, form2=form2)

@app.route('/friend_request_sent/<id>', methods=['GET', 'POST'])
@login_required
def friend_request_sent(id):
    form = FriendSearchForm()
    form2 = AddFriendForm()
    if form2.validate_on_submit():
        new_friend_request = FriendRequests(user_id=current_user.user_id, friend_id=id)
        db.session.add(new_friend_request)
        db.session.commit()
        return redirect(url_for('friends'))
    return render_template('search_friends.html', form=form, form2=form2)

@app.route('/add_friend/<id>', methods=['GET', 'POST'])
@login_required
def add_friend(id):
    form = AddFriendForm()
    form2 = RemoveFriendForm()
    new_friend = Friends(user_id=current_user.user_id, friend_id=id)
    friend_request = FriendRequests.query.filter_by(user_id=id, friend_id=current_user.user_id).first()
    db.session.add(new_friend)
    db.session.delete(friend_request)
    db.session.commit()
    render_template('friends.html', form=form, form2=form2)
    return redirect(url_for('friends'))

@app.route('/remove_friend/<id>', methods=['GET', 'POST'])
@login_required
def remove_friend(id):
    form2 = RemoveFriendForm()
    friend_to_remove1 = Friends.query.filter_by(user_id=id, friend_id=current_user.user_id).first()
    friend_to_remove2 = Friends.query.filter_by(user_id=current_user.user_id, friend_id=id).first()
    if friend_to_remove1:
        db.session.delete(friend_to_remove1)
    elif friend_to_remove2:
        db.session.delete(friend_to_remove2)
    db.session.commit()
    render_template('friends.html', form2=form2)
    return redirect(url_for('friends'))

@app.route('/remove_friend_request/<id>', methods=['GET', 'POST'])
@login_required
def remove_friend_request(id):
    form3 = RemoveFriendRequestForm()
    friend_request_to_remove = FriendRequests.query.filter_by(user_id=id, friend_id=current_user.user_id).first()
    db.session.delete(friend_request_to_remove)
    db.session.commit()
    render_template('friends.html', form3=form3)
    return redirect(url_for('friends'))


@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionForm()
    success = False
    if form.validate_on_submit():
        new_question = Questions(question=form.question.data)
        db.session.add(new_question)
        db.session.commit()
        form.question.data = ''
        success = True
    return render_template('add_question.html', form=form, success=success)


if __name__ == "__main__":
    app.run(debug=True)