from flask import Blueprint

bp = Blueprint('transaction', __name__, template_folder='templates')

from app.transaction import routes
