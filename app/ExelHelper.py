import datetime
import xlrd
from app import dbFunc
from app.models import *


def add_students(way, school_id):
    wb = xlrd.open_workbook(way)
    sheet = wb.sheet_by_index(0)
    student_list = []
    for i in range(sheet.nrows):
        class_id = ""
        name = ""
        surname = ""
        patronymic = ""
        sex = ""
        class_id = sheet.row_values(i)[0]
        if isinstance(class_id, float):
            class_id = int(class_id)
        name = sheet.row_values(i)[1]
        surname = sheet.row_values(i)[2]
        patronymic = sheet.row_values(i)[3]
        sex = sheet.row_values(i)[4]
        a = dbFunc.random_password()
        user = User(admin=False, email=None, confirmed=False)
        user.set_password(a)
        db.session.add(user)
        db.session.commit()
        id_user = db.session.query(User).order_by(User.id)[-1]
        id_user = id_user.id
        student_list.append([str(name) + " " + str(surname) + " " + str(patronymic), id_user, a])
        a = datetime.datetime.now() - datetime.timedelta(days=360)
        class_id = db.session.query(Classes).filter_by(name=class_id, id_school=school_id).first().id
        b = Students(school_id=school_id, class_id=class_id, name=name, surname=surname, patronymic=patronymic, sex=sex,
                     id_user=id_user, cooldown=a)

        db.session.add(
            b)
        db.session.commit()
        a = db.session.query(Classes).filter_by(id=b.class_id).all()
        a = a[0].id
        dbFunc.add_student_to_group([b.id], a)
        db.session.commit()
    return student_list


def add_teachers(way, school_id):
    wb = xlrd.open_workbook(way)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        subject = ""
        name = ""
        surname = ""
        patronymic = ""
        sex = ""
        email = ""
        subject = sheet.row_values(i)[0]
        name = sheet.row_values(i)[1]
        surname = sheet.row_values(i)[2]
        patronymic = sheet.row_values(i)[3]
        sex = sheet.row_values(i)[4]
        email = sheet.row_values(i)[5]
        db.session.add(
            Teachers(school_id=school_id, name=name, surname=surname, patronymic=patronymic, sex=sex, subject=subject,
                     email=email))
        db.session.commit()
