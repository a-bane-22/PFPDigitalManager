from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, DateField)
from wtforms.validators import InputRequired


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = StringField('Description')
    due = DateField('Due Date')
    submit = SubmitField('Save')


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = StringField('Description')
    due = DateField('Due Date')
    submit = SubmitField('Save')
