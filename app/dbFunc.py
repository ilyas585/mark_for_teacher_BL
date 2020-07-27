from app.models import *
import datetime
import string
import random


def get_day_of_week():
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    return days_of_week


def add_school(school, locality):
    db.session.add(School(school, locality))
    db.session.commit()


def add_student(school_id, class_id, name, surname, patronymic, sex, password):
    user = User(admin=False, email=None, confirmed=False)
    user.set_password(str(password))
    db.session.add(user)
    db.session.commit()
    id_user = db.session.query(User).order_by(User.id)[-1]
    id_user = id_user.id
    a = datetime.datetime.now() - datetime.timedelta(days=360)
    b = Students(school_id=school_id, class_id=class_id, name=name, surname=surname, patronymic=patronymic, sex=sex,
                 id_user=id_user, cooldown=a)
    db.session.add(
        b)
    db.session.commit()
    a = db.session.query(Classes).filter_by(id=b.class_id).all()
    a = a[0].id
    add_student_to_group([b.id], a)
    return b.id_user


def get_last_added_userid2():
    a = db.session.query(Admin).order_by(Admin.id_user)[-1]
    return a.id_user


def delete_student(id):
    a = db.session.query(Students).filter_by(id=id)
    db.session.query(StudentsGroup).filter_by(id_student=id).delete()
    student = db.session.query(Students).filter_by(id=id)
    student = student.all()
    user_id = student[0].id_user
    db.session.query(User).filter_by(id=user_id).delete()
    db.session.query(Students).filter_by(id=id).delete()
    db.session.commit()


def student_list_form():
    a = db.session.query(Students).all()
    st_list = []
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(class_name)))
    return st_list


def student_list_form2(class_id):
    a = db.session.query(Students).filter_by(class_id=class_id).all()
    st_list = []
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(class_name)))
    return st_list


def get_school_id(u_id):
    a = db.session.query(Admin).filter_by(id_user=u_id).all()
    return a[0].school_id


def student_list_form_admin(s_id):
    a = db.session.query(Students).filter_by(school_id=s_id).all()
    st_list = []
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(class_name)))
    return st_list


def student_list_form_admin2(s_id, class_id):
    a = db.session.query(Students).filter_by(school_id=s_id, class_id=class_id).all()
    st_list = []
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(class_name)))
    return st_list


def get_student_name(usr_id):
    a = db.session.query(Students).filter_by(id_user=usr_id).all()
    b = db.session.query(Classes).filter_by(id=a[0].class_id).all()
    c = db.session.query(School).filter_by(id=a[0].school_id).all()
    return [a[0].surname + " " + a[0].name + " " + a[0].patronymic, c[0].school + " " + b[0].name]


def student_list():
    st_list = []
    a = db.session.query(Students).all()
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(class_name) + ", " + str(i.name) + ", " + str(
            i.surname) + ", " + str(i.patronymic) + ", " + str(i.sex))
    return st_list


def student_list_admin(s_id):
    st_list = []
    a = db.session.query(Students).filter_by(school_id=s_id).all()
    for i in a:
        class_name = Classes.query.filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(class_name) + ", " + str(i.name) + ", " + str(
            i.surname) + ", " + str(i.patronymic) + ", " + str(i.sex))
    return st_list


def update_student(id, class_id="", name="", surname="", patronymic="", sex="", password=""):
    if class_id != "":
        db.session.query(Students).filter_by(id=id).update(({"class_id": class_id}))
        db.session.commit()

    if name != "":
        db.session.query(Students).filter_by(id=id).update(({"name": name}))
        db.session.commit()

    if surname != "":
        db.session.query(Students).filter_by(id=id).update(({"surname": surname}))
        db.session.commit()

    if patronymic != "":
        db.session.query(Students).filter_by(id=id).update(({"patronymic": patronymic}))
        db.session.commit()

    if sex != "":
        db.session.query(Students).filter_by(id=id).update(({"sex": sex}))
        db.session.commit()

    if password != "":
        st_id = db.session.query(Students).filter_by(id=id)
        st_id = st_id.all()
        st_id = st_id[0].id_user
        password = generate_password_hash(str(password))
        db.session.query(User).filter_by(id=st_id).update(({"password_hash": password}))
        db.session.commit()


