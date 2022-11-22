from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,
                     DateField, SelectMultipleField, widgets, FloatField)
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo
from app.models import User, Security


class GetStartedForm(FlaskForm):
    client_file = FileField('Client File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    account_file = FileField('Account File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    transaction_file = FileField('Transaction File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Submit')


