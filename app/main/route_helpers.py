from app.models import Custodian, FeeSchedule
from werkzeug.utils import secure_filename
import os


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


def upload_file(file_object):
    filename = os.path.join('uploads/files/' + secure_filename(file_object.filename))
    file_object.save(filename)
    data_file = open(filename, 'r')
    data_file.readline()
    lines = data_file.readlines()
    data_file.close()
    return lines
