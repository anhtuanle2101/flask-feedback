from flask import Flask, redirect, render_template, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from secret import APP_SECRET
from forms import UserForm, LoginForm, FeedbackForm
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
        feedbacks = Feedback.query.order_by(Feedback.id).filter(Feedback.username == user.username).all()
        return render_template('user.html', user=user, feedbacks=feedbacks)
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
        session['user_name'] = new_user.username
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
    
# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their feedback. 
# Clear any user information in the session and redirect to /. 
# Make sure that only the user who is logged in can successfully delete their account
@app.route('/users/<username>/delete', methods=['POST'])
def delete_account(username):
    if 'user_name' in session:
        user = User.query.filter(User.username == username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop('user_name')
        flash('Delete account succesfully', 'info')
        return redirect('/register')
    else:
        flash('Please login first!', 'danger')
        return redirect('/login')

# GET /users/<username>/feedback/add
# Display a form to add feedback Make sure that only the user who is logged in can see this form
# POST /users/<username>/feedback/add
# Add a new piece of feedback and redirect to /users/<username> — Make sure that only the 
# user who is logged in can successfully add feedback
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'user_name' in session:
        user = User.query.filter(User.username == username).first()
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = user.username
            new_feedback = Feedback(title=title, content=content, username=username)
            user.feedbacks.append(new_feedback)
            db.session.commit()
            flash('Feedback added', 'info')
            return redirect(f'/users/{user.username}')
        return render_template('feedback.html', user=user, form=form)
    else:
        flash('Please login first!')
        return redirect('/login')

# GET /feedback/<feedback-id>/update
# Display a form to edit feedback — **Make sure that only the user who has written that 
# feedback can see this form **
# POST /feedback/<feedback-id>/update
# Update a specific piece of feedback and redirect to /users/<username> — Make sure that only 
# the user who has written that feedback can update it
@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    if 'user_name' in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        user = feedback.user
        if session['user_name'] == user.username:
            form = FeedbackForm(obj=feedback)
            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data
                db.session.commit()
                flash(f'Feedback {feedback.id} is updated!', 'info')
                return redirect(f'/users/{user.username}')
            else:
                return render_template('feedback_edit.html', form=form, feedback=feedback)
        else:
            flash('This feedback is unauthorized!', 'danger')
            return redirect(f'/users/{user.username}')
    else:
        flash('Please login first!', 'danger')
        return redirect('/login')


# POST /feedback/<feedback-id>/delete
# Delete a specific piece of feedback and redirect to /users/<username> — Make sure that only 
# the user who has written that feedback can delete it
@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if 'user_name' in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        user = feedback.user
        if session['user_name'] == user.username:
            db.session.delete(feedback)
            db.session.commit()
            flash(f'Feedback {feedback.id} is deleleted by {user.username}', 'info')
            return redirect(f'/users/{user.username}')
        else:
            flash('This feedback is unauthorized!', 'danger')
            return redirect(f'/users/{user.username}')
    else:
        flash('Please login first!', 'danger')
        return redirect('/login')