def school_list():
    st_list = []
    a = db.session.query(School).all()
    for i in a:
        st_list.append(str(i.id) + " " + str(i.school) + " " + str(i.locality))
    return st_list


def list_school_form():
    a = db.session.query(School).all()
    sc_list = []
    for i in a:
        sc_list.append((i.id, str(i.school) + " " + str(i.locality)))
    return sc_list


def list_school_form_admin(s_id):
    a = db.session.query(School).filter_by(id=s_id).all()
    sc_list = []
    for i in a:
        sc_list.append((i.id, str(i.school) + " " + str(i.locality)))
    return sc_list


def delete_school(id_school):
    a = db.session.query(Students).filter_by(school_id=id_school).all()
    b = db.session.query(Teachers).filter_by(school_id=id_school).all()
    c = db.session.query(Classes).filter_by(id_school=id_school).all()
    h = db.session.query(Admin).filter_by(school_id=id_school).all()
    for i in a:
        db.session.query(StudentsGroup).filter_by(id_student=i.id).delete()
        db.session.query(User).filter_by(id=i.id_user).delete()
    for i in b:
        db.session.query(TeachersGroup).filter_by(id_teacher=i.id).delete()
    for i in c:
        db.session.query(Groups).filter_by(class_id=i.id).delete()
        d = db.session.query(Schedule).filter_by(class_id=i.id).all()
        for j in d:
            db.session.query(ScheduleDays).filter_by(schedule_id=j.id).delete()
        db.session.query(Schedule).filter_by(class_id=i.id).delete()
    for i in h:
        db.session.query(User).filter_by(id=i.id_user).delete()
        db.session.query(Admin).filter_by(id=i.id).delete()
    db.session.query(Admin).filter_by(school_id=id_school).delete()
    db.session.query(Classes).filter_by(id_school=id_school).delete()
    db.session.query(Teachers).filter_by(school_id=id_school).delete()
    db.session.query(Students).filter_by(school_id=id_school).delete()
    db.session.query(Assessment).filter_by(id_school=id_school).delete()
    db.session.query(School).filter_by(id=id_school).delete()
    db.session.commit()


def add_teacher(school_id, name, surname, patronymic, sex, subject, email):
    db.session.add(
        Teachers(school_id=school_id, name=name, surname=surname, patronymic=patronymic, sex=sex, subject=subject,
                 email=email))
    db.session.commit()


def teacher_list_form():
    a = db.session.query(Teachers).all()
    t_list = []
    for i in a:
        t_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(i.subject)))
    return t_list


def teacher_list_form_admin(s_id):
    a = db.session.query(Teachers).filter_by(school_id=s_id).all()
    t_list = []
    for i in a:
        t_list.append((i.id, str(i.name) + " " + str(i.surname) + " " + str(i.subject)))
    return t_list


def teacher_list():
    st_list = []
    a = db.session.query(Teachers).all()
    for i in a:
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(i.subject) + ", " + str(i.name) + ", " + str(
            i.surname) + ", " + str(i.patronymic) + ", " + str(i.sex) + ", " + str(i.email))
    return st_list


def teacher_list_admin(s_id):
    st_list = []
    a = db.session.query(Teachers).filter_by(school_id=s_id).all()
    for i in a:
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(i.subject) + ", " + str(i.name) + ", " + str(
            i.surname) + ", " + str(i.patronymic) + ", " + str(i.sex) + ", " + str(i.email))
    return st_list


def delete_teacher(id):
    db.session.query(TeachersGroup).filter_by(id_teacher=id).delete()
    db.session.query(Teachers).filter_by(id=id).delete()
    db.session.commit()


