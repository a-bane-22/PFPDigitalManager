from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, SubmitField, RadioField, DateField, SelectMultipleField, widgets)
from wtforms.validators import InputRequired, Email


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ClientInformationForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    middle_name = StringField('Middle Name')
    dob = DateField('DOB', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    cell_phone = StringField('Cell Phone')
    home_phone = StringField('Home Phone')
    work_phone = StringField('Work Phone')
    submit = SubmitField('Save')


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[InputRequired()])
    submit = SubmitField('Save')


class AssignClientsForm(FlaskForm):
    selections = MultiCheckboxField('Select Clients to Assign', coerce=int)
    submit = SubmitField('Assign')


class AssignClientForm(FlaskForm):
    selection = RadioField('Select Group')
    submit = SubmitField('Assign')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class ExportToFileForm(FlaskForm):
    filename = StringField('Filename', validators=[InputRequired()])
    submit = SubmitField('Export')
