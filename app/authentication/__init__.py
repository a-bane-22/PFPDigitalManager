from flask import Blueprint

bp = Blueprint('authentication', __name__, template_folder='templates')

from app.authentication import routes

