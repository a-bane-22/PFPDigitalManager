from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Account, Quarter, FeeRule, FeeSchedule)
from app.billing.forms import (AddQuarterForm, EditQuarterForm, FeeRuleForm, FeeScheduleForm, AssignFeeScheduleForm)
from app.billing import bp
from app.route_helpers import (upload_file, create_account_snapshots_from_file)


@bp.route('/view_quarters')
@login_required
def view_quarters():
    quarters = Quarter.query.all()
    return render_template('view_quarters.html', title='View Quarters', quarters=quarters)


@bp.route('/view_quarter/<quarter_id>')
@login_required
def view_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    snapshots = quarter.account_snapshots
    return render_template('view_quarter.html', title='View Quarter', quarter=quarter, snapshots=snapshots)


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
        lines = upload_file(file_object=f)
        create_account_snapshots_from_file(quarter_id=quarter.id, lines=lines)
        return redirect(url_for('billing.view_quarter', quarter_id=quarter.id))
    return render_template('add_quarter.html', title='Add Quarter', form=form)


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
        return redirect(url_for('billing.view_quarter', quarter_id=quarter.id))
    form.from_date.data = quarter.from_date
    form.to_date.data = quarter.to_date
    form.name.data = quarter.name
    return render_template('edit_quarter.html', title='Edit Quarter', form=form)


@bp.route('/delete_quarter/<quarter_id>')
@login_required
def delete_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    for snapshot in quarter.account_snapshots:
        db.session.delete(snapshot)
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
    accounts = Account.query.filter_by(billable=True, schedule_id=None)
    choices = []
    for account in accounts:
        choices.append((account.id, account.account_number))
    form.accounts.choices = choices
    form.accounts.size = len(choices)
    if form.validate_on_submit():
        assigned_accounts = form.accounts.data
        for account_id in assigned_accounts:
            account = Account.query.get(int(account_id))
            account.schedule_id = schedule.id
            db.session.add(account)
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
