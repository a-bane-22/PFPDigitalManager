from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Account, Quarter, FeeRule, FeeSchedule, Group, GroupSnapshot, AccountSnapshot)
from app.billing.forms import (QuarterForm, FeeRuleForm, FeeScheduleForm,
                               AssignFeeScheduleForm, UploadFileForm, GenerateFeesByAccountForm)
from app.billing import bp
from app.billing.route_helpers import (write_tda_group_value, write_tda_fee_by_account)
from app.route_helpers import upload_file
from datetime import date


@bp.route('/view_quarters')
@login_required
def view_quarters():
    quarters = Quarter.query.all()
    return render_template('view_quarters.html', title='View Quarters', quarters=quarters)


@bp.route('/view_quarter/<quarter_id>')
@login_required
def view_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    group_snapshots = quarter.group_snapshots
    snapshots = quarter.account_snapshots
    return render_template('view_quarter.html', title='View Quarter', quarter=quarter,
                           group_snapshots=group_snapshots)


@bp.route('/add_quarter', methods=['GET', 'POST'])
@login_required
def add_quarter():
    form = QuarterForm()
    if form.validate_on_submit():
        quarter = Quarter(from_date=form.from_date.data, to_date=form.to_date.data, name=form.name.data,
                          aum=0)
        db.session.add(quarter)
        db.session.commit()
        return redirect(url_for('billing.view_quarter', quarter_id=quarter.id))
    return render_template('add_quarter.html', title='Add Quarter', form=form)


@bp.route('/edit_quarter/<quarter_id>', methods=['GET', 'POST'])
@login_required
def edit_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    form = QuarterForm()
    if form.validate_on_submit():
        quarter.from_date = form.from_date.data
        quarter.to_date = form.to_date.data
        quarter.name = form.name.data
        db.session.add(quarter)
        db.session.commit()
        return redirect(url_for('billing.view_quarter', quarter_id=quarter.id))
    form.from_date.data = quarter.from_date
    form.to_date.data = quarter.to_date
    form.name.data = quarter.name
    return render_template('edit_quarter.html', title='Edit Quarter', form=form)


@bp.route('/delete_quarter/<quarter_id>')
@login_required
def delete_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for group_snapshot in quarter.group_snapshots:
        for account_snapshot in group_snapshot.account_snapshots:
            db.session.delete(account_snapshot)
        db.session.delete(group_snapshot)
    db.session.delete(quarter)
    db.session.commit()
    return redirect(url_for('billing.view_quarters'))


@bp.route('/view_fee_schedules')
@login_required
def view_fee_schedules():
    schedules = FeeSchedule.query.all()
    return render_template('view_fee_schedules.html', title='Fee Schedules', schedules=schedules)


@bp.route('/view_fee_schedule/<schedule_id>')
@login_required
def view_fee_schedule(schedule_id):
    schedule = FeeSchedule.query.get(int(schedule_id))
    return render_template('view_fee_schedule.html', title='Fee Schedule', schedule=schedule)


@bp.route('/add_fee_schedule', methods=['GET', 'POST'])
@login_required
def add_fee_schedule():
    form = FeeScheduleForm()
    if form.validate_on_submit():
        schedule = FeeSchedule(name=form.name.data)
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedule', schedule_id=schedule.id))
    return render_template('add_fee_schedule.html', title='Add Fee Schedule', form=form)


@bp.route('/edit_fee_schedule/<schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_fee_schedule(schedule_id):
    schedule = FeeSchedule.query.get(int(schedule_id))
    form = FeeScheduleForm()
    if form.validate_on_submit():
        schedule.name = form.name.data
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedule', schedule_id=schedule.id))
    form.name.data = schedule.name
    return render_template('edit_fee_schedule.html', title='Edit Fee Schedule', form=form)


@bp.route('/assign_fee_schedule/<schedule_id>', methods=['GET', 'POST'])
@login_required
def assign_fee_schedule(schedule_id):
    schedule = FeeSchedule.query.get(int(schedule_id))
    form = AssignFeeScheduleForm()
    groups = Group.query.filter_by(fee_schedule_id=None)
    choices = []
    for group in groups:
        choices.append((group.id, group.name))
    form.groups.choices = choices
    form.groups.size = len(choices)
    if form.validate_on_submit():
        assigned_groups = form.groups.data
        for group_id in assigned_groups:
            group = Group.query.get(int(group_id))
            group.fee_schedule_id = schedule.id
            db.session.add(group)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedule', schedule_id=schedule_id))
    return render_template('assign_fee_schedule.html', title='Assign Fee Schedule', form=form, schedule=schedule)


@bp.route('/delete_fee_schedule/<schedule_id>')
@login_required
def delete_fee_schedule(schedule_id):
    schedule = FeeSchedule.query.get(int(schedule_id))
    for rule in schedule.rules:
        db.session.delete(rule)
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for('billing.view_fee_schedules'))


