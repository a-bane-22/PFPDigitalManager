from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Security, SecuritySnapshot, SecurityIndicatorChart)
from app.security.forms import (AddSecurityForm, EditSecurityForm, WMACrossoverForm,
                                UploadFileForm, ExportToFileForm)
from app.security import bp
from app.route_helpers import (get_security_choices, upload_file)
from app.security.route_helpers import generate_daily_close_wma_crossover_chart, get_crossover_points
from datetime import date
import os
from werkzeug.utils import secure_filename
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


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


@bp.route('/view_security_momentum/<security_id>')
@login_required
def view_security_momentum(security_id):
    security = Security.query.get(int(security_id))
    file_name = os.path.join('technical_indicators/momentum/' +
                             "{}_momentum.png".format(security.symbol))
    ti = TechIndicators(key=os.environ['ALPHAVANTAGE_API_KEY'])
    data, meta_data = ti.get_mom(symbol=security.symbol, interval='daily',
                                 time_period=20, series_type='close')
    dates = [key for key in data.keys()]
    values = [float(data[key]['MOM']) for key in data.keys()]
    point_pairs = dict([(i, (dates[i], values[i])) for i in range(100)])
    df = pd.DataFrame(point_pairs)
    fig = px.line(x=df.loc[0], y=df.loc[1])
    fig.add_trace()
    fig.write_image(file_name)
    return redirect(url_for('security.view_security', security_id=security_id))


@bp.route('/generate_daily_close_wma_crossover/<security_id>', methods=['GET', 'POST'])
@login_required
def generate_daily_close_wma_crossover(security_id):
    form = WMACrossoverForm()
    if form.validate_on_submit():
        security = Security.query.get(int(security_id))
        num_points = form.num_points.data
        period_0 = form.period_0.data
        period_1 = form.period_1.data
        file_name = generate_daily_close_wma_crossover_chart(symbol=security.symbol,
                                                             num_points=num_points,
                                                             period_0=period_0,
                                                             period_1=period_1)
        description = ('{symbol} WMA Crossover - {period_0}, '
                       '{period_1} Daily Close').format(symbol=security.symbol,
                                                        period_0=period_0,
                                                        period_1=period_1)
        chart = SecurityIndicatorChart(symbol=security.symbol,
                                       chart_date=date.today(),
                                       description=description,
                                       file_path=file_name,
                                       security_id=security.id)
        db.session.add(chart)
        db.session.commit()
        return redirect(url_for('security.view_security', security_id=security.id))
    return render_template('generate_wma_crossover.html', title='Generate WMA Crossover', form=form)


@bp.route('/view_security_indicator_chart/<chart_id>')
@login_required
def view_security_indicator_chart(chart_id):
    indicator_chart = SecurityIndicatorChart.query.get(int(chart_id))
    return render_template('view_security_indicator_chart.html',
                           title='Security Indicator Chart',
                           indicator_chart=indicator_chart)


@bp.route('/view_security_indicator_charts')
@login_required
def view_security_indicator_charts():
    indicator_charts = SecurityIndicatorChart.query.all()
    return render_template('view_security_indicator_charts.html',
                           title='Security Indicator Charts',
                           indicator_charts=indicator_charts)


@bp.route('/delete_security_indicator_chart/<chart_id>')
@login_required
def delete_security_indicator_chart(chart_id):
    chart = SecurityIndicatorChart.query.get(int(chart_id))
    db.session.delete(chart)
    db.session.commit()
    return redirect(url_for('security.view_security_indicator_charts'))


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
