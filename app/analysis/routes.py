from flask import render_template, flash, redirect, url_for
from flask_login import current_user, logout_user, login_required
from app import db
from app.analysis import bp
from app.analysis.forms import UploadFileForm, GenerateFeesByAccountForm
from app.analysis.route_helpers import sort_ranked_securities
from app.route_helpers import upload_file, upload_xml_file
from app.models import Security
from alpha_vantage.timeseries import TimeSeries


@bp.route('/rank_securities', methods=['GET', 'POST'])
@login_required
def rank_securities():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        benchmark_data = lines.pop(0).split(',')
        benchmark_symbol = benchmark_data[0].strip()
        benchmark_name = benchmark_data[1].strip()
        benchmark_risk = float(benchmark_data[2].strip())
        benchmark_mean = float(benchmark_data[3].strip())
        benchmark_ratio = benchmark_mean/benchmark_risk
        benchmark = [benchmark_symbol, benchmark_name, benchmark_risk,
                     benchmark_mean, benchmark_ratio]
        security_list = []
        for line in lines:
            data = line.split(',')
            symbol = data[0].strip()
            name = data[1].strip()
            risk = float(data[2].strip())
            mean = float(data[3].strip())
            quadrant = 0
            if mean < benchmark_mean:
                if risk < benchmark_risk:
                    quadrant = 3
                else:
                    quadrant = 4
            elif mean > benchmark_mean:
                if risk < benchmark_risk:
                    quadrant = 2
                else:
                    quadrant = 1
            ratio = mean/risk
            security_list.append((symbol, name, risk, mean, quadrant, ratio))
        security_list.sort(key=sort_ranked_securities)
        return render_template('rank_securities_display.html', title='Rank Securities',
                               benchmark=benchmark, security_list=security_list)
    return render_template('rank_securities.html', title='Rank Securities', form=form)


@bp.route('/calculate_alpha', methods=['GET', 'POST'])
@login_required
def calculate_alpha():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        benchmark_portfolio = {'quantity': 0, 'cash': 0}
        portfolio = {'cost': 0, 'cash': 0}
        benchmark_final_value = 0
        for line in lines:
            data = line.split(',')
            transaction_date = data[0].strip()
            transaction_type = data[1].strip()
            symbol = data[2].strip()
            name = data[3].strip()
            market_price = float(data[4].strip())
            num_shares = float(data[5].strip())
            cost = float(data[6].strip())
            benchmark_market_price = float(data[7].strip())
            if transaction_type == 'BUY':
                benchmark_quantity = cost / benchmark_market_price
                benchmark_portfolio['quantity'] += benchmark_quantity
                portfolio['cost'] += cost
            elif transaction_type == 'SELL':
                benchmark_portfolio['quantity'] -= cost / benchmark_market_price
                portfolio['cost'] -= cost
            elif transaction_type == 'DEPOSIT':
                benchmark_portfolio['cash'] += cost
                portfolio += cost
            elif transaction_type == 'WITHDRAW':
                benchmark_portfolio['cash'] -= cost
                portfolio -= cost
        portfolio_value = 0
        benchmark_portfolio_value = benchmark_portfolio['quantity'] * benchmark_final_value
        return render_template('calculate_alpha_display.html', title='Calculate Alpha',
                               portfolio_value=portfolio_value,
                               benchmark_portfolio_value=benchmark_portfolio_value)
    return render_template('calculate_alpha.html', title='Calculate Alpha', form=form)
