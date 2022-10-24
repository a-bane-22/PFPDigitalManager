from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Account, Client, Quarter, FeeRule, FeeSchedule, Group,
                        GroupSnapshot, AccountSnapshot)
from app.billing.forms import (QuarterForm, AccountSnapshotForm, FeeRuleForm, FeeScheduleForm,
                               AssignFeeScheduleToGroupForm, AssignFeeScheduleToGroupsForm, UploadFileForm, ExportToFileForm,
                               GenerateFeesByAccountForm)
from app.billing import bp
from app.billing.route_helpers import (generate_group_fees, generate_account_fees)
from app.route_helpers import upload_file
from datetime import date
import os
from werkzeug.utils import secure_filename


@bp.route('/billing_index')
@login_required
def billing_index():
    return render_template('billing_index.html', title='Billing Index')


@bp.route('/view_quarters')
@login_required
def view_quarters():
    quarters = Quarter.query.all()
    return render_template('view_quarters.html', title='View Quarters', quarters=quarters)


@bp.route('/view_quarter/<quarter_id>')
@login_required
def view_quarter(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    return render_template('view_quarter.html', title='View Quarter', quarter=quarter)


@bp.route('/add_quarter', methods=['GET', 'POST'])
@login_required
def add_quarter():
    form = QuarterForm()
    if form.validate_on_submit():
        quarter = Quarter(from_date=form.from_date.data, to_date=form.to_date.data, name=form.name.data,
                          aum=0, fee=0)
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


@bp.route('/view_account_snapshots')
@login_required
def view_account_snapshots():
    snapshots = AccountSnapshot.query.all()
    return render_template('view_account_snapshots.html', title='Account Snapshots', snapshots=snapshots)


@bp.route('/view_account_snapshot/<snapshot_id>')
@login_required
def view_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    return render_template('view_account_snapshot.html', title='Account Snapshot', snapshot=snapshot)


@bp.route('/create_account_snapshot/<account_id>', methods=['GET', 'POST'])
@login_required
def add_account_snapshot(account_id):
    form = AccountSnapshotForm()
    quarters = Quarter.query.all()
    choices = []
    for quarter in quarters:
        choices.append((quarter.id, quarter.name))
    form.quarter.choices = choices
    if form.validate_on_submit():
        account = Account.query.get(int(account_id))
        quarter = Quarter.query.get(form.quarter.data)
        client = Client.query.get(account.client_id)
        group = Group.query.get(account.group_id)
        group_snapshot = GroupSnapshot.query.filter_by(group_id=group.id, quarter_id=quarter.id).first()
        if group_snapshot is None:
            name = '{group_name} - {quarter_name}'.format(group_name=group.name, quarter_name=quarter.name)
            group_snapshot = GroupSnapshot(date=date.today(), name=name, group_name=group.name,
                                           quarter_name=quarter.name, group_id=group.id,
                                           quarter_id=quarter.id, market_value=form.market_value.data,
                                           fee=0, fee_schedule_id=group.fee_schedule_id)
        else:
            group_snapshot.market_value += form.market_value.data
        db.session.add(group_snapshot)
        name = '{account_number} - {quarter_name}'.format(account_number=account.account_number,
                                                          quarter_name=quarter.name)
        snapshot = AccountSnapshot(name=name,
                                   account_number=account.account_number,
                                   description=account.description,
                                   billable=account.billable,
                                   discretionary=account.discretionary,
                                   client_name=client.get_name(),
                                   group_name=group.name,
                                   custodian=account.get_custodian_name(),
                                   account_id=account.id,
                                   client_id=client.id,
                                   market_value=form.market_value.data,
                                   date=date.today(),
                                   quarter_name=quarter.name,
                                   quarter_id=quarter.id,
                                   group_snapshot_id=group_snapshot.id)
        db.session.add(snapshot)
        db.session.commit()
        return redirect(url_for('billing.view_account_snapshot', snapshot_id=snapshot.id))
    return render_template('add_account_snapshot.html', title='Add Account Snapshot', form=form)


@bp.route('/upload_account_values/<quarter_id>', methods=['GET', 'POST'])
@login_required
def upload_account_values(quarter_id):
    form = UploadFileForm()
    if form.validate_on_submit():
        quarter = Quarter.query.get(int(quarter_id))
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        for line in lines:
            data = line.split(',')
            snapshot_date = date.fromisoformat(data[0].strip())
            account_number = data[1].strip()
            market_value = float(data[4].strip())
            name = '{account_number} - {quarter_name}'.format(account_number=account_number,
                                                              quarter_name=quarter.name)
            account = Account.query.filter_by(account_number=account_number).first()
            if account is not None:
                client = Client.query.get(account.client_id)
                group = Group.query.get(account.group_id)
                group_snapshot = GroupSnapshot.query.filter_by(group_id=group.id, quarter_id=quarter.id).first()
                if group_snapshot is None:
                    name = '{group_name} - {quarter_name}'.format(group_name=group.name, quarter_name=quarter.name)
                    group_snapshot = GroupSnapshot(date=date.today(), name=name, group_name=group.name,
                                                   quarter_name=quarter.name, group_id=group.id,
                                                   quarter_id=quarter.id, market_value=market_value,
                                                   fee=0, fee_schedule_id=group.fee_schedule_id)
                else:
                    group_snapshot.market_value += market_value
                db.session.add(group_snapshot)
                snapshot = AccountSnapshot(name=name,
                                           account_number=account.account_number,
                                           description=account.description,
                                           billable=account.billable,
                                           discretionary=account.discretionary,
                                           client_name=client.get_name(),
                                           group_name=group.name,
                                           custodian=account.get_custodian_name(),
                                           account_id=account.id,
                                           client_id=client.id,
                                           market_value=market_value,
                                           date=snapshot_date,
                                           quarter_name=quarter.name,
                                           quarter_id=quarter.id,
                                           group_snapshot_id=group_snapshot.id)
                db.session.add(snapshot)
            else:
                snapshot = AccountSnapshot(name=name,
                                           account_number=account_number,
                                           date=snapshot_date,
                                           market_value=market_value)
                db.session.add(snapshot)
        return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))
    return render_template('upload_account_values.html', title='Upload Account Values', form=form)


