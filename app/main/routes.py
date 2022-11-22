from flask import render_template, url_for, redirect
from flask_login import login_required
from app.main import bp
from app.main.forms import GetStartedForm
from app.route_helpers import (process_client_csv_file,
                               process_account_csv_file,
                               process_transaction_csv_file)


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')


@bp.route('/get_started')
@login_required
def get_started():
    form = GetStartedForm()
    if form.validate_on_submit():
        process_client_csv_file(file_object=form.client_file.data)
        process_account_csv_file(file_object=form.account_file.data)
        process_transaction_csv_file(file_object=form.transaction_file.data)
        return redirect(url_for('main.index'))
    return render_template('get_started.html', title='Get Started', form=form)
