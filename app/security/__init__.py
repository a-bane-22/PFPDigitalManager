from flask import Blueprint

bp = Blueprint('security', __name__, template_folder='templates')

from app.security import routes
