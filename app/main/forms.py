from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,
                     DateField, SelectMultipleField, widgets, FloatField)
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo
from app.models import User, Security


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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


class AccountForm(FlaskForm):
    custodian = SelectField('Custodian')
    account_number = StringField('Account Number')
    description = StringField('Description', validators=[InputRequired()])
    billable = BooleanField('Billable')
    discretionary = BooleanField('Discretionary')
    submit = SubmitField('Save')


class AccountSnapshotForm(FlaskForm):
    quarter = SelectField('Quarter', validators=[InputRequired()])
    market_value = FloatField('Market Value', validators=[InputRequired()])
    submit = SubmitField('Save')


class CustodianForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


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


class TransactionForm(FlaskForm):
    date = DateField('Date')
    type = SelectField('Type')
    security = SelectField('Security')
    quantity = FloatField('Quantity', validators=[InputRequired()])
    share_price = FloatField('Share Price', validators=[InputRequired()])
    gross_amount = FloatField('Gross Amount', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class QuarterForm(FlaskForm):
    from_date = DateField('From', validators=[InputRequired()])
    to_date = DateField('To', validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired()])


class AddQuarterForm(QuarterForm):
    account_file = FileField('Account File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Save')


class EditQuarterForm(QuarterForm):
    submit = SubmitField('Save')


class FeeScheduleForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Save')


class FeeRuleForm(FlaskForm):
    minimum = FloatField('Minimum', validators=[InputRequired()])
    maximum = FloatField('Maximum', validators=[InputRequired()])
    rate = FloatField('Rate', validators=[InputRequired()])
    flat = FloatField('Flat Fee', validators=[InputRequired()])
    submit = SubmitField('Save')
