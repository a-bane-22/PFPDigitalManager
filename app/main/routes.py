from flask import render_template, flash, redirect, url_for
from flask_login import current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import (User, Client, Group, Account, AccountSnapshot, Custodian, Security, Position, Transaction,
                        Quarter)
from app.main.forms import (AddUserForm, EditUserForm, ChangePasswordForm, DeleteUserForm,
                            ClientInformationForm, GroupForm, AssignClientsForm, AssignClientForm, AccountForm,
                            CustodianForm, AccountSnapshotForm, AddSecurityForm, EditSecurityForm, TransactionForm,
                            UploadTransactionForm, AddQuarterForm, EditQuarterForm)
from app.main import bp
from datetime import date
import os


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title='Home')


@bp.route('/view_users')
@login_required
def view_users():
    users = User.query.all()
    return render_template('main/view_users.html', title='Users', users=users)


@bp.route('/view_user/<user_id>')
@login_required
def view_user(user_id):
    user = User.query.get(int(user_id))
    return render_template('main/view_user.html', title='User Dashboard', user=user)


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.view_user', user_id=user.id))
    return render_template('main/add_user.html', title='Add User', form=form)


@bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(int(user_id))
    form = EditUserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.view_user', user_id=user.id))
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    form.phone.data = user.phone
    return render_template('main/edit_user.html', title='Edit User', form=form)


@bp.route('/change_password/<user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    user = User.query.get(int(user_id))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.view_user', user_id=user.id))
        else:
            flash('The password provided was not correct')
            return redirect(url_for('main.change_password', user_id=user.id))
    return render_template('main/change_password.html', title='Change Password', form=form)


@bp.route('/delete_user/<user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(int(user_id))
    form = DeleteUserForm()
    if form.validate_on_submit():
        if form.confirm.data:
            if current_user.id == user.id:
                logout_user()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.index'))
    return render_template('main/delete_user.html', title='Delete User', form=form, user=user)


@bp.route('/view_clients')
@login_required
def view_clients():
    clients = Client.query.all()
    return render_template('main/view_clients.html', title='Clients', clients=clients)


@bp.route('/view_client/<client_id>')
@login_required
def view_client(client_id):
    client = Client.query.get(int(client_id))
    accounts = client.accounts
    return render_template('main/view_client.html', title='Client Dashboard', client=client, accounts=accounts)


@bp.route('/add_client', methods=['GET', 'POST'])
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
        return redirect(url_for('main.view_client', client_id=client.id))
    return render_template('main/add_client.html', title='Add Client', form=form)


@bp.route('/edit_client/<client_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.view_client', client_id=client_id))
    form.first_name.data = client.first_name
    form.last_name.data = client.last_name
    if client.middle_name is not None:
        form.middle_name.data = client.middle_name
    form.dob.data = client.dob
    form.email.data = client.email
    form.cell_phone.data = client.cell_phone
    form.work_phone.data = client.work_phone
    form.home_phone.data = client.home_phone
    return render_template('main/edit_client.html', title='Edit Client', form=form)


@bp.route('/view_groups')
@login_required
def view_groups():
    groups = Group.query.all()
    return render_template('main/view_groups.html', title='Groups', groups=groups)


@bp.route('/view_group/<group_id>')
@login_required
def view_group(group_id):
    group = Group.query.get(int(group_id))
    clients = group.clients
    return render_template('main/view_group.html', title='Group Dashboard', group=group, clients=clients)


@bp.route('/add_group/', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('main.view_group', group_id=group.id))
    return render_template('main/add_group.html', title='Add Group', form=form)


@bp.route('/edit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get(int(group_id))
    form = GroupForm()
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('main.view_group', group_id=group.id))
    form.name.data = group.name
    return render_template('main/edit_group.html', title='Edit Group', form=form)


@bp.route('/assign_clients/<group_id>', methods=['GET', 'POST'])
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
            for account in client.accounts:
                for snapshot in account.snapshots:
                    snapshot.group_id = group.id
                    db.session.add(snapshot)
        db.session.commit()
        return redirect(url_for('main.view_group', group_id=group_id))
    unassigned_clients = Client.query.filter_by(group_id=None).all()
    choices = []
    for client in unassigned_clients:
        choices.append((client.id, client.get_name()))
    form.selections.choices = choices
    form.selections.size = len(unassigned_clients)
    return render_template('main/assign_clients.html', title='Assign Clients', group=group, form=form)