def update_teacher(id, name="", surname="", patronymic="", sex="", subject="", email=""):
    if name != "":
        db.session.query(Teachers).filter_by(id=id).update(({"name": name}))
        db.session.commit()

    if surname != "":
        db.session.query(Teachers).filter_by(id=id).update(({"surname": surname}))
        db.session.commit()

    if patronymic != "":
        db.session.query(Teachers).filter_by(id=id).update(({"patronymic": patronymic}))
        db.session.commit()

    if sex != "":
        db.session.query(Teachers).filter_by(id=id).update(({"sex": sex}))
        db.session.commit()

    if subject != "":
        db.session.query(Teachers).filter_by(id=id).update(({"subject": subject}))
        db.session.commit()

    if email != "":
        db.session.query(Teachers).filter_by(id=id).update(({"email": email}))
        db.session.commit()


# Добавление класса
def add_class(school_id, name):
    a = Classes(school_id, name)
    db.session.add(a)

    # Комитим что бы получить id !
    db.session.commit()

    # Добавляем основную группу что бы могли привязывать предметы сразу.
    db.session.add(Groups(class_id=a.id, name=a.name + "Основная"))

    # Добавляем расписание.
    new_schedule = Schedule(class_id=a.id)
    db.session.add(new_schedule)

    # Комитим что бы получить id !
    db.session.commit()
    schedule_id = new_schedule.id

    # К добавленному расписанию добавляем уроки.
    for day in get_day_of_week():
        for i in range(1, 7):
            add_schedule_days(schedule_id, day, "Пустой", i)

    db.session.commit()


def up_class(class_id, name=""):
    if name != "":
        db.session.query(Classes).filter_by(id=class_id).update(({"name": name}))
        db.session.commit()


def class_list_form():
    a = db.session.query(Classes).all()
    cl_list = []
    for i in a:
        cl_list.append((i.id, str(i.name)))
    return cl_list


def class_list_form_admin(s_id):
    a = db.session.query(Classes).filter_by(id_school=s_id).all()
    cl_list = []
    for i in a:
        cl_list.append((i.id, str(i.name)))
    return cl_list


def class_list():
    st_list = []
    a = db.session.query(Classes).all()
    for i in a:
        school_name = db.session.query(School).filter_by(id=i.id_school).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(i.name))
    return st_list


def class_list_admin(s_id):
    st_list = []
    a = db.session.query(Classes).filter_by(id_school=s_id).all()
    for i in a:
        school_name = db.session.query(School).filter_by(id=i.id_school).all()
        school_name = school_name[0].school
        st_list.append(str(i.id) + ", " + str(school_name) + ", " + str(i.name))
    return st_list


def delete_class(class_id):
    a = db.session.query(Groups).filter_by(class_id=class_id).all()
    for i in a:
        idd = i.id
        db.session.query(StudentsGroup).filter_by(id_group=idd).delete()
        db.session.query(TeachersGroup).filter_by(id_group=idd).delete()
    a = db.session.query(Students).filter_by(class_id=class_id).all()
    for i in a:
        user_id = i.id_user
        db.session.query(User).filter_by(id=user_id).delete()
    a = db.session.query(Schedule).filter_by(class_id=class_id).all()
    for i in a:
        db.session.query(ScheduleDays).filter_by(schedule_id=i.id).delete()
    db.session.query(Schedule).filter_by(class_id=class_id).delete()
    db.session.query(Students).filter_by(class_id=class_id).delete()
    db.session.query(Groups).filter_by(class_id=class_id).delete()
    db.session.query(Classes).filter_by(id=class_id).delete()
    db.session.commit()


def add_group(class_id, name):
    db.session.add(Groups(class_id, name))
    db.session.commit()


def up_group(class_id, name=""):
    if name != "":
        db.session.query(Groups).filter_by(id=class_id).update(({"name": name}))
        db.session.commit()


def group_list():
    st_list = []
    a = db.session.query(Groups).all()
    for i in a:
        class_name = db.session.query(Classes).filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append(str(i.id) + ", " + str(class_name) + ", " + str(i.name))
    return st_list


def group_list_admin(s_id):
    st_list = []
    a = db.session.query(Groups).all()
    for i in a:
        class_name = db.session.query(Classes).filter_by(id=i.class_id).all()
        class_id = class_name[0].id_school
        class_name = class_name[0].name
        if class_id == s_id:
            st_list.append(str(i.id) + ", " + str(class_name) + ", " + str(i.name))
    return st_list


