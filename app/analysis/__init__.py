from flask import Blueprint

bp = Blueprint('analysis', __name__, template_folder='templates')

from app.analysis import routes
