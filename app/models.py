from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(10), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_name(self):
        return self.first_name + ' ' + self.last_name


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    clients = db.relationship('Client', backref='group', lazy='dynamic')


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    middle_name = db.Column(db.String(32), index=True)
    dob = db.Column(db.Date, index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    cell_phone = db.Column(db.String(10), index=True)
    work_phone = db.Column(db.String(10), index=True)
    home_phone = db.Column(db.String(10), index=True)
    assigned = db.Column(db.Boolean, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    accounts = db.relationship('Account', backref='client', lazy='dynamic')

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    def get_full_name(self):
        return self.first_name + ' ' + self.middle_name + ' ' + self.last_name

    def get_group_name(self):
        group = Group.query.get(self.group_id)
        return group.name


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(32), index=True)
    description = db.Column(db.String(512))
    billable = db.Column(db.Boolean, index=True)
    discretionary = db.Column(db.Boolean, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    custodian_id = db.Column(db.Integer, db.ForeignKey('custodian.id'))
    snapshots = db.relationship('AccountSnapshot', backref='account', lazy='dynamic')
    positions = db.relationship('Position', backref='account', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')

    def get_client_name(self):
        client = Client.query.get(self.client_id)
        return client.get_name()

    def get_custodian_name(self):
        custodian = Custodian.query.get(self.custodian_id)
        return custodian.name


class AccountSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    market_value = db.Column(db.Float)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    def get_account_number(self):
        account = Account.query.get(self.account_id)
        return account.account_number


class Custodian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    description = db.Column(db.String(512))
    accounts = db.relationship('Account', backref='custodian', lazy='dynamic')


class Security(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), index=True, unique=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(512))
    positions = db.relationship('Position', backref='security', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='security', lazy='dynamic')


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float)
    cost_basis = db.Column(db.Float)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    security_id = db.Column(db.Integer, db.ForeignKey('security.id'))
    transactions = db.relationship('Transaction', backref='position', lazy='dynamic')

    def get_account_number(self):
        account = Account.query.get(self.account_id)
        return account.account_number

    def get_security_symbol(self):
        security = Security.query.get(self.security_id)
        return security.symbol

    def add_transaction(self, transaction_type, quantity, gross_amount):
        if transaction_type.upper() == 'BUY':
            self.quantity += quantity
            self.cost_basis += gross_amount
        elif transaction_type.upper() == 'SELL':
            self.quantity -= quantity
            if self.cost_basis < gross_amount:
                self.cost_basis = 0
            else:
                self.cost_basis -= gross_amount

    def remove_transaction(self, transaction_id):
        self.quantity = 0
        self.cost_basis = 0
        for transaction in self.transactions:
            if transaction.id != transaction_id:
                self.add_transaction(transaction_type=transaction.type, quantity=transaction.quantity,
                                     gross_amount=transaction.gross_amount)

    def recreate_position(self):
        self.quantity = 0
        self.cost_basis = 0
        for transaction in self.transactions:
            self.add_transaction(transaction_type=transaction.type, quantity=transaction.quantity,
                                 gross_amount=transaction.gross_amount)

    def reverse_transaction(self, transaction_type, quantity, cost_basis):
        if transaction_type == 'BUY':
            self.quantity -= quantity
            self.cost_basis -= cost_basis
        elif transaction_type == 'SELL':
            self.quantity += quantity
            self.cost_basis += cost_basis


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    type = db.Column(db.String(16), index=True)
    description = db.Column(db.String(512))
    quantity = db.Column(db.Float)
    share_price = db.Column(db.Float)
    gross_amount = db.Column(db.Float)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    security_id = db.Column(db.Integer, db.ForeignKey('security.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    def get_account_number(self):
        account = Account.query.get(self.account_id)
        return account.account_number

    def get_security_symbol(self):
        security = Security.query.get(self.security_id)
        return security.symbol


class Quarter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_date = db.Column(db.Date, index=True)
    to_date = db.Column(db.Date, index=True)
    name = db.Column(db.String(7), unique=True, index=True)
    aum = db.Column(db.Float)