@bp.route('/assign_client/<client_id>', methods=['GET', 'POST'])
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
        for account in client.accounts:
            for snapshot in account.snapshots:
                snapshot.group_id = client.group_id
                db.session.add(snapshot)
        db.session.commit()
        return redirect(url_for('main.view_client', client_id=client_id))
    return render_template('main/assign_client.html', title='Assign Client', client=client, form=form)


@bp.route('/view_accounts')
@login_required
def view_accounts():
    accounts = Account.query.all()
    return render_template('main/view_accounts.html', title='Accounts', accounts=accounts)


@bp.route('/view_account/<account_id>')
@login_required
def view_account(account_id):
    account = Account.query.get(int(account_id))
    positions = account.positions
    transactions = account.transactions
    snapshots = account.snapshots
    return render_template('main/view_account.html', title='Account Dashboard', account=account,
                           positions=positions, transactions=transactions, snapshots=snapshots)


@bp.route('/add_account/<client_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.view_account', account_id=account.id))
    return render_template('main/add_account.html', title='Add Account', form=form, client=client)


@bp.route('/edit_account/<account_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.view_account', account_id=account.id))
    form.account_number.data = account.account_number
    form.description.data = account.description
    form.billable.data = account.billable
    form.discretionary.data = account.discretionary
    custodians = Custodian.query.all()
    choices = []
    for custodian in custodians:
        choices.append((custodian.id, custodian.name))
    form.custodian.choices = choices
    return render_template('main/edit_account.html', title='Edit Account', form=form)


@bp.route('/delete_account/<account_id>')
@login_required
def delete_account(account_id):
    account = Account.query.get(int(account_id))
    for snapshot in account.snapshots:
        quarter = Quarter.query.get(snapshot.quarter_id)
        quarter.aum -= snapshot.market_value
        db.session.delete(snapshot)
        db.session.add(quarter)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('main.view_accounts'))


@bp.route('/view_account_snapshots')
@login_required
def view_account_snapshots():
    snapshots = AccountSnapshot.query.all()
    return render_template('main/view_account_snapshots.html', title='Account Snapshots', snapshots=snapshots)


@bp.route('/view_account_snapshot/<snapshot_id>')
@login_required
def view_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    account = Account.query.get(snapshot.account_id)
    return render_template('main/view_account_snapshot.html', title='Account Snapshot', snapshot=snapshot, account=account)


@bp.route('/create_account_snapshot/<account_id>', methods=['GET', 'POST'])
@login_required
def add_account_snapshot(account_id):
    account = Account.query.get(int(account_id))
    form = AccountSnapshotForm()
    quarters = Quarter.query.all()
    choices = []
    for quarter in quarters:
        choices.append((quarter.id, quarter.name))
    form.quarter.choices = choices
    if form.validate_on_submit():
        quarter = Quarter.query.get(form.quarter.data)
        client = Client.query.get(account.client_id)
        snapshot = AccountSnapshot(account_id=account.id, market_value=form.market_value.data,
                                   date=date.today(), quarter_id=quarter.id, group_id=client.group_id)
        quarter.aum += snapshot.market_value
        db.session.add(snapshot)
        db.session.add(quarter)
        db.session.commit()
        return redirect(url_for('main.view_account_snapshot', snapshot_id=snapshot.id))
    return render_template('main/add_account_snapshot.html', title='Add Account Snapshot', form=form)


@bp.route('/delete_account_snapshot/<snapshot_id>')
@login_required
def delete_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    quarter = Quarter.query.get(snapshot.quarter_id)
    quarter.aum -= snapshot.market_value
    db.session.delete(snapshot)
    db.session.add(quarter)
    db.session.commit()
    return redirect(url_for('main.view_account_snapshots'))


@bp.route('/delete_all_account_snapshots')
@login_required
def delete_all_account_snapshots():
    num_deleted = AccountSnapshot.query.delete()
    quarters = Quarter.query.all()
    for quarter in quarters:
        quarter.aum = 0
        db.session.add(quarter)
    db.session.commit()
    flash('Deleted ' + str(num_deleted) + ' Account Snapshots')
    return redirect(url_for('main.index'))


@bp.route('/view_custodians')
@login_required
def view_custodians():
    custodians = Custodian.query.all()
    return render_template('main/view_custodians.html', title='Custodians', custodians=custodians)


@bp.route('/view_custodian/<custodian_id>')
@login_required
def view_custodian(custodian_id):
    custodian = Custodian.query.get(int(custodian_id))
    return render_template('main/view_custodian.html', title='Custodian Dashboard', custodian=custodian)


@bp.route('/add_custodian', methods=['GET', 'POST'])
@login_required
def add_custodian():
    form = CustodianForm()
    if form.validate_on_submit():
        custodian = Custodian(name=form.name.data, description=form.description.data)
        db.session.add(custodian)
        db.session.commit()
        return redirect(url_for('main.view_custodian', custodian_id=custodian.id))
    return render_template('main/add_custodian.html', title='Add Custodian', form=form)


@bp.route('/edit_custodian/<custodian_id>', methods=['GET', 'POST'])
@login_required
def edit_custodian(custodian_id):
    custodian = Custodian.query.get(int(custodian_id))
    form = CustodianForm()
    if form.validate_on_submit():
        custodian.name = form.name.data
        custodian.description = form.description.data
        db.session.add(custodian)
        db.session.commit()
        return redirect(url_for('main.view_custodian', custodian_id=custodian.id))
    form.name.data = custodian.name
    form.description.data = custodian.description
    return render_template('main/edit_custodian.html', title='Edit Custodian', form=form)


@bp.route('/view_securities')
@login_required
def view_securities():
    securities = Security.query.all()
    return render_template('main/view_securities.html', title='Securities', securities=securities)


@bp.route('/view_security/<security_id>')
@login_required
def view_security(security_id):
    security = Security.query.get(int(security_id))
    positions = security.positions
    transactions = security.transactions
    return render_template('main/view_security.html', title='Security', security=security, positions=positions,
                           transactions=transactions)


@bp.route('/add_security', methods=['GET', 'POST'])
@login_required
def add_security():
    form = AddSecurityForm()
    if form.validate_on_submit():
        security = Security(symbol=form.symbol.data, name=form.name.data, description=form.description.data)
        db.session.add(security)
        db.session.commit()
        return redirect(url_for('main.view_security', security_id=security.id))
    return render_template('main/add_security.html', title='Add Security', form=form)


@bp.route('/edit_security/<security_id>', methods=['GET', 'POST'])
@login_required
def edit_security(security_id):
    security = Security.query.get(int(security_id))
    form = EditSecurityForm()
    if form.validate_on_submit():
        security.name = form.name.data
        security.description = form.description.data
        db.session.add(security)
        db.session.commit()
        return redirect(url_for('main.view_security', security_id=security.id))
    form.name.data = security.name
    form.description.data = security.description
    return render_template('main/edit_security.html', title='Edit Security', form=form, security=security)


@bp.route('/view_positions')
@login_required
def view_positions():
    positions = Position.query.all()
    return render_template('main/view_positions.html', title='Positions', positions=positions)


@bp.route('/view_position/<position_id>')
@login_required
def view_position(position_id):
    position = Position.query.get(int(position_id))
    transactions = position.transactions
    return render_template('main/view_position.html', title='Position', position=position, transactions=transactions)


@bp.route('/view_transactions')
@login_required
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('main/view_transactions.html', title='Transactions', transactions=transactions)


@bp.route('/view_transaction/<transaction_id>')
@login_required
def view_transaction(transaction_id):
    transaction = Transaction.query.get(int(transaction_id))
    return render_template('main/view_transaction.html', title='Transaction', transaction=transaction)


