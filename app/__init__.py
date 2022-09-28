from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'authentication.login'
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.account import bp as account_bp
    app.register_blueprint(account_bp)

    from app.analysis import bp as analysis_bp
    app.register_blueprint(analysis_bp)

    from app.authentication import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/authentication')

    from app.billing import bp as billing_bp
    app.register_blueprint(billing_bp)

    from app.client import bp as client_bp
    app.register_blueprint(client_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.task import bp as task_bp
    app.register_blueprint(task_bp)

    from app.transaction import bp as transaction_bp
    app.register_blueprint(transaction_bp)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp)

    return app


from app import models
