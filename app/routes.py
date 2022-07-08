from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ClientInformationForm
from app.models import User, Client


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user_profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='User Profile', user=user)


@app.route('/client_profile/<client_id>')
@login_required
def client_profile(client_id):
    client = Client.query.get(int(client_id))
    return render_template('client.html', title='Client Profile', client=client)


@app.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientInformationForm()
    if form.validate_on_submit():
        client = Client(first_name=form.first_name.data, last_name=form.last_name.data,
                        middle_name=form.middle_name.data, dob=form.dob.data, email=form.email.data,
                        cell_phone=form.cell_phone.data, work_phone=form.work_phone.data,
                        home_phone=form.home_phone.data)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client', client_id=client.id))
    return render_template('add_client.html', title='Add Client', form=form)


@app.route('/edit_client/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get(int(client_id))
    form = ClientInformationForm()
    form.first_name = client.first_name
    form.last_name = client.last_name
    if client.middle_name is not None:
        form.middle_name = client.middle_name
    form.dob.data = client.dob
    form.email.data = client.email
    form.cell_phone.data = client.cell_phone
    form.work_phone.data = client.work_phone
    form.home_phone.data = client.home_phone
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.middle_name = form.middle_name.data
        client.last_name = form.last_name.data
        client.dob = form.dob.data
        client.email = form.email.data
        client.cell_phone = form.cell_phone.data
        client.work_phone = form.work_phone.data
        client.home_phone = form.home_phone.data
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client.html', client_id=client_id))
    return render_template('edit_client.html', title='Edit Client', form=form)