@bp.route('/delete_account_snapshot/<snapshot_id>')
@login_required
def delete_account_snapshot(snapshot_id):
    snapshot = AccountSnapshot.query.get(int(snapshot_id))
    db.session.delete(snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_account_snapshots'))


@bp.route('/delete_all_account_snapshots')
@login_required
def delete_all_account_snapshots():
    AccountSnapshot.query.delete()
    quarters = Quarter.query.all()
    for quarter in quarters:
        quarter.aum = 0
        quarter.fee = 0
        db.session.add(quarter)
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/view_group_snapshots')
@login_required
def view_group_snapshots():
    snapshots = GroupSnapshot.query.all()
    return render_template('view_group_snapshots.html', title='Group Snapshots', snapshots=snapshots)


@bp.route('/view_group_snapshot/<snapshot_id>')
@login_required
def view_group_snapshot(snapshot_id):
    snapshot = GroupSnapshot.query.get(int(snapshot_id))
    return render_template('view_group_snapshot.html', title='Group Snapshot', snapshot=snapshot)


@bp.route('/delete_group_snapshot/<snapshot_id>')
@login_required
def delete_group_snapshot(snapshot_id):
    snapshot = GroupSnapshot.query.get(int(snapshot_id))
    for account_snapshot in snapshot.account_snapshots:
        account_snapshot.group_snapshot_id = None
    db.session.delete(snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_group_snapshots'))


@bp.route('/delete_all_group_snapshots')
@login_required
def delete_all_group_snapshots():
    snapshots = GroupSnapshot.query.all()
    for snapshot in snapshots:
        for account_snapshot in snapshot.account_snapshots:
            account_snapshot.group_snapshot_id = None
        db.session.delete(snapshot)
    db.session.commit()
    return redirect(url_for('main.index'))

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


@bp.route('/upload_fee_schedules', methods=['GET', 'POST'])
@login_required
def upload_fee_schedules():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        for line in lines:
            data = line.split(',')
            name = data[0].strip()
            minimum = float(data[1].strip())
            maximum = float(data[2].strip())
            rate = float(data[3].strip())
            flat = float(data[4].strip())
            fee_schedule = FeeSchedule.query.filter_by(name=name).first()
            if fee_schedule is None:
                fee_schedule = FeeSchedule(name=name)
                db.session.add(fee_schedule)
            fee_rule = FeeRule(minimum=minimum, maximum=maximum, rate=rate,
                               flat=flat, schedule_id=fee_schedule.id)
            db.session.add(fee_rule)
        db.session.commit()
        return redirect(url_for('billing.view_fee_schedules'))
    return render_template('upload_fee_schedules.html', title='Upload Fee Schedules', form=form)


@bp.route('/export_fee_schedules', methods=['GET', 'POST'])
@login_required
def export_fee_schedules():
    form = ExportToFileForm()
    if form.validate_on_submit():
        filename = os.path.join('exports/' + secure_filename(form.filename.data))
        with open(filename, 'w') as export_file:
            header = 'Schedule Name,Minimum,Maximum,Rate,Flat\n'
            export_file.write(header)
            fee_schedules = FeeSchedule.query.all()
            for schedule in fee_schedules:
                for rule in schedule.rules:
                    export_file.write(rule.export_fee_rule_csv() + '\n')
        return redirect(url_for('main.index'))
    return render_template('export_fee_schedules.html', title='Export Fee Schedules', form=form)


@bp.route('/assign_fee_schedule_to_groups/<schedule_id>', methods=['GET', 'POST'])
@login_required
def assign_fee_schedule_to_groups(schedule_id):
    schedule = FeeSchedule.query.get(int(schedule_id))
    form = AssignFeeScheduleToGroupsForm()
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
    return render_template('assign_fee_schedule_to_groups.html', title='Assign Fee Schedule', form=form, schedule=schedule)


@bp.route('/assign_fee_schedule_to_group/<group_id>', methods=['GET', 'POST'])
@login_required
def assign_fee_schedule_to_group(group_id):
    form = AssignFeeScheduleToGroupForm()
    schedules = FeeSchedule.query.all()
    form.fee_schedule.choices = [(schedule.id, schedule.name) for schedule in schedules]
    form.fee_schedule.size = len(schedules)
    if form.validate_on_submit():
        group = Group.query.get(int(group_id))
        group.fee_schedule_id = form.fee_schedule.data
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('client.view_group', group_id=group_id))
    return render_template('assign_fee_schedule_to_group.html', title='Assign Fee Schedule', form=form)


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


@bp.route('/generate_group_snapshots/<quarter_id>')
@login_required
def generate_group_snapshots(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    account_snapshots = AccountSnapshot.query.filter_by(quarter_id=quarter.id,
                                                        group_snapshot_id=None)
    for account_snapshot in account_snapshots:
        account = Account.query.get(account_snapshot.account_id)
        group = Group.query.get(account.group_id)
        if group is not None:
            group_snapshot = GroupSnapshot.query.filter_by(quarter_id=quarter.id, group_id=group.id).first()
            if group_snapshot is not None:
                name = '{group_name} - {quarter_name}'.format(group_name=group.name, quarter_name=quarter.name)
                group_snapshot = GroupSnapshot(date=date.today(), name=name,
                                               group_name=group.name,
                                               quarter_name=quarter.name,
                                               market_value=account_snapshot.market_value,
                                               fee=0, fee_schedule_id=group.fee_schedule_id,
                                               group_id=group.id, quarter_id=quarter.id)
            else:
                group_snapshot.market_value += account_snapshot.market_value
            db.session.add(group_snapshot)
            account_snapshot.group_snapshot_id = group_snapshot.id
            db.session.add(group_snapshot)
    db.session.commit()
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))


