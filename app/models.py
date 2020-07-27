from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    super_admin = db.Column(db.Boolean, nullable=True, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_email(self, email):
        self.email = email


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(120))
    locality = db.Column(db.String(120))

    def __init__(self, school, locality):
        self.school = school
        self.locality = locality


class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey(School.id))
    subject = db.Column(db.String(120))
    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))
    patronymic = db.Column(db.String(120))
    sex = db.Column(db.String(120))
    email = db.Column(db.String(120))

    def __init__(self, school_id, subject, name, surname, patronymic, sex, email):
        self.school_id = school_id
        self.subject = subject
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.sex = sex
        self.email = email


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_school = db.Column(db.Integer, db.ForeignKey(School.id))
    name = db.Column(db.String(120))

    def __init__(self, id_school, name):
        self.id_school = id_school
        self.name = name


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey(Classes.id))

    def __init__(self,  class_id):
        self.class_id = class_id


class ScheduleDays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey(Schedule.id))
    day = db.Column(db.String(120))
    subject = db.Column(db.String(120))
    lesson_number = db.Column(db.String(120))

    def __init__(self, schedule_id, day, subject, lesson_number):
        self.schedule_id = schedule_id
        self.day = day
        self.subject = subject
        self.lesson_number = lesson_number


class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey(Classes.id))
    name = db.Column(db.String(120))

    def __init__(self, class_id, name):
        self.class_id = class_id
        self.name = name


class TeachersGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_teacher = db.Column(db.Integer, db.ForeignKey(Teachers.id))
    id_group = db.Column(db.Integer, db.ForeignKey(Groups.id))

    def __init__(self, id_teacher, id_group):
        self.id_teacher = id_teacher
        self.id_group = id_group


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey(School.id))
    class_id = db.Column(db.Integer, db.ForeignKey(Classes.id))
    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))
    patronymic = db.Column(db.String(120))
    sex = db.Column(db.String(120))
    id_user = db.Column(db.Integer, db.ForeignKey(User.id))
    cooldown = db.Column(db.DateTime)

    def __init__(self, school_id, class_id, name, surname, patronymic, sex, id_user, cooldown):
        self.school_id = school_id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.sex = sex
        self.class_id = class_id
        self.id_user = id_user
        self.cooldown = cooldown


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_school = db.Column(db.Integer, db.ForeignKey(School.id))
    id_student = db.Column(db.Integer, db.ForeignKey(Students.id))
    id_teacher = db.Column(db.Integer, db.ForeignKey(Teachers.id))
    text_field = db.Column(db.String(120))
    lesson_interest = db.Column(db.Integer)
    lesson_comprehensibility = db.Column(db.Integer)
    teacher_behavior = db.Column(db.Integer)
    time = db.Column(db.DateTime)

    def __init__(self, id_school, id_student, id_teacher, text_field, lesson_interest, lesson_comprehensibility, teacher_behavior, time):
        self.id_school = id_school
        self.id_student = id_student
        self.id_teacher = id_teacher
        self.text_field = text_field
        self.lesson_interest = lesson_interest
        self.lesson_comprehensibility = lesson_comprehensibility
        self.teacher_behavior = teacher_behavior
        self.time = time


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey(School.id))
    id_user = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, school_id, id_user):
        self.school_id = school_id
        self.id_user = id_user


class StudentsGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_student = db.Column(db.Integer, db.ForeignKey(Students.id))
    id_group = db.Column(db.Integer, db.ForeignKey(Groups.id))

    def __init__(self, id_student, id_group):
        self.id_student = id_student
        self.id_group = id_group


class ScheduleCalls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_school = db.Column(db.Integer, db.ForeignKey(School.id))

    def __init__(self, id_school):
        self.id_school = id_school


class ScheduleCallsLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_schedule_calls = db.Column(db.Integer, db.ForeignKey(ScheduleCalls.id))
    shift = db.Column(db.Integer)
    lesson_number = db.Column(db.Integer)
    start = db.Column(db.String(120))
    finish = db.Column(db.String(120))
    day = db.Column(db.String(120))

    def __init__(self, id_schedule_calls, shift, lesson_number, start, finish, day):
        self.id_schedule_calls = id_schedule_calls
        self.shift = shift
        self.lesson_number = lesson_number
        self.start = start
        self.finish = finish
        self.day = day