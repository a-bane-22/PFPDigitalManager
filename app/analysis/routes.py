from flask import render_template, flash, redirect, url_for
from flask_login import current_user, logout_user, login_required
from app import db
from app.analysis import bp
from app.analysis.forms import UploadFileForm
from app.analysis.route_helpers import sort_ranked_securities
from app.route_helpers import upload_file
from app.models import Security


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
