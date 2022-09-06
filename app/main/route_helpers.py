from app.models import Custodian, FeeSchedule, Quarter, Group, AccountSnapshot, Account, Client
from app import db
from werkzeug.utils import secure_filename
import os
from datetime import date


# PRE:  The Custodian data table must be defined with rows id and name
# POST: Returns a list of tuples (custodian.id, custodian.name) for each custodian in Custodian
def get_custodian_choices():
    custodians = Custodian.query.all()
    choices = []
    for custodian in custodians:
        choices.append((custodian.id, custodian.name))
    return choices


# PRE:  The FeeSchedule data table must be defined with rows id and name
# POST: Returns a list of tuples (fee_schedule.id, fee_schedule.name) for each fee_schedule in FeeSchedule
def get_fee_schedule_choices():
    fee_schedules = FeeSchedule.query.all()
    choices = [('None', 'Unassigned')]
    for fee_schedule in fee_schedules:
        choices.append((fee_schedule.id, fee_schedule.name))
    return choices


# PRE:  file_object is
# POST: The file associated with file_object has been saved. The file has been read with the first line
#        treated as a header. Every subsequent line is treated as data and is read and returned.
def upload_file(file_object):
    filename = os.path.join('uploads/files/' + secure_filename(file_object.filename))
    file_object.save(filename)
    data_file = open(filename, 'r')
    data_file.readline()
    lines = data_file.readlines()
    data_file.close()
    return lines


# PRE:  quarter_id is an integer representing a defined Quarter object stored in db
#       lines is a list of account snapshot data
# POST: For each line in lines, an account snapshot object has been created associated with quarter_id
def create_account_snapshots_from_file(quarter_id, lines):
    quarter = Quarter.query.get(quarter_id)
    for line in lines:
        data = line.split(',')
        snapshot_date = date.fromisoformat(data[0].strip())
        account_number = data[1].strip()
        market_value = float(data[4].strip())
        group_name = data[8].strip()
        group = Group.query.filter_by(name=group_name).first()
        account = Account.query.filter_by(account_number=account_number).first()
        if group is not None and account is not None:
            # ASSERT: Neither group nor account are undefined
            snapshot = AccountSnapshot(date=snapshot_date, market_value=market_value,
                                       account_id=account.id, quarter_id=quarter_id, group_id=group.id)
            snapshot.calculate_fee()
            quarter.aum += market_value
            quarter.fee += snapshot.fee
            db.session.add(snapshot)
    db.session.add(quarter)
    db.session.commit()
