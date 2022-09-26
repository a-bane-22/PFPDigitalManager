from flask import Blueprint

bp = Blueprint('task', __name__, template_folder='templates')

from app.task import routes