def group_list_form(class_id):
    a = db.session.query(Groups).filter_by(class_id=class_id).all()
    gr_list = []
    for i in a:
        gr_list.append((i.id, str(i.name)))
    return gr_list


def group_list_form2(class_id):
    a = db.session.query(Groups).filter_by(class_id=class_id).all()
    b = db.session.query(Classes).filter_by(id=class_id).first().name
    gr_list = []
    for i in a:
        if i.name != b + "Основная":
            gr_list.append((i.id, str(i.name)))
    return gr_list


def delete_group(group_id):
    a = db.session.query(Groups).filter_by(id=group_id).all()
    for i in a:
        idd = i.id
        db.session.query(TeachersGroup).filter_by(id_group=idd).delete()
    db.session.query(Groups).filter_by(id=group_id).delete()
    db.session.commit()


def add_teacher_to_group(id_teacher, group_id):
    for i in id_teacher:
        db.session.add(TeachersGroup(i, group_id))
    db.session.commit()


def add_student_to_group(id_student, group_id):
    for i in id_student:
        db.session.add(StudentsGroup(i, group_id))
    db.session.commit()


def teachergroup_list_form():
    a = db.session.query(TeachersGroup).all()
    gr_list = []
    for i in a:
        teacher = db.session.query(Teachers).filter_by(id=i.id_teacher).all()
        teacher_id = teacher[0].id
        teacher = str(teacher[0].name) + " " + str(teacher[0].surname) + ", " + str(teacher[0].subject)
        group_name = db.session.query(Groups).filter_by(id=i.id_group).all()
        group_name = group_name[0].name
        gr_list.append((str(i.id_group) + " " + str(teacher_id), teacher + ", " + group_name))
    return gr_list


def teachergroup_list_form_admin(s_id):
    a = db.session.query(TeachersGroup).all()
    gr_list = []
    for i in a:
        teacher = db.session.query(Teachers).filter_by(id=i.id_teacher).all()
        if teacher[0].school_id == s_id:
            teacher_id = teacher[0].id
            teacher = str(teacher[0].name) + " " + str(teacher[0].surname) + ", " + str(teacher[0].subject)
            group_name = db.session.query(Groups).filter_by(id=i.id_group).all()
            group_name = group_name[0].name
            gr_list.append((str(i.id_group) + " " + str(teacher_id), teacher + ", " + group_name))
    return gr_list


def studentgroup_list_form_admin(s_id):
    a = db.session.query(StudentsGroup).all()
    gr_list = []
    for i in a:
        teacher = db.session.query(Students).filter_by(id=i.id_student).all()
        if teacher[0].school_id == s_id:
            teacher_id = teacher[0].id
            teacher = str(teacher[0].name) + " " + str(teacher[0].surname)
            group_name = db.session.query(Groups).filter_by(id=i.id_group).all()
            group_name = group_name[0].name
            gr_list.append((str(i.id_group) + " " + str(teacher_id), teacher + ", " + group_name))
    return gr_list


def studentgroup_list_form():
    a = db.session.query(StudentsGroup).all()
    gr_list = []
    for i in a:
        teacher = db.session.query(Students).filter_by(id=i.id_student).all()
        teacher_id = teacher[0].id
        teacher = str(teacher[0].name) + " " + str(teacher[0].surname)
        group_name = db.session.query(Groups).filter_by(id=i.id_group).all()
        group_name = group_name[0].name
        gr_list.append((str(i.id_group) + " " + str(teacher_id), teacher + ", " + group_name))
    return gr_list


def delete_teacher_from_group(id_teacher, group_id):
    db.session.query(TeachersGroup).filter_by(id_group=group_id, id_teacher=id_teacher).delete()
    db.session.commit()


def delete_student_from_group(id_teacher, group_id):
    db.session.query(StudentsGroup).filter_by(id_group=group_id, id_student=id_teacher).delete()
    db.session.commit()


def add_rating(id_school, id_student, id_teacher, text_field, lesson_interest, lesson_comprehensibility,
               teacher_behavior, time):
    db.session.add(Assessment(id_school, id_student, id_teacher, text_field, lesson_interest, lesson_comprehensibility,
                              teacher_behavior, time))
    db.session.commit()


