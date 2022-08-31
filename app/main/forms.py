from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,
                     DateField, SelectMultipleField, widgets, FloatField)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Security


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
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
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Save')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class DeleteUserForm(FlaskForm):
    confirm = BooleanField('Confirm')
    submit = SubmitField('Submit')


class ClientInformationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    dob = DateField('DOB', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cell_phone = StringField('Cell Phone')
    home_phone = StringField('Home Phone')
    work_phone = StringField('Work Phone')
    submit = SubmitField('Save')


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
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
    description = StringField('Description', validators=[DataRequired()])
    billable = BooleanField('Billable')
    discretionary = BooleanField('Discretionary')
    submit = SubmitField('Save')


class AccountSnapshotForm(FlaskForm):
    quarter = SelectField('Quarter', validators=[DataRequired()])
    market_value = FloatField('Market Value', validators=[DataRequired()])
    submit = SubmitField('Save')


class CustodianForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class NewSecurityForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')

    @staticmethod
    def validate_symbol(self, symbol):
        security = Security.query.filter_by(symbol=symbol.data).first()
        if security is not None:
            raise ValidationError('A security already exists with that symbol.')


class AddSecurityForm(NewSecurityForm):
    submit = SubmitField('Save')


class EditSecurityForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class TransactionForm(FlaskForm):
    date = DateField('Date')
    type = SelectField('Type')
    security = SelectField('Security')
    quantity = FloatField('Quantity', validators=[DataRequired()])
    share_price = FloatField('Share Price', validators=[DataRequired()])
    gross_amount = FloatField('Gross Amount', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')


class UploadFileForm(FlaskForm):
    upload_file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')


class QuarterForm(FlaskForm):
    from_date = DateField('From', validators=[DataRequired()])
    to_date = DateField('To', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])


class AddQuarterForm(QuarterForm):
    account_file = FileField('Account File', validators=[FileRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Save')


class EditQuarterForm(QuarterForm):
    submit = SubmitField('Save')


class FeeScheduleForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class FeeRuleForm(FlaskForm):
    minimum = FloatField('Minimum', validators=[DataRequired()])
    maximum = FloatField('Maximum', validators=[DataRequired()])
    rate = FloatField('Rate', validators=[DataRequired()])
    flat = FloatField('Flat Fee', validators=[DataRequired()])
    submit = SubmitField('Save')
