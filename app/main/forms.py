from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,
                     DateField, SelectMultipleField, widgets, FloatField)
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo
from app.models import User, Security


