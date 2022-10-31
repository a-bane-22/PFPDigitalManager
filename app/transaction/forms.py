from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,
                     DateField, SelectMultipleField, widgets, FloatField)
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo
from app.models import User, Security


class TransactionForm(FlaskForm):
    date = DateField('Date')
    type = SelectField('Type')
    security = SelectField('Security')
    quantity = FloatField('Quantity', validators=[InputRequired()])
    share_price = FloatField('Share Price', validators=[InputRequired()])
    gross_amount = FloatField('Gross Amount', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')
