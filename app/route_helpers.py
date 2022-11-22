from app import db
from app.models import (Client, Account, Transaction, Custodian,
                        Position, Group, FeeSchedule, Security)
from werkzeug.utils import secure_filename
import os
import xml.etree.ElementTree as ET
from datetime import date


# PRE:  The Custodian data table must be defined with rows id and name
# POST: Returns a list of tuples (custodian.id, custodian.name) for each custodian in Custodian
def get_custodian_choices():
    custodians = Custodian.query.all()
    choices = [(custodian.id, custodian.name) for custodian in custodians]
    return choices


# PRE:  The FeeSchedule data table must be defined with rows id and name
# POST: Returns a list of tuples (fee_schedule.id, fee_schedule.name) for each fee_schedule in FeeSchedule
def get_fee_schedule_choices():
    fee_schedules = FeeSchedule.query.all()
    choices = [('None', 'Unassigned')] + [(fee_schedule.id, fee_schedule.name) for fee_schedule in fee_schedules]
    return choices


# PRE:  The Security data table must be defined with rows id and name
# POST: Returns a list of tuples (security.id, security.name) for each security in Security
def get_security_choices():
    securities = Security.query.all()
    choices = [(security.id, security.name) for security in securities]
    return choices


# PRE:  file_object is a file uploaded via HTML form
# POST: The file associated with file_object has been saved. The file has been read with the first line
#        treated as a header. Every subsequent line is treated as data and is read and returned.
def upload_file(file_object):
    filename = os.path.join('uploads/files/' + secure_filename(file_object.filename))
    file_object.save(filename)
    with open(filename, 'r') as data_file:
        data_file.readline()
        lines = data_file.readlines()
        return lines


# PRE:  file_object is a file uploaded via HTML form with format .xml
# POST: The file associated with file_object has been saved and the data has been parsed into
#        an ElementTree. The ElementTree is returned.
def upload_xml_file(file_object):
    filename = os.path.join('uploads/files/' + secure_filename(file_object.filename))
    file_object.save(filename)
    tree = ET.parse(filename)
    return tree


# Pre:  file_object is a file uploaded via HTML form with format .csv
#        containing client data
# Post:
def process_client_csv_file(file_object):
    lines = upload_file(file_object=file_object)
    data = [line.strip().split(',') for line in lines]
    for line in data:
        group_name = line[8].strip()
        group_id = None
        assigned = False
        if group_name is not None:
            assigned = True
            group = Group.query.filter_by(name=group_name).first()
            if group is None:
                group = Group(name=group_name)
                db.session.add(group)
                db.session.commit()
            group_id = group.id
        client = Client(first_name=line[0].strip(),
                        middle_name=line[1].strip(),
                        last_name=line[2].strip(),
                        dob=date.fromisoformat(data[3].strip()),
                        email=line[4].strip(),
                        cell_phone=line[5].strip(),
                        work_phone=line[6].strip(),
                        home_phone=line[7].strip(),
                        group_id=group_id,
                        assigned=assigned)
        db.session.add(client)
    db.session.commit()


# Pre:
# Post:
def process_account_csv_file(file_object):
    lines = upload_file(file_object=file_object)
    data = [line.split(',') for line in lines]
    for line in data:
        client_first = line[2].strip()
        client_last = line[3].strip()
        custodian_name = line[4].strip()
        client = Client.query.filter_by(first_name=client_first, last_name=client_last).first()
        if client is not None:
            custodian = Custodian.query.filter_by(name=custodian_name).first()
            if custodian is None:
                custodian = Custodian(name=custodian_name)
                db.session.add(custodian)
                db.session.commit()
            account = Account(account_number=line[0].strip(),
                              description=line[1].strip(),
                              billable=(line[5].strip.lower() == 'true'),
                              discretionary=(line[6].strip().lower() == 'true'),
                              client_id=client.id,
                              group_id=client.group_id,
                              custodian_id=custodian.id)
            db.session.add(account)
    db.session.commit()


# Pre:
# Post:
def process_transaction_csv_file(file_object):
    lines = upload_file(file_object=file_object)
    data = [line.split(',') for line in lines]
    for line in data:
        symbol = data[3].strip()
        name = data[4].strip()
        account = Account.query.filter_by(account_number=line[1].strip()).first()
        if account is not None:
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
            transaction = Transaction(date=date.fromisoformat(line[0].strip()),
                                      type=line[2].strip(),
                                      quantity=float(line[5].strip()),
                                      share_price=float(line[6].strip()),
                                      gross_amount=float(line[7].strip()),
                                      description=line[8].strip(),
                                      account_id=account.id,
                                      security_id=security.id,
                                      position_id=position.id)
            position.add_transaction(transaction_type=transaction.type, quantity=transaction.quantity,
                                     gross_amount=transaction.gross_amount)
            db.session.add(transaction)
            db.session.add(position)
    db.session.commit()