@bp.route('/add_fee_rule/<schedule_id>', methods=['GET', 'POST'])
@login_required
def add_fee_rule(schedule_id):
    form = FeeRuleForm()
    if form.validate_on_submit():
        rule = FeeRule(minimum=form.minimum.data, maximum=form.maximum.data, rate=form.rate.data,
                       flat=form.flat.data, schedule_id=int(schedule_id))
        db.session.add(rule)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedule', schedule_id=schedule_id))
    return render_template('add_fee_rule.html', title='Add Fee Rule', form=form)


@bp.route('/edit_fee_rule/<rule_id>', methods=['GET', 'POST'])
@login_required
def edit_fee_rule(rule_id):
    rule = FeeRule.query.get(int(rule_id))
    form = FeeRuleForm()
    if form.validate_on_submit():
        rule.minimum = form.minimum.data
        rule.maximum = form.maximum.data
        rule.rate = form.rate.data
        rule.flat = form.flat.data
        db.session.add(rule)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedule', schedule_id=rule.schedule_id))
    form.minimum.data = rule.minimum
    form.maximum.data = rule.maximum
    form.rate.data = rule.rate
    form.flat.data = rule.flat
    return render_template('edit_fee_rule.html', title='Edit Fee Rule', form=form)


@bp.route('/delete_fee_rule/<rule_id>')
@login_required
def delete_fee_rule(rule_id):
    rule = FeeRule.query.get(int(rule_id))
    schedule_id = rule.schedule_id
    db.session.delete(rule)
    db.session.commit()
    return redirect(url_for('billing.view_fee_schedule', schedule_id=schedule_id))


@bp.route('/upload_account_values/<quarter_id>', methods=['GET', 'POST'])
@login_required
def upload_account_values(quarter_id):
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        for line in lines:
            data = line.split(',')
            snapshot_date = date.fromisoformat(data[0].strip())
            account_number = data[1].strip()
            market_value = float(data[4].strip())
            account_id = None
            account = Account.query.filter_by(account_number=account_number).first()
            if account is not None:
                account_id = account.id
            snapshot = AccountSnapshot(date=snapshot_date, market_value=market_value,
                                       billable=account.billable,
                                       account_id=account_id, quarter_id=quarter_id)
            db.session.add(snapshot)
        return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))
    return render_template('upload_account_values.html', title='Upload Account Values', form=form)


@bp.route('/generate_group_snapshots/<quarter_id>')
@login_required
def generate_group_snapshots(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for account_snapshot in quarter.account_snapshots:
        account = Account.query.get(account_snapshot.account_id)
        group = Group.query.get(account.group_id)
        if group is not None:
            group_snapshot = GroupSnapshot.query.filter_by(quarter_id=quarter.id, group_id=group.id).first()
            if group_snapshot is not None:
                group_snapshot = GroupSnapshot(date=date.today(), market_value=account_snapshot.market_value,
                                               group_id=group.id, quarter_id=quarter.id)
            else:
                group_snapshot.market_value += account_snapshot.market_value
            db.session.add(group_snapshot)
            account_snapshot.group_snapshot_id = group_snapshot.id
            db.session.add(group_snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))


@bp.route('/calculate_group_fees/<quarter_id>')
@login_required
def calculate_group_fees(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for group_snapshot in quarter.group_snapshots:
        fee_schedule = FeeSchedule.query.get(group_snapshot.fee_schedule_id)
        group_snapshot.fee = fee_schedule.calculate_fee(value=group_snapshot.market_value)
        db.session.add(group_snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))


@bp.route('/calculate_account_fees/<quarter_id>')
@login_required
def calculate_account_fees(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for group_snapshot in quarter.group_snapshots:
        group_market_value = group_snapshot.market_value
        for account_snapshot in group_snapshot.account_snapshots:
            if account_snapshot.billable:
                account_snapshot.group_weight = round(account_snapshot.market_value/group_market_value)
                account_snapshot.fee = group_snapshot.fee * account_snapshot.group_weight
                db.session.add(account_snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))