def add_schedule(class_id):
    db.session.query(Schedule).filter_by(class_id=class_id).delete()
    db.session.add(Schedule(class_id))
    db.session.commit()


def get_schedule_id(class_id):
    a = db.session.query(Schedule).filter_by(class_id=class_id).all()
    return a[0].id


def subject_list(class_id):
    a = db.session.query(Groups).filter_by(class_id=class_id).all()
    gr_list = []
    for i in a:
        b = db.session.query(TeachersGroup).filter_by(id_group=i.id).all()
        for j in b:
            c = db.session.query(Teachers).filter_by(id=j.id_teacher).all()
            c = c[0].subject
            gr_list.append((c, c))
    gr_list = list(set(gr_list))
    gr_list.insert(0, ("Пустой", "Пустой"))
    return gr_list


def subject_list2(class_id, day_of_week, lesson_number):
    gr_list = []
    schedule_id = db.session.query(Schedule).filter_by(class_id=class_id).first().id
    subject = db.session.query(ScheduleDays).filter_by(schedule_id=schedule_id,
                                                       day=day_of_week, lesson_number=lesson_number).first().subject

    a = db.session.query(Groups).filter_by(class_id=class_id).all()
    for i in a:
        b = db.session.query(TeachersGroup).filter_by(id_group=i.id).all()
        for j in b:
            c = db.session.query(Teachers).filter_by(id=j.id_teacher).all()
            c = c[0].subject
            if c != subject:
                gr_list.append((c, c))
    gr_list = list(set(gr_list))

    gr_list.insert(0, (subject, subject))
    if subject != "Пустой":
        gr_list.insert(1, ("Пустой", "Пустой"))

    return gr_list


def up_schedule_days(schedule_id, day, subject, lesson_number):
    if subject != "Без изменений":
        db.session.query(ScheduleDays).filter_by(day=day, schedule_id=schedule_id, lesson_number=lesson_number).update(
            ({"subject": subject}))
    db.session.commit()


def add_schedule_days(schedule_id, day, subject, lesson_number):
    db.session.add(ScheduleDays(schedule_id, day, subject, lesson_number))
    db.session.commit()


def ti_chego_nadelal(schedule_id):
    db.session.query(ScheduleDays).filter_by(schedule_id=schedule_id).delete()
    db.session.commit()


def schedule_list():
    st_list = []
    a = db.session.query(Schedule).all()
    for i in a:
        class_name = db.session.query(Classes).filter_by(id=i.class_id).all()
        class_name = class_name[0].name
        st_list.append((i.id, str(class_name)))
    return st_list


def schedule_list_admin(s_id):
    st_list = []
    a = db.session.query(Schedule).all()
    for i in a:
        class_name = db.session.query(Classes).filter_by(id=i.class_id).all()
        if class_name[0].id_school == s_id:
            class_name = class_name[0].name
            st_list.append((i.id, str(class_name)))
    return st_list


def delete_schedule(schedule_id):
    db.session.query(Schedule).filter_by(id=schedule_id).delete()
    db.session.query(ScheduleDays).filter_by(schedule_id=schedule_id).delete()
    db.session.commit()


def add_admin(school_id, password):
    user = User(admin=True, email=None, confirmed=False)
    user.set_password(str(password))
    db.session.add(user)
    db.session.commit()
    id_user = db.session.query(User).order_by(User.id)[-1]
    id_user = id_user.id
    db.session.add(Admin(school_id=school_id, id_user=id_user))
    db.session.commit()


def delete_admin(id):
    db.session.query(User).filter_by(id=id).delete()
    db.session.query(Admin).filter_by(id_user=id).delete()
    db.session.commit()


