from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, FormField, DateField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UserBase(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email')


class RegistrationForm(UserBase):
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class UserForm(UserBase):
    submit = SubmitField('Save User')


class ClientInformationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    dob = DateField('DOB', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cell_phone = StringField('Cell Phone')
    home_phone = StringField('Home Phone')
    work_phone = StringField('Work Phone')
    submit = SubmitField('Save Client')


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    submit = SubmitField('Save Group')


class AssignClientsForm(FlaskForm):
    selections = MultiCheckboxField('Select Clients to Assign', coerce=int)
    submit = SubmitField('Assign Clients')


class AssignClientForm(FlaskForm):
    selection = RadioField('Select Group')
    submit = SubmitField('Assign Client')


class AccountForm(FlaskForm):
    custodian = SelectField('Custodian')
    account_number = StringField('Account Number')
    description = StringField('Description', validators=[DataRequired()])
    billable = BooleanField('Billable')
    discretionary = BooleanField('Discretionary')
    submit = SubmitField('Save Account')


class CustodianForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save Custodian')


