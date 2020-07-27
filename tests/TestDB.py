import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

import app
from app.dbFunc import *

"""
# Тестовая конфигурация
class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECURITY_PASSWORD_SALT = 'RTWgfqcokLsm'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xfXFp4tnkgv2'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'testdb.db')
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


# Задаём тестовую конфигурацию
app.app.config.from_object(Config)

db = SQLAlchemy(app.app)
migrate = Migrate(app.app, db)
login = LoginManager(app.app)
login.login_view = 'login'
mail = Mail(app)
s = URLSafeTimedSerializer('ppHrFeUXEwpf!')

"""


def test_add_admin():
    school_id = 1
    password = '123'
    add_admin(school_id, password)
    id_user = app.db.session.query(Admin).order_by(Admin.id)[-1]

    assert id_user.school_id == school_id


test_add_admin()


def test_add_calls():
    id_school = 1
    add_calls(id_school)
    id_user = app.db.session.query(ScheduleCalls).order_by(ScheduleCalls.id)[-1]

    assert id_user.id_school == id_school


test_add_calls()


def test_add_calls_lesson():
    lesson_number = 1
    start = '1'
    finish = '1'
    shift = 2
    day = 'monday'
    id_schedule_calls = 1
    add_calls_lesson(id_schedule_calls, lesson_number, start, finish, shift, day)
    id_user = app.db.session.query(ScheduleCallsLesson).order_by(ScheduleCallsLesson.id)[-1]

    assert id_user.lesson_number == lesson_number
    assert id_user.start == start
    assert id_user.finish == finish
    assert id_user.shift == shift
    assert id_user.day == day
    assert id_user.id_schedule_calls == id_schedule_calls


test_add_calls_lesson()


def test_add_class():
    id_school = 6
    name = 'Гимназия №29'
    add_class(id_school, name)
    id_user = app.db.session.query(Classes).order_by(Classes.id)[-1]

    assert id_user.id_school == id_school
    assert id_user.name == name


test_add_class()


def test_add_group():
    class_id = 2
    name = 'Гимназия №29Основная'
    add_group(class_id, name)
    id_user = app.db.session.query(Groups).order_by(Groups.id)[-1]

    assert id_user.class_id == class_id
    assert id_user.name == name


test_add_group()


def test_add_schedule():
    class_id = 1
    add_schedule(class_id)
    id_user = app.db.session.query(Schedule).order_by(Schedule.id)[-1]

    assert id_user.class_id == class_id


test_add_schedule()


def test_add_schedule_days():
    schedule_id = 1
    day = 'monday'
    subject = 'Пустой'
    lesson_number = '1'
    add_schedule_days(schedule_id, day, subject, lesson_number)
    id_user = app.db.session.query(ScheduleDays).order_by(ScheduleDays.id)[-1]

    assert id_user.schedule_id == schedule_id
    assert id_user.day == day
    assert id_user.subject == subject
    assert id_user.lesson_number == lesson_number


test_add_schedule_days()


def test_add_school():
    school = 'Гимназия №29'
    locality = 'г. Нальчик'
    add_school(school, locality)
    id_user = app.db.session.query(School).order_by(School.id)[-1]

    assert id_user.school == school
    assert id_user.locality == locality


test_add_school()


# DELETE


def test_delete_admin():
    id = 5
    delete_admin(id)
    id_user = db.session.query(Admin).filter_by(Admin.id).delete()

    assert id_user.id == id


test_delete_admin()