def get_current_teacher(user_id, id=True):
    if id:
        subject = get_current_lesson(user_id)
        subject = subject
        if subject is not False:
            student = db.session.query(Students).filter_by(id_user=user_id).all()
            group = db.session.query(StudentsGroup).filter_by(id_student=student[0].id).all()
            for i in group:
                teacher = db.session.query(TeachersGroup).filter_by(id_group=i.id_group).all()
                for j in teacher:
                    teacher = db.session.query(Teachers).filter_by(id=j.id_teacher).all()
                    if teacher[0].subject == subject:
                        return teacher[0].id
        else:
            return False
    else:
        subject = get_current_lesson(user_id)
        subject = subject
        if subject is not False:
            student = db.session.query(Students).filter_by(id_user=user_id).all()
            group = db.session.query(StudentsGroup).filter_by(id_student=student[0].id).all()
            for i in group:
                teacher = db.session.query(TeachersGroup).filter_by(id_group=i.id_group).all()
                for j in teacher:
                    teacher = db.session.query(Teachers).filter_by(id=j.id_teacher).all()
                    if teacher[0].subject == subject:
                        return teacher[0].name + " " + teacher[0].surname + " " + teacher[0].patronymic
        else:
            return False


def get_time(user_id):
    student = db.session.query(Students).filter_by(id_user=user_id).all()
    b = student[0].school_id
    student = student[0].class_id
    schedule = db.session.query(Schedule).filter_by(class_id=student).all()
    schedule = schedule[0].id
    calls_id = db.session.query(ScheduleCalls).filter_by(id_school=b).first().id
    day = datetime.datetime.today().isoweekday()
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d")
    if 1 <= day < 7:
        dday = get_day_of_week()[day - 1]

    a = datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(
        id_schedule_calls=calls_id, day=dday,
        shift=1, lesson_number=6).first().finish, '%Y-%m-%d %H:%M')
    a += datetime.timedelta(minutes=10)
    lesson_array = [

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M'),
                a
        ]
    ]
    a = datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(
        id_schedule_calls=calls_id, day=dday,
        shift=2, lesson_number=6).first().finish, '%Y-%m-%d %H:%M')
    a += datetime.timedelta(minutes=10)
    lesson_array2 = [

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M'),
                a
        ]
    ]

    if lesson_array[0][0] <= now <= lesson_array[0][1] or lesson_array2[0][0] <= now <= lesson_array2[0][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')
        else:
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')

    elif lesson_array[1][0] <= now <= lesson_array[1][1] or lesson_array2[1][0] <= now <= lesson_array2[1][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')
        else:
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')

    elif lesson_array[2][0] <= now <= lesson_array[2][1] or lesson_array2[2][0] <= now <= lesson_array2[2][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')
        else:
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')

    elif lesson_array[3][0] <= now <= lesson_array[3][1] or lesson_array2[3][0] <= now <= lesson_array2[3][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')
        else:
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')

    elif lesson_array[4][0] <= now <= lesson_array[4][1] or lesson_array2[4][0] <= now <= lesson_array2[4][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')
        else:
            return datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')

    elif lesson_array[5][0] <= now <= lesson_array[5][1] or lesson_array2[5][0] <= now <= lesson_array2[5][1]:
        if now < datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'):
            return 1
        else:
            return 2
    else:
        return False


def get_current_lesson(user_id):
    student = db.session.query(Students).filter_by(id_user=user_id).all()
    school_id = student[0].school_id
    class_id = student[0].class_id
    schedule = db.session.query(Schedule).filter_by(class_id=class_id).all()
    schedule = schedule[0].id
    calls_id = db.session.query(ScheduleCalls).filter_by(id_school=school_id).first().id
    day = datetime.datetime.today().isoweekday()
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d")
    if 1 <= day < 7:
        dday = get_day_of_week()[day - 1]
    else:
        return False

    a = datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(
        id_schedule_calls=calls_id, day=dday,
        shift=1, lesson_number=6).first().finish, '%Y-%m-%d %H:%M')
    a += datetime.timedelta(minutes=10)

    lesson_array = [

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=1, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M'),
                a
        ]
    ]
    a = datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(
        id_schedule_calls=calls_id, day=dday,
        shift=2, lesson_number=6).first().finish, '%Y-%m-%d %H:%M')
    a += datetime.timedelta(minutes=10)
    lesson_array2 = [

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=1).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=2).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=3).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=4).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=5).first().start,
                '%Y-%m-%d %H:%M'),
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M')
        ],

        [
            datetime.datetime.strptime(
                time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, day=dday,
                                                                             shift=2, lesson_number=6).first().start,
                '%Y-%m-%d %H:%M'),
                a
        ]
    ]

    days_of_week = get_day_of_week()
    if 0 < day < 8:
        day = days_of_week[day - 1]
    else:
        return False

    if lesson_array[0][0] <= now <= lesson_array[0][1] or lesson_array2[0][0] <= now <= lesson_array2[0][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=1).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    elif lesson_array[1][0] <= now <= lesson_array[1][1] or lesson_array2[1][0] <= now <= lesson_array2[1][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=2).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    elif lesson_array[2][0] <= now <= lesson_array[2][1] or lesson_array2[2][0] <= now <= lesson_array2[2][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=3).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    elif lesson_array[3][0] <= now <= lesson_array[3][1] or lesson_array2[3][0] <= now <= lesson_array2[3][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=4).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    elif lesson_array[4][0] <= now <= lesson_array[4][1] or lesson_array2[4][0] <= now <= lesson_array2[4][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=5).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    elif lesson_array[5][0] <= now <= lesson_array[5][1] or lesson_array2[5][0] <= now <= lesson_array2[5][1]:
        schedule_days = db.session.query(ScheduleDays).filter_by(schedule_id=schedule, day=day, lesson_number=6).all()
        if schedule_days[0].subject != "Пустой" and schedule_days[0].subject != None:
            return schedule_days[0].subject
        else:
            return False
    else:
        return False


