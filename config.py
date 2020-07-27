import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECURITY_PASSWORD_SALT = 'RTWgfqcokLsm'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xfXFp4tnkgv2'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME ='onextopplay@gmail.com'
    MAIL_PASSWORD ='enovzewxqolwlbha'

    # mail accounts
    MAIL_DEFAULT_SENDER = 'onextopplay@gmail.com'