@bp.route('/add_transaction/<account_id>', methods=['GET', 'POST'])
@login_required
def add_transaction(account_id):
    account = Account.query.get(int(account_id))
    form = TransactionForm()
    securities = Security.query.all()
    security_choices = []
    for security in securities:
        security_choices.append((security.id, security.symbol))
    form.security.choices = security_choices
    type_choices = [('BUY', 'Buy'), ('SELL', 'Sell')]
    form.type.choices = type_choices
    if form.validate_on_submit():
        security = Security.query.get(int(form.security.data))
        position = Position.query.filter_by(account_id=account.id, security_id=security.id).first()
        if position is None:
            position = Position(quantity=0, cost_basis=0, account_id=account.id, security_id=security.id)
            db.session.add(position)
            db.session.commit()
        transaction = Transaction(date=form.date.data, type=form.type.data, quantity=form.quantity.data,
                                  share_price=form.share_price.data, gross_amount=form.gross_amount.data,
                                  description=form.description.data, account_id=account.id, security_id=security.id,
                                  position_id=position.id)
        position.add_transaction(transaction_type=transaction.type, quantity=transaction.quantity,
                                 gross_amount=transaction.gross_amount)
        db.session.add(transaction)
        db.session.add(position)
        db.session.commit()
        return redirect(url_for('main.view_account', account_id=account_id))
    return render_template('main/add_transaction.html', title='Add Transaction', form=form, account=account)


@bp.route('/add_transaction_redirect')
@login_required
def add_transaction_redirect():
    flash('Choose an account')
    return redirect(url_for('main.view_accounts'))