@bp.route('/calculate_fees/<quarter_id>')
@login_required
def calculate_fees(quarter_id):
    generate_group_fees(quarter_id=quarter_id)
    generate_account_fees(quarter_id=quarter_id)
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))


@bp.route('/update_quarter_data/<quarter_id>')
@login_required
def update_quarter_data(quarter_id):
    quarter = Quarter.query.get(int(quarter_id))
    quarter.aum = 0
    quarter.fee = 0
    for group_snapshot in quarter.group_snapshots:
        quarter.aum += group_snapshot.market_value
        quarter.fee += group_snapshot.fee
    db.session.add(quarter)
    db.session.commit()
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))


@bp.route('/export_quarter_csv/<quarter_id>')
@login_required
def export_quarter_csv(quarter_id):
    group_filename = 'groups'
    account_filename = 'accounts'
    with open(group_filename, 'w') as group_file:
        header = 'Group,Market Value,Fee\n'
        group_file.write(header)
        group_snapshots = GroupSnapshot.query.filter_by(quarter_id=quarter_id).all()
        for snapshot in group_snapshots:
            group_file.write(snapshot.export_to_csv() + '\n')
    with open(account_filename, 'w') as account_file:
        header = ('Account Number,Group Name,Group Market Value,' +
                  'Account Market Value,Account Weight,Group Fee,' +
                  'Account Fee\n')
        account_file.write(header)
        account_snapshots = AccountSnapshot.query.filter_by(quarter_id=quarter_id).all()
        for snapshot in account_snapshots:
            account_file.write(snapshot.export_to_csv() + '\n')
    return redirect(url_for('billing.view_quarter', quarter_id=quarter_id))
