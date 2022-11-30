from flask import Blueprint

bp = Blueprint('option', __name__, template_folder='templates')

from app.option import routes