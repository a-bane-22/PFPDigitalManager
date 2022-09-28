from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')
