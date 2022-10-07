from app.models import Custodian, FeeSchedule, Security
from werkzeug.utils import secure_filename
import os
import xml.etree.ElementTree as ET


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
