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
    certifications = db.relationship('Certificate', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_completed_modules(self):
        name_list = []
        for certificate in self.certifications:
            name_list.append(certificate.get_module_name)
        return name_list


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
