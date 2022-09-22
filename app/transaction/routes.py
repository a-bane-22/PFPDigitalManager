from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Account, Security, Position, Transaction)
from app.transaction.forms import (AddSecurityForm, EditSecurityForm, TransactionForm, UploadFileForm)
from app.transaction import bp
from app.route_helpers import (get_security_choices, upload_file)
from datetime import date


@bp.route('/view_securities')
@login_required
def view_securities():
    securities = Security.query.all()
    return render_template('view_securities.html', title='Securities', securities=securities)


@bp.route('/view_security/<security_id>')
@login_required
def view_security(security_id):
    security = Security.query.get(int(security_id))
    positions = security.positions
    transactions = security.transactions
    return render_template('view_security.html', title='Security', security=security, positions=positions,
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
    return render_template('add_security.html', title='Add Security', form=form)


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
    return render_template('edit_security.html', title='Edit Security', form=form, security=security)


@bp.route('/upload_securities', methods=['GET', 'POST'])
@login_required
def upload_securities():
    return render_template('upload_securities.html', title='Upload Securities')


@bp.route('/view_positions')
@login_required
def view_positions():
    positions = Position.query.all()
    return render_template('view_positions.html', title='Positions', positions=positions)


@bp.route('/view_position/<position_id>')
@login_required
def view_position(position_id):
    position = Position.query.get(int(position_id))
    transactions = position.transactions
    return render_template('view_position.html', title='Position', position=position, transactions=transactions)


@bp.route('/view_transactions')
@login_required
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('view_transactions.html', title='Transactions', transactions=transactions)


@bp.route('/view_transaction/<transaction_id>')
@login_required
def view_transaction(transaction_id):
    transaction = Transaction.query.get(int(transaction_id))
    return render_template('view_transaction.html', title='Transaction', transaction=transaction)


@bp.route('/add_transaction/<account_id>', methods=['GET', 'POST'])
@login_required
def add_transaction(account_id):
    account = Account.query.get(int(account_id))
    form = TransactionForm()
    form.security.choices = get_security_choices()
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
    return render_template('add_transaction.html', title='Add Transaction', form=form, account=account)


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
    return render_template('edit_transaction.html', title='Edit Transaction', form=form)


@bp.route('/upload_transactions', methods=['GET', 'POST'])
@login_required
def upload_transactions():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
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
    return render_template('upload_transaction_file.html', title='Upload Transaction File', form=form)


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
