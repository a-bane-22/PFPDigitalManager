from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Security, SecuritySnapshot)
from app.security.forms import (AddSecurityForm, EditSecurityForm, UploadFileForm, ExportToFileForm)
from app.security import bp
from app.route_helpers import (get_security_choices, upload_file)
from datetime import date
import os
from werkzeug.utils import secure_filename
from alpha_vantage.timeseries import TimeSeries
import pandas as pd


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
        return redirect(url_for('security.view_security', security_id=security.id))
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
        return redirect(url_for('security.view_security', security_id=security.id))
    form.name.data = security.name
    form.description.data = security.description
    return render_template('edit_security.html', title='Edit Security', form=form, security=security)


@bp.route('/upload_securities', methods=['GET', 'POST'])
@login_required
def upload_securities():
    return render_template('upload_securities.html', title='Upload Securities')


@bp.route('/update_security_data/<security_id>')
@login_required
def update_security_data(security_id):
    security = Security.query.get(int(security_id))
    if security.last_snapshot != date.today() or True:
        ts = TimeSeries(key=os.environ['ALPHAVANTAGE_API_KEY'])
        data, meta_data = ts.get_daily(symbol=security.symbol,
                                       outputsize='compact')
        df = pd.DataFrame(data)
        rows = df.index
        date_key = df.columns[0]
        data_date = date.fromisoformat(date_key)
        df.loc[rows[0]] = df.loc[rows[0]].astype(float)
        df.loc[rows[1]] = df.loc[rows[1]].astype(float)
        df.loc[rows[2]] = df.loc[rows[2]].astype(float)
        df.loc[rows[3]] = df.loc[rows[3]].astype(float)
        df.loc[rows[4]] = df.loc[rows[4]].astype(float)
        hundred_day_average_open = round(df.loc[rows[0]].mean(), 2)
        hundred_day_average_high = round(df.loc[rows[1]].mean(), 2)
        hundred_day_average_low = round(df.loc[rows[2]].mean(), 2)
        hundred_day_average_close = round(df.loc[rows[3]].mean(), 2)
        hundred_day_average_volume = round(df.loc[rows[4]].mean())
        snapshot = SecuritySnapshot(symbol=security.symbol,
                                    data_date=data_date,
                                    open_value=df.loc[rows[0]][date_key],
                                    close_value=df.loc[rows[3]][date_key],
                                    high_value=df.loc[rows[1]][date_key],
                                    low_value=df.loc[rows[2]][date_key],
                                    volume=df.loc[rows[4]][date_key],
                                    hundred_day_average_open=hundred_day_average_open,
                                    hundred_day_average_close=hundred_day_average_close,
                                    hundred_day_average_low=hundred_day_average_low,
                                    hundred_day_average_high=hundred_day_average_high,
                                    hundred_day_average_volume=hundred_day_average_volume,
                                    security_id=security.id)
        db.session.add(snapshot)
        security.last_snapshot = date.today()
        db.session.add(security)
        db.session.commit()
    else:
        flash('Data is current')
    return redirect(url_for('security.view_security', security_id=security_id))


@bp.route('/view_security_snapshot/<snapshot_id>')
@login_required
def view_security_snapshot(snapshot_id):
    snapshot = SecuritySnapshot.query.get(int(snapshot_id))
    return render_template('view_security_snapshot.html', title='Security Snapshot', snapshot=snapshot)


@bp.route('/delete_security_snapshot/<snapshot_id>')
@login_required
def delete_security_snapshot(snapshot_id):
    snapshot = SecuritySnapshot.query.get(int(snapshot_id))
    security_id = snapshot.security_id
    db.session.delete(snapshot)
    db.session.commit()
    return redirect(url_for('security.view_security', security_id=security_id))
