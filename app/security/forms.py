from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField)
from wtforms.validators import InputRequired, ValidationError
from app.models import Security


class NewSecurityForm(FlaskForm):
    symbol = StringField('Symbol', validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')

    @staticmethod
    def validate_symbol(self, symbol):
        security = Security.query.filter_by(symbol=symbol.data).first()
        if security is not None:
            raise ValidationError('A security already exists with that symbol.')


class AddSecurityForm(NewSecurityForm):
    submit = SubmitField('Save')


class EditSecurityForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')
