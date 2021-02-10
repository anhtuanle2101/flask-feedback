from flask import Flask, redirect, render_template, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from secret import APP_SECRET
from forms import UserForm, LoginForm
from models import db, User, connect_db, Feedback
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

app.config['SECRET_KEY'] = APP_SECRET

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


debug = DebugToolbarExtension(app)
connect_db(app)
db.create_all()

@app.route('/')
def home():
    return redirect('/register')

@app.route('/users/<username>')
def show_info(username):
    if 'user_name' in session:
        user = User.query.filter(User.username == username).first()
        return render_template('user.html', user=user)
    else:
        flash('Please log in first!', 'info')
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors = ['Duplicated username']
            return render_template('register.html', form=form)
        session['user_name'] = user.username
        return redirect('/secret')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticating(username=username, password=password)
        if user:
            flash('Signed in successfully!', 'info')
            session['user_name'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            flash('Incorrect Creditials', 'danger')
            return redirect('/login')
    else:
        return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_name')
    flash('Logged out succesfully!', 'info')
    return redirect('/')
    