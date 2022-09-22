from flask import Blueprint

bp = Blueprint('account', __name__, template_folder='templates')

from app.account import routes
