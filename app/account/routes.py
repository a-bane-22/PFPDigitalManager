from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Client, Account, AccountSnapshot, Custodian, Quarter)
from app.account.forms import (AccountForm, CustodianForm, AccountSnapshotForm, UploadFileForm)
from app.account import bp
from app.route_helpers import (get_custodian_choices, get_fee_schedule_choices, upload_file)
from datetime import date


@bp.route('/view_accounts')
@login_required
def view_accounts():
    accounts = Account.query.all()
    return render_template('view_accounts.html', title='Accounts', accounts=accounts)


@bp.route('/view_account/<account_id>')
@login_required
def view_account(account_id):
    account = Account.query.get(int(account_id))
    positions = account.positions
    transactions = account.transactions
    snapshots = account.snapshots
    return render_template('view_account.html', title='Account Dashboard', account=account,
                           positions=positions, transactions=transactions, snapshots=snapshots)


@bp.route('/add_account/<client_id>', methods=['GET', 'POST'])
@login_required
def add_account(client_id):
    client = Client.query.get(int(client_id))
    form = AccountForm()
    custodian_choices = get_custodian_choices()
    fee_schedule_choices = get_fee_schedule_choices()
    form.custodian.choices = custodian_choices
    form.fee_schedule.choices = fee_schedule_choices
    if form.validate_on_submit():
        if form.fee_schedule.data == 'None':
            schedule_id = None
        else:
            schedule_id = form.fee_schedule.data
        account = Account(account_number=form.account_number.data, description=form.description.data,
                          discretionary=form.discretionary.data, billable=form.billable.data,
                          client_id=int(client_id), custodian_id=form.custodian.data,
                          schedule_id=schedule_id)
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account.view_account', account_id=account.id))
    return render_template('add_account.html', title='Add Account', form=form, client=client)


@bp.route('/upload_accounts', methods=['GET', 'POST'])
@login_required
def upload_accounts():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        for line in lines:
            data = line.split(',')
            account_number = data[0].strip()
            description = data[1].strip()
            client_first = data[2].strip()
            client_last = data[3].strip()
            custodian_name = data[4].strip()
            billable = (data[5].strip().lower() == 'true')
            discretionary = (data[6].strip().lower() == 'true')
            client = Client.query.filter_by(first_name=client_first, last_name=client_last).first()
            if client is not None:
                custodian = Custodian.query.filter_by(name=custodian_name).first()
                if custodian is None:
                    custodian = Custodian(name=custodian_name)
                    db.session.add(custodian)
                    db.session.commit()
                account = Account(account_number=account_number, description=description, billable=billable,
                                  discretionary=discretionary, client_id=client.id, custodian_id=custodian.id)
                db.session.add(account)
        db.session.commit()
        return redirect(url_for('account.view_accounts'))
    return render_template('upload_account_file.html', title='Upload Accounts', form=form)


@bp.route('/edit_account/<account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    account = Account.query.get(int(account_id))
    form = AccountForm()
    custodian_choices = get_custodian_choices()
    fee_schedule_choices = get_fee_schedule_choices()
    form.custodian.choices = custodian_choices
    form.fee_schedule.choices = fee_schedule_choices
    if form.validate_on_submit():
        account.account_number = form.account_number.data
        account.description = form.description.data
        account.billable = form.billable.data
        account.discretionary = form.discretionary.data
        if form.fee_schedule.data == 'None':
            schedule_id = None
        else:
            schedule_id = form.fee_schedule.data
        account.schedule_id = schedule_id
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account.view_account', account_id=account.id))
    form.account_number.data = account.account_number
    form.description.data = account.description
    form.billable.data = account.billable
    form.discretionary.data = account.discretionary
    return render_template('edit_account.html', title='Edit Account', form=form)


@bp.route('/delete_account/<account_id>')
@login_required
def delete_account(account_id):
    account = Account.query.get(int(account_id))
    for snapshot in account.snapshots:
        quarter = Quarter.query.get(snapshot.quarter_id)
        quarter.aum -= snapshot.market_value
        quarter.fee -= snapshot.fee
        db.session.delete(snapshot)
        db.session.add(quarter)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('account.view_accounts'))


@bp.route('/view_account_snapshots')
@login_required
def view_account_snapshots():
    snapshots = AccountSnapshot.query.all()
    return render_template('view_account_snapshots.html', title='Account Snapshots', snapshots=snapshots)


@bp.route('/view_account_snapshot/<snapshot_id>')
@login_required
def view_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    account = Account.query.get(snapshot.account_id)
    return render_template('view_account_snapshot.html', title='Account Snapshot', snapshot=snapshot, account=account)


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
        snapshot.calculate_fee()
        quarter.aum += snapshot.market_value
        quarter.fee += snapshot.fee
        db.session.add(snapshot)
        db.session.add(quarter)
        db.session.commit()
        return redirect(url_for('account.view_account_snapshot', snapshot_id=snapshot.id))
    return render_template('add_account_snapshot.html', title='Add Account Snapshot', form=form)


@bp.route('/delete_account_snapshot/<snapshot_id>')
@login_required
def delete_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    quarter = Quarter.query.get(snapshot.quarter_id)
    quarter.aum -= snapshot.market_value
    quarter.fee -= snapshot.fee
    db.session.delete(snapshot)
    db.session.add(quarter)
    db.session.commit()
    return redirect(url_for('account.view_account_snapshots'))


@bp.route('/delete_all_account_snapshots')
@login_required
def delete_all_account_snapshots():
    num_deleted = AccountSnapshot.query.delete()
    quarters = Quarter.query.all()
    for quarter in quarters:
        quarter.aum = 0
        quarter.fee = 0
        db.session.add(quarter)
    db.session.commit()
    flash('Deleted ' + str(num_deleted) + ' Account Snapshots')
    return redirect(url_for('main.index'))


@bp.route('/view_custodians')
@login_required
def view_custodians():
    custodians = Custodian.query.all()
    return render_template('view_custodians.html', title='Custodians', custodians=custodians)


@bp.route('/view_custodian/<custodian_id>')
@login_required
def view_custodian(custodian_id):
    custodian = Custodian.query.get(int(custodian_id))
    return render_template('view_custodian.html', title='Custodian Dashboard', custodian=custodian)


@bp.route('/add_custodian', methods=['GET', 'POST'])
@login_required
def add_custodian():
    form = CustodianForm()
    if form.validate_on_submit():
        custodian = Custodian(name=form.name.data, description=form.description.data)
        db.session.add(custodian)
        db.session.commit()
        return redirect(url_for('account.view_custodian', custodian_id=custodian.id))
    return render_template('add_custodian.html', title='Add Custodian', form=form)


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
        return redirect(url_for('account.view_custodian', custodian_id=custodian.id))
    form.name.data = custodian.name
    form.description.data = custodian.description
    return render_template('edit_custodian.html', title='Edit Custodian', form=form)
