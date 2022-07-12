from datetime import datetime
from pickle import NONE
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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

    def get_client_name(self):
        client = Client.query.get(self.client_id)
        return client.get_name()

    def get_custodian_name(self):
        custodian = Custodian.query.get(self.custodian_id)
        return custodian.name


class Custodian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    description = db.Column(db.String(512))
    accounts = db.relationship('Account', backref='custodian', lazy='dynamic')


