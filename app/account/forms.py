from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, BooleanField, SubmitField, SelectField, FloatField)
from wtforms.validators import InputRequired


class AccountForm(FlaskForm):
    custodian = SelectField('Custodian')
    account_number = StringField('Account Number')
    description = StringField('Description', validators=[InputRequired()])
    billable = BooleanField('Billable')
    discretionary = BooleanField('Discretionary')
    fee_schedule = SelectField('Fee Schedule')
    submit = SubmitField('Save')


class AccountSnapshotForm(FlaskForm):
    quarter = SelectField('Quarter', validators=[InputRequired()])
    market_value = FloatField('Market Value', validators=[InputRequired()])
    submit = SubmitField('Save')


class CustodianForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')
