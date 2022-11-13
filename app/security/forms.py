from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField, IntegerField)
from wtforms.validators import InputRequired, ValidationError
from app.models import Security


class AddSecurityForm(FlaskForm):
    symbol = StringField('Symbol', validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')

    @staticmethod
    def validate_symbol(self, symbol):
        security = Security.query.filter_by(symbol=symbol.data).first()
        if security is not None:
            raise ValidationError('A security already exists with that symbol.')


class EditSecurityForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class WMACrossoverForm(FlaskForm):
    period_0 = IntegerField('Period', validators=[InputRequired()])
    period_1 = IntegerField('Different Period', validators=[InputRequired()])
    num_points = IntegerField('Number of Data Points', validators=[InputRequired()])
    submit = SubmitField('Submit')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')
