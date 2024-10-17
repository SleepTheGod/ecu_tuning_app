from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, TuningForm
from models import db, User, Tuning

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Replace with hashed password check
            login_user(user)
            return redirect(url_for('tuning'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/tuning", methods=['GET', 'POST'])
@login_required
def tuning():
    form = TuningForm()
    if form.validate_on_submit():
        tuning = Tuning(user_id=current_user.id, parameter=form.parameter.data, value=form.value.data)
        db.session.add(tuning)
        db.session.commit()
        flash('Tuning parameter added!', 'success')
        return redirect(url_for('results'))
    return render_template('tuning.html', form=form)

@app.route("/results")
@login_required
def results():
    tunings = Tuning.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', tunings=tunings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
