from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField, SelectField,
                     DateField, FloatField)
from wtforms.validators import InputRequired, ValidationError


class AddOptionQuoteForm(FlaskForm):
    type = SelectField('Type',
                       choices=[('call', 'Call'), ('put', 'Put')],
                       validators=[InputRequired()])
    expiration_date = DateField('Expiration Date',
                                validators=[InputRequired()])
    strike_price = FloatField('Strike Price',
                              validators=[InputRequired()])
    bid = FloatField('Bid',
                     validators=[InputRequired()])
    ask = FloatField('Ask',
                     validators=[InputRequired()])
    last = FloatField('Last',
                      validators=[InputRequired()])
    high = FloatField('High',
                      validators=[InputRequired()])
    low = FloatField('Low',
                     validators=[InputRequired()])
    change = FloatField('Change',
                        validators=[InputRequired()])
    volume = FloatField('Volume',
                        validators=[InputRequired()])
    open_interest = FloatField('Open Interest',
                               validators=[InputRequired()])
    submit = SubmitField('Submit')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')
