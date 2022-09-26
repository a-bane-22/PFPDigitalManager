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
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

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
    account_snapshots = db.relationship('AccountSnapshot', backref='group', lazy='dynamic')

    # PRE:  self is a well-defined Group object
    #       quarter_id is an integer representing the primary key of a Quarter object
    # POST: Returns the sum of the market values of each AccountSnapshot object associated
    #        with this Group and Quarter
    def get_market_value(self, quarter_id):
        market_value = 0
        snapshots = AccountSnapshot.query.filter_by(group_id=self.id, quarter_id=quarter_id)
        for snapshot in snapshots:
            market_value += snapshot.market_value
        return market_value

    # PRE:  self is a well-defined Group object
    #       quarter_id is an integer representing the primary key of a Quarter object
    # POST: Returns the sum of the fees of each AccountSnapshot object associated with this
    #        Group and Quarter
    def get_fee(self, quarter_id):
        fee = 0
        snapshots = AccountSnapshot.query.filter_by(group_id=self.id, quarter_id=quarter_id)
        for snapshot in snapshots:
            fee += snapshot.fee
        return fee

    # PRE:  self is a well-defined Group object
    #       quarter_id is an integer representing the primary key of a Quarter object
    # POST: Returns a tuple containing the sum of the market values and the sum
    #        of the fees of each AccountSnapshot object associated with this
    #        Group and Quarter
    def get_quarter_data(self, quarter_id):
        market_value = 0
        fee = 0
        snapshots = AccountSnapshot.query.filter_by(group_id=self.id, quarter_id=quarter_id)
        for snapshot in snapshots:
            market_value += snapshot.market_value
            fee += snapshot.fee
        return market_value, fee


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
    schedule_id = db.Column(db.Integer, db.ForeignKey('fee_schedule.id'))
    snapshots = db.relationship('AccountSnapshot', backref='account', lazy='dynamic')
    positions = db.relationship('Position', backref='account', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')

    def get_client_name(self):
        client = Client.query.get(self.client_id)
        return client.get_name()

    def get_custodian_name(self):
        custodian = Custodian.query.get(self.custodian_id)
        return custodian.name

    def get_fee_schedule_name(self):
        schedule = FeeSchedule.query.get(self.schedule_id)
        return schedule.name

    # POST: Returns True if schedule_id is not None
    def assigned_fee_schedule(self):
        assigned = False
        if self.schedule_id is not None:
            print(type(self.schedule_id))
            print('Assigned == True')
            assigned = True
        return assigned

    # POST: Returns the AccountSnapshot associated with this object and quarter_id
    def get_snapshot(self, quarter_id):
        snapshot = AccountSnapshot.query.filter_by(account_id=self.id, quarter_id=quarter_id).first()
        return snapshot


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
    fee = db.Column(db.Float)
    account_snapshots = db.relationship('AccountSnapshot', backref='quarter', lazy='dynamic')


class AccountSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    market_value = db.Column(db.Float)
    fee = db.Column(db.Float)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    quarter_id = db.Column(db.Integer, db.ForeignKey('quarter.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def get_account_number(self):
        account = Account.query.get(self.account_id)
        return account.account_number

    def get_account(self):
        account = Account.query.get(self.account_id)
        return account

    def assigned_group(self):
        assigned = True
        if self.group_id is None:
            assigned = False
        return assigned

    def get_group_name(self):
        group = Group.query.get(self.group_id)
        return group.name

    def get_quarter_name(self):
        quarter = Quarter.query.get(self.quarter_id)
        return quarter.name

    def calculate_fee(self):
        account = Account.query.get(self.account_id)
        if account.billable and account.schedule_id is not None:
            schedule = FeeSchedule.query.get(account.schedule_id)
            fee = schedule.calculate_fee(self.market_value)
            self.fee = fee


class FeeSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    accounts = db.relationship('Account', backref='FeeSchedule', lazy='dynamic')
    rules = db.relationship('FeeRule', backref='FeeSchedule', lazy='dynamic')

    def calculate_fee(self, value):
        fee = 0
        for rule in self.rules:
            fee += rule.flat
            if value > rule.minimum:
                if value < rule.maximum:
                    fee += (value - rule.minimum) * (rule.rate/4)
                else:
                    fee += (rule.maximum - rule.minimum) * (rule.rate/4)
        return fee


class FeeRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    minimum = db.Column(db.Float)
    maximum = db.Column(db.Float)
    rate = db.Column(db.Float)
    flat = db.Column(db.Float)
    schedule_id = db.Column(db.Integer, db.ForeignKey('fee_schedule.id'))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.String(512))
    due_date = db.Column(db.Date, index=True)
    create_date = db.Column(db.Date, index=True)
    tasks = db.relationship('Task', backref='project', lazy='dynamic')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.String(512))
    due_date = db.Column(db.Date, index=True)
    create_date = db.Column(db.Date, index=True)
    completed = db.Column(db.Boolean, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
