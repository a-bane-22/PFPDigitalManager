from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField)
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo
from app.models import User


class AddUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    password_2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email')


class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired()])
    submit = SubmitField('Save')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    password_2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class DeleteUserForm(FlaskForm):
    confirm = BooleanField('Confirm')
    submit = SubmitField('Submit')