@bp.route('/edit_transaction/<transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get(int(transaction_id))
    form = TransactionForm()
    if form.validate_on_submit():
        transaction.date = form.date.data
        transaction.type = form.type.data
        transaction.quantity = form.quantity.data
        transaction.share_price = form.share_price.data
        transaction.gross_amount = form.gross_amount.data
        transaction.description = form.description.data
        position = Position.query.get(transaction.position_id)
        position.recreate_position()
        db.session.add(transaction)
        db.session.add(position)
        db.session.commit()
        return redirect(url_for('main.view_transaction', transaction_id=transaction.id))
    form.date.data = transaction.date
    form.type.data = transaction.type
    form.quantity.data = transaction.quantity
    form.share_price.data = transaction.share_price
    form.gross_amount.data = transaction.gross_amount
    form.description.data = transaction.description
    return render_template('main/edit_transaction.html', title='Edit Transaction', form=form)


@bp.route('/upload_transactions', methods=['GET', 'POST'])
@login_required
def upload_transactions():
    form = UploadTransactionForm()
    if form.validate_on_submit():
        f = form.transaction_file.data
        transaction_filename = os.path.join('uploads/files/' + secure_filename(f.filename))
        f.save(transaction_filename)
        transaction_file = open(transaction_filename, 'r')
        transaction_file.readline()
        lines = transaction_file.readlines()
        transaction_file.close()
        for line in lines:
            data = line.split(',')
            transaction_date = date.fromisoformat(data[0].strip())
            account_number = data[1].strip()
            transaction_type = data[2].strip()
            symbol = data[3].strip()
            name = data[4].strip()
            quantity = float(data[5].strip())
            share_price = float(data[6].strip())
            gross_amount = float(data[7].strip())
            description = data[8].strip()
            account = Account.query.filter_by(account_number=account_number).first()
            security = Security.query.filter_by(symbol=symbol).first()
            if security is None:
                security = Security(symbol=symbol, name=name)
                db.session.add(security)
                db.session.commit()
            position = Position.query.filter_by(account_id=account.id, security_id=security.id).first()
            if position is None:
                position = Position(account_id=account.id, security_id=security.id, quantity=0, cost_basis=0)
                db.session.add(position)
                db.session.commit()
            transaction = Transaction(date=transaction_date, type=transaction_type, quantity=quantity,
                                      share_price=share_price, gross_amount=gross_amount, description=description,
                                      account_id=account.id, security_id=security.id, position_id=position.id)
            position.add_transaction(transaction_type=transaction_type, quantity=transaction.quantity,
                                     gross_amount=transaction.gross_amount)
            db.session.add(transaction)
            db.session.add(position)
        db.session.commit()
        return redirect(url_for('main.view_transactions'))
    return render_template('main/upload_transaction_file.html', title='Upload Transaction File', form=form)


@bp.route('/delete_transaction/<transaction_id>')
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(int(transaction_id))
    position = Position.query.get(int(transaction.position_id))
    position.remove_transaction(transaction_id=transaction.id)
    db.session.delete(transaction)
    db.session.add(position)
    db.session.commit()
    return redirect(url_for('main.view_transactions'))


@bp.route('/view_quarters')
@login_required
def view_quarters():
    quarters = Quarter.query.all()
    return render_template('main/view_quarters.html', title='View Quarters', quarters=quarters)


@bp.route('/view_quarter/<quarter_id>')
@login_required
def view_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    snapshots = quarter.account_snapshots
    return render_template('main/view_quarter.html', title='View Quarter', quarter=quarter, snapshots=snapshots)


@bp.route('/add_quarter', methods=['GET', 'POST'])
@login_required
def add_quarter():
    form = AddQuarterForm()
    if form.validate_on_submit():
        quarter = Quarter(from_date=form.from_date.data, to_date=form.to_date.data, name=form.name.data,
                          aum=0)
        db.session.add(quarter)
        db.session.commit()
        f = form.account_file.data
        account_filename = os.path.join('uploads/files/' + secure_filename(f.filename))
        f.save(account_filename)
        create_account_snapshots_from_file(quarter_id=quarter.id, filename=account_filename)
        return redirect(url_for('main.view_quarter', quarter_id=quarter.id))
    return render_template('main/add_quarter.html', title='Add Quarter', form=form)


# MOVE TO ROUTE HELPER FILE
def create_account_snapshots_from_file(quarter_id, filename):
    quarter = Quarter.query.get(quarter_id)
    account_file = open(filename, 'r')
    account_file.readline()
    lines = account_file.readlines()
    account_file.close()
    for line in lines:
        data = line.split(',')
        snapshot_date = date.fromisoformat(data[0].strip())
        account_number = data[1].strip()
        account_description = data[3].strip()
        market_value = float(data[4].strip())
        group_name = data[8].strip()
        group = Group.query.filter_by(name=group_name).first()
        if group is None:
            group = Group(name=group_name)
            db.session.add(group)
            group = Group.query.filter_by(name=group_name).first()
        account = Account.query.filter_by(account_number=account_number).first()
        if account is None:
            custodian_name = data[2].strip()
            custodian = Custodian.query.filter_by(name=custodian_name).first()
            client_first = data[5].strip()
            client_middle = data[6].strip()
            client_last = data[7].strip()
            client = Client.query.filter_by(first_name=client_first, middle_name=client_middle,
                                            last_name=client_last).first()
            account = Account(account_number=account_number, description=account_description, billable=True,
                              custodian_id=custodian.id, client_id=client.id)
            db.session.add(account)
            account = Account.query.filter_by(account_number=account_number).first()
        snapshot = AccountSnapshot(date=snapshot_date, market_value=market_value,
                                   account_id=account.id, quarter_id=quarter_id, group_id=group.id)
        quarter.aum += market_value
        db.session.add(snapshot)
    db.session.add(quarter)
    db.session.commit()


@bp.route('/edit_quarter/<quarter_id>', methods=['GET', 'POST'])
@login_required
def edit_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    form = EditQuarterForm()
    if form.validate_on_submit():
        quarter.from_date = form.from_date.data
        quarter.to_date = form.to_date.data
        quarter.name = form.name.data
        db.session.add(quarter)
        db.session.commit()
        return redirect(url_for('main.view_quarter', quarter_id=quarter.id))
    form.from_date.data = quarter.from_date
    form.to_date.data = quarter.to_date
    form.name.data = quarter.name
    return render_template('main/edit_quarter.html', title='Edit Quarter', form=form)


@bp.route('/delete_quarter/<quarter_id>')
@login_required
def delete_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for snapshot in quarter.account_snapshots:
        db.session.delete(snapshot)
    db.session.delete(quarter)
    db.session.commit()
    return redirect(url_for('main.view_quarters'))
