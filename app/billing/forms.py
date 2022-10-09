from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField, DateField, SelectField, SelectMultipleField,
                     FloatField)
from wtforms.validators import InputRequired, ValidationError, Optional


class QuarterForm(FlaskForm):
    from_date = DateField('From', validators=[InputRequired()])
    to_date = DateField('To', validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Save')


class AccountSnapshotForm(FlaskForm):
    quarter = SelectField('Quarter', validators=[InputRequired()])
    market_value = FloatField('Market Value', validators=[InputRequired()])
    submit = SubmitField('Save')


class FeeScheduleForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Save')


class FeeRuleForm(FlaskForm):
    minimum = FloatField('Minimum', validators=[InputRequired()])
    maximum = FloatField('Maximum', validators=[Optional()])
    rate = FloatField('Rate', validators=[InputRequired()])
    flat = FloatField('Flat Fee', validators=[InputRequired()])
    submit = SubmitField('Save')

    def validate_minimum(self, minimum):
        if minimum.data < 0:
            raise ValidationError('Invalid minimum')


class AssignFeeScheduleForm(FlaskForm):
    groups = SelectMultipleField('Groups', coerce=int)
    submit = SubmitField('Assign')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')


class GenerateFeesByAccountForm(FlaskForm):
    account_file = FileField('Account File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    group_file = FileField('Group File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')