def admin_list():
    st_list = []
    a = db.session.query(Admin).all()
    for i in a:
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append((str(i.id_user), str(school_name)))
    return st_list


def admin_list2():
    st_list = []
    a = db.session.query(Admin).all()
    for i in a:
        school_name = School.query.filter_by(id=i.school_id).all()
        school_name = school_name[0].school
        st_list.append((str(i.id_user), str(i.id_user) + ", " + str(school_name)))
    return st_list


def random_password():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 8)
    return ''.join(random.choice(chars) for x in range(size))


def add_calls(school_id):
    db.session.query(ScheduleCalls).filter_by(id_school=school_id).delete()
    a = ScheduleCalls(id_school=school_id)
    db.session.add(a)
    db.session.commit()
    return a.id


def add_calls_lesson(calls_id, lesson_number, start, finish, shift, day):
    db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=shift,
                                                    lesson_number=lesson_number, day=day).delete()
    db.session.add(
        ScheduleCallsLesson(id_schedule_calls=calls_id, shift=shift, lesson_number=lesson_number, start=start,
                            finish=finish, day=day))
    #db.session.commit()
    #calls_calls(calls_id)


def calls_calls(calls_id):
    a = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1).all()
    for i in a:
        if i.lesson_number != 6:
            b = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1, lesson_number=i.lesson_number + 1).first().start
            c = b.split(":")
            d = c[0]
            c = int(c[1]) - 1
            db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1,
                                                                lesson_number=i.lesson_number).update(
                    ({"finish": str(d) + ":" + str(c)}))
            db.session.commit()
        else:
            b = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1,
                                                                lesson_number=i.lesson_number).first().start
            c = b.split(":")
            d = c[0]
            c = int(c[1]) + 10
            db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1,
                                                            lesson_number=i.lesson_number).update(
                ({"finish": str(d) + ":" + str(c)}))
            db.session.commit()

        a = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2).all()
        for i in a:
            if i.lesson_number != 6:
                b = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2,
                                                                    lesson_number=i.lesson_number + 1).first().start
                c = b.split(":")
                d = c[0]
                c = int(c[1]) - 1
                db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2,
                                                                lesson_number=i.lesson_number).update(
                    ({"finish": str(d) + ":" + str(c)}))
                db.session.commit()
            else:
                b = db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2,
                                                                    lesson_number=i.lesson_number).first().start
                c = b.split(":")
                d = c[0]
                c = int(c[1]) + 10
                db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2,
                                                                lesson_number=i.lesson_number).update(
                    ({"finish": str(d) + ":" + str(c)}))
                db.session.commit()


def check_email(email):
    for i in db.session.query(User).all():
        if i.email == email:
            return False

    return True
