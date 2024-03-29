from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Client, Account, Custodian, Quarter)
from app.account.forms import (AccountForm, CustodianForm, UploadFileForm,
                               ExportToFileForm)
from app.account import bp
from app.route_helpers import (get_custodian_choices, get_fee_schedule_choices, upload_file,
                               process_account_csv_file)
from werkzeug.utils import secure_filename
import os


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
                          client_id=client.id, group_id=client.group_id, custodian_id=form.custodian.data,
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
        process_account_csv_file(file_object=f)
        return redirect(url_for('account.view_accounts'))
    return render_template('upload_account_file.html', title='Upload Accounts', form=form)


@bp.route('/export_accounts', methods=['GET', 'POST'])
@login_required
def export_accounts():
    form = ExportToFileForm()
    if form.validate_on_submit():
        filename = os.path.join('exports/' + secure_filename(form.filename.data))
        with open(filename, 'w') as export_file:
            export_file.write('Account Number,Description,Client First Name,Client Last Name,' +
                              'Custodian,Billable,Discretionary\n')
            accounts = Account.query.all()
            for account in accounts:
                export_file.write(account.export_account_csv() + '\n')
        return redirect(url_for('main.index'))
    return render_template('export_accounts.html', title='Export Accounts', form=form)


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


@bp.route('/delete_all_accounts')
@login_required
def delete_all_accounts():
    accounts = Account.query.all()
    for account in accounts:
        db.session.delete(account)
    db.session.commit()
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
