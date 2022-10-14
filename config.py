import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_is_a_secret_kangaroo'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADS_DEFAULT_DEST = '/uploads'
    UPLOADED_FILES_DEST = '/uploads/files'

    ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY')
