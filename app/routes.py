from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, ClientInformationForm, GroupForm, AssignClientsForm, AssignClientForm, AccountForm, CustodianForm
from app.models import User, Client, Group, Account, Custodian


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='User Dashboard', user=user)


@app.route('/clients')
@login_required
def clients():
    clients = Client.query.all()
    return render_template('clients.html', title='Clients', clients=clients)


@app.route('/client/<client_id>')
@login_required
def client(client_id):
    client = Client.query.get(int(client_id))
    accounts = client.accounts
    return render_template('client.html', title='Client Dashboard', client=client, accounts=accounts)


@app.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientInformationForm()
    if form.validate_on_submit():
        client = Client(first_name=form.first_name.data, last_name=form.last_name.data,
                        middle_name=form.middle_name.data, dob=form.dob.data, email=form.email.data,
                        cell_phone=form.cell_phone.data, work_phone=form.work_phone.data,
                        home_phone=form.home_phone.data, assigned=False)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client', client_id=client.id))
    return render_template('add_client.html', title='Add Client', form=form)


@app.route('/edit_client/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get(int(client_id))
    form = ClientInformationForm()
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
        return redirect(url_for('client', client_id=client_id))
    form.first_name.data = client.first_name
    form.last_name.data = client.last_name
    if client.middle_name is not None:
        form.middle_name.data = client.middle_name
    form.dob.data = client.dob
    form.email.data = client.email
    form.cell_phone.data = client.cell_phone
    form.work_phone.data = client.work_phone
    form.home_phone.data = client.home_phone
    return render_template('edit_client.html', title='Edit Client', form=form)


@app.route('/groups')
@login_required
def groups():
    groups = Group.query.all()
    return render_template('groups.html', title='Groups', groups=groups)


@app.route('/group/<group_id>')
@login_required
def group(group_id):
    group = Group.query.get(int(group_id))
    clients = group.clients
    return render_template('group.html', title='Group Dashboard', group=group, clients=clients)


@app.route('/add_group/', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('group', group_id=group.id))
    return render_template('add_group.html', title='Add Group', form=form)


@app.route('/edit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get(int(group_id))
    form = GroupForm()
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('group', group_id=group.id))
    form.name.data = group.name
    return render_template('edit_group.html', title='Edit Group', form=form)


@app.route('/assign_clients/<group_id>', methods=['GET', 'POST'])
@login_required
def assign_clients(group_id):
    group = Group.query.get(int(group_id))
    form = AssignClientsForm()
    if form.validate_on_submit():
        assigned_client_ids = form.selections.data
        for client_id in assigned_client_ids:
            client = Client.query.get(client_id)
            client.group_id = group.id
            client.assigned = True
            db.session.add(client)
        db.session.commit()
        return redirect(url_for('group', group_id=group_id))
    unassigned_clients = Client.query.filter_by(group_id=None).all()
    choices = []
    for client in unassigned_clients:
        choices.append((client.id, client.get_name()))
    form.selections.choices = choices
    form.selections.size = len(unassigned_clients)
    return render_template('assign_clients.html', title='Assign Clients', group=group, form=form)


@app.route('/assign_client/<client_id>', methods=['GET', 'POST'])
@login_required
def assign_client(client_id):
    client = Client.query.get(int(client_id))
    groups = Group.query.all()
    choices = []
    for group in groups:
        choices.append((group.id, group.name))
    form = AssignClientForm()
    form.selection.choices = choices
    if form.validate_on_submit():
        client.group_id = form.selection.data
        client.assigned = True
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client', client_id=client_id))
    return render_template('assign_client.html', title='Assign Client', client=client, form=form)


@app.route('/accounts')
@login_required
def accounts():
    accounts = Account.query.all()
    return render_template('accounts.html', title='Accounts', accounts=accounts)


@app.route('/account/<account_id>')
@login_required
def account(account_id):
    account = Account.query.get(int(account_id))
    return render_template('account.html', title='Account Dashboard', account=account)


@app.route('/add_account/<client_id>', methods=['GET', 'POST'])
@login_required
def add_account(client_id):
    client = Client.query.get(int(client_id))
    form = AccountForm()
    custodians = Custodian.query.all()
    choices = []
    for custodian in custodians:
        choices.append((custodian.id, custodian.name))
    form.custodian.choices = choices
    if form.validate_on_submit():
        account = Account(account_number=form.account_number.data, description=form.description.data,
                          discretionary=form.discretionary.data, billable=form.billable.data,
                          client_id=int(client_id), custodian_id=form.custodian.data)
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account', account_id=account.id))
    return render_template('add_account.html', title='Add Account', form=form, client=client)


@app.route('/edit_account/<account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    account = Account.query.get(int(account_id))
    form = AccountForm()
    if form.validate_on_submit():
        account.account_number = form.account_number.data
        account.description = form.description.data
        account.billable = form.billable.data
        account.discretionary = form.discretionary.data
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account', account_id=account.id))
    form.account_number.data = account.account_number
    form.description.data = account.description
    form.billable.data = account.billable
    form.discretionary.data = account.discretionary
    custodians = Custodian.query.all()
    choices = []
    for custodian in custodians:
        choices.append((custodian.id, custodian.name))
    form.custodian.choices = choices
    return render_template('edit_account.html', title='Edit Account', form=form)


@app.route('/custodians')
@login_required
def custodians():
    custodians = Custodian.query.all()
    return render_template('custodians.html', title='Custodians', custodians=custodians)


@app.route('/custodian/<custodian_id>')
@login_required
def custodian(custodian_id):
    custodian = Custodian.query.get(int(custodian_id))
    return render_template('custodian.html', title='Custodian Dashboard', custodian=custodian)


@app.route('/add_custodian', methods=['GET', 'POST'])
@login_required
def add_custodian():
    form = CustodianForm()
    if form.validate_on_submit():
        custodian = Custodian(name=form.name.data, description=form.description.data)
        db.session.add(custodian)
        db.session.commit()
        return redirect(url_for('custodian', custodian_id=custodian.id))
    return render_template('add_custodian.html', title='Add Custodian', form=form)


@app.route('/edit_custodian/<custodian_id>', methods=['GET', 'POST'])
@login_required
def edit_custodian(custodian_id):
    custodian = Custodian.query.get(int(custodian_id))
    form = CustodianForm()
    if form.validate_on_submit():
        custodian.name = form.name.data
        custodian.description = form.description.data
        db.session.add(custodian)
        db.session.commit()
        return redirect(url_for('custodian', custodian_id=custodian.id))
    form.name.data = custodian.name
    form.description.data = custodian.description
    return render_template('edit_custodian.html', title='Edit Custodian', form=form)


