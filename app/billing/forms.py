from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField, DateField, SelectMultipleField, FloatField)
from wtforms.validators import InputRequired


class QuarterForm(FlaskForm):
    from_date = DateField('From', validators=[InputRequired()])
    to_date = DateField('To', validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired()])


class AddQuarterForm(QuarterForm):
    account_file = FileField('Account File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Save')


class EditQuarterForm(QuarterForm):
    submit = SubmitField('Save')


class FeeScheduleForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Save')


class FeeRuleForm(FlaskForm):
    minimum = FloatField('Minimum', validators=[InputRequired()])
    maximum = FloatField('Maximum', validators=[InputRequired()])
    rate = FloatField('Rate', validators=[InputRequired()])
    flat = FloatField('Flat Fee', validators=[InputRequired()])
    submit = SubmitField('Save')


class AssignFeeScheduleForm(FlaskForm):
    accounts = SelectMultipleField('Accounts', coerce=int)
    submit = SubmitField('Assign')
