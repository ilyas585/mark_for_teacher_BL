import os
import datetime
from datetime import timedelta
import time
import threading
import json
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.tokenn import generate_confirmation_token, confirm_token, confirm_token2
from app.mail import send_email, send_mail2
from app import app, db, dbFunc, ExelHelper
from app.forms import LoginForm, SelectForm, ScheduleForm, CallsForm
from app.models import *
from app.statistic import get_stats


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='favicon.ico')


@app.route('/stat')
@login_required
def temp():
    if current_user.admin:
        teacher_id = request.args.get('teacher_id')
        try:
            b = get_stats(teacher_id)
            a = json.dumps(b[0])
            return render_template('teacher_statistic.html', stat_data=a, r1=b[1], r2=b[2], r3=b[3], name=b[4], surname=b[5],
                                   patr=b[6])
        except:
            return render_template("no_rating.html")
    return redirect(url_for("index"))


@app.route('/stats/<token>')
def stats(token):
    try:
        teacher_id = confirm_token2(token)
    except:
        return redirect(url_for("index"))
    try:
        b = get_stats(teacher_id)
        a = json.dumps(b[0])
        return render_template('statistic.html', stat_data=a, r1=b[1], r2=b[2], r3=b[3], name=b[4], surname=b[5],
                               patr=b[6])
    except:
        return "У вас еще нет оценок"


@app.route('/')
@login_required
def index():
    if current_user.admin:
        return redirect(url_for('admin'))
    else:
        return redirect(url_for("star"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == "POST":
        user = User.query.filter_by(id=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        user = User.query.filter_by(email=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)

        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/change_pass", methods=["GET", "POST"])
def change_pass():
    form = SelectForm()
    if form.submit.data:
        token = generate_confirmation_token(form.email.data)
        confirm_url = url_for('confirm_pass', token=token, _external=True)
        html = render_template('change_pass.html', confirm_url=confirm_url)
        subject = "Сылка для изменения пароля"
        send_email(form.email.data, subject, html)
        return "На ваш email отправлено письмо"
    return render_template('email_pass.html', title='Email', form=form)


@app.route('/confirm_pass/<token>', methods=["GET", "POST"])
def confirm_pass(token):
    form = SelectForm()
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if form.submit.data:
        user.set_password(str(form.name.data))
        db.session.commit()
        return redirect(url_for("logout"))
    return render_template("ch_pass.html", form=form)


@app.route("/email", methods=["GET", "POST"])
@login_required
def add_email():
    form = SelectForm()
    if form.submit.data:
        if dbFunc.check_email(form.email.data):
            User.query.filter_by(id=current_user.id).update({"email": form.email.data})
            db.session.commit()
            token = generate_confirmation_token(current_user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(current_user.email, subject, html)
            flash('Congratulations, you are now a registered user!')
            return "<h1>На ваш email было высланно письмо <a href='/tst'> Перейти в личный кабинет</a></h1>"
        else:
            return "<h1>Данный email уже зарегистриван введите другой email <a href='/tst'> Перейти в личный кабинет</a></h1>"
    return render_template('email.html', title='Email', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('tst'))


@app.route("/admin")
@login_required
def admin():
    if current_user.super_admin:
        return render_template("school_admin_panel.html")
    elif current_user.admin:
        return render_template("school_admin_panel.html", a=True)
    else:
        return redirect(url_for(index))


@app.route("/add_student", methods=['GET', "POST"])
@login_required
def add_student():
    if current_user.super_admin:
        form = SelectForm()
        form.student_list.choices = dbFunc.student_list_form()
        form.class_list.choices = dbFunc.class_list_form()
        form.school_list.choices = dbFunc.list_school_form()
        form.student_list2.choices = dbFunc.student_list_form()
        form.class_list2.choices = dbFunc.class_list_form()
        form.a1.choices = dbFunc.student_list_form()
        if form.submit.data:
            a = dbFunc.random_password()
            return render_template("stl.html", u_id=str(dbFunc.add_student(form.school_list.data, form.class_list.data,
                                                                           form.name.data, form.surname.data,
                                                                           form.patronymic.data,
                                                                           form.sex.data, a)), name=a, admin=False, b=[form.name.data, form.surname.data,
                                                                           form.patronymic.data])
        if form.submit3.data:
            dbFunc.update_student(id=form.student_list2.data, class_id=form.class_list2.data, sex=form.sex2.data,
                                  name=form.name2.data, surname=form.surname2.data, patronymic=form.patronymic2.data,
                                  password=form.password2.data)
            return redirect(url_for("add_student"))
        if form.submit2.data:
            for i in form.a1.data:
                db.session.query(StudentsGroup).filter_by(id_student=i).delete()
                student = db.session.query(Students).filter_by(id=i)
                student = student.all()
                user_id = student[0].id_user
                db.session.query(User).filter_by(id=user_id).delete()
                db.session.query(Students).filter_by(id=i).delete()
                db.session.commit()
            return redirect(url_for("add_student"))
        return render_template("students.html", form=form,
                               rows=dbFunc.student_list(), is_school_admin=False)
    elif current_user.admin:
        form = SelectForm()
        form.student_list.choices = dbFunc.student_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.student_list2.choices = dbFunc.student_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.class_list2.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.a1.choices = dbFunc.student_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit.data:
            form.school_list = db.session.query(Admin).filter_by(
                id_user=current_user.id).first().school_id

            a = dbFunc.random_password()
            student_fio = [form.name.data, form.surname.data, form.patronymic.data]
            return render_template("stl.html", u_id=str(
                dbFunc.add_student(form.school_list, form.class_list.data,
                form.name.data, form.surname.data,
                form.patronymic.data,
                form.sex.data, a)), name=a, admin=False, b=student_fio)

        if form.submit3.data:
            dbFunc.update_student(id=form.student_list2.data, class_id=form.class_list2.data, sex=form.sex2.data,
                                  name=form.name2.data, surname=form.surname2.data, patronymic=form.patronymic2.data,
                                  password=form.password2.data)
            return redirect(url_for("add_student"))
        if form.submit2.data:
            for i in form.a1.data:
                db.session.query(StudentsGroup).filter_by(id_student=i).delete()
                student = db.session.query(Students).filter_by(id=i)
                student = student.all()
                user_id = student[0].id_user
                db.session.query(User).filter_by(id=user_id).delete()
                db.session.query(Students).filter_by(id=i).delete()
                db.session.commit()
            return redirect(url_for("add_student"))
        if form.submit4.data:
            return redirect(url_for("add_student_file"))
        return render_template("students.html", form=form,
                               rows=dbFunc.student_list_admin(dbFunc.get_school_id(current_user.id)),
                               is_school_admin=True)
    else:
        return redirect(url_for("index"))


@app.route("/add_student_xls", methods=['GET', "POST"])
def add_student_file():
    if current_user.admin and not current_user.super_admin:
        school_id = dbFunc.get_school_id(current_user.id)
        if request.method == "POST":
            file = request.files['file']
            filename = file.filename
            if os.path.isdir(os.path.join("app", "download")):
                path_name = "download"
                a = os.path.join("app", path_name, filename)
                file.save(a)
                b = ExelHelper.add_students(a, school_id)
                os.remove(a)
                return render_template("stl.html", xls=True, a=b)
            else:
                path_name = "download"
                os.mkdir(os.path.join("app", path_name))
                a = os.path.join("app", path_name, filename)
                file.save(a)
                b = ExelHelper.add_students(a, school_id)
                os.remove(a)
                return render_template("stl.html", xls=True, a=b)
        return render_template("add_xls.html", st=True)
    else:
        return redirect(url_for("index"))


@app.route("/add_teacher_xls", methods=['GET', "POST"])
def add_teacher_file():
    if current_user.admin and not current_user.super_admin:
        school_id = dbFunc.get_school_id(current_user.id)
        if request.method == "POST":
            if os.path.isdir(os.path.join("app", "download")):
                file = request.files['file']
                filename = file.filename
                path_name = "download"
                a = os.path.join("app", path_name, filename)
                file.save(a)
                ExelHelper.add_teachers(a, school_id)
                os.remove(a)
                return redirect(url_for("add_teacher"))
            else:
                file = request.files['file']
                filename = file.filename
                path_name = "download"
                os.mkdir(os.path.join("app", path_name))
                a = os.path.join("app", path_name, filename)
                file.save(a)
                ExelHelper.add_teachers(a, school_id)
                os.remove(a)
                return redirect(url_for("add_teacher"))
        return render_template("add_xls2.html")
    else:
        return redirect(url_for("index"))


@app.route("/add_teacher", methods=['GET', "POST"])
@login_required
def add_teacher():
    if current_user.super_admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form()
        form.teacher_list2.choices = dbFunc.teacher_list_form()
        form.teacher_list3.choices = dbFunc.teacher_list_form()
        form.teacher_list.choices = dbFunc.teacher_list_form()
        form.a1.choices = dbFunc.teacher_list_form()
        a = [
            ("Труды", "Труды"), ("Математика", "Математика"), ("Музыка", "Музыка"), ("ИЗО", "ИЗО"), ("Русский язык и литература", "Русский язык и литература"),
            ("Физкультура", "Физкультура"), ("Родной язык", "Родной язык"), ("Английский язык", "Английский язык"),
            ("История", "История"), ("ОБЖ", "ОБЖ"), ("География", "География"), ("Биология", "Биология"), ("Информатика", "Информатика"),
            ("Обществознание", "Обществознание"), ("Физика", "Физика"), ("Химия", "Химия")
        ]
        form.group_list.choices = a
        form.group_list2.choices = a
        if form.submit.data:
            dbFunc.add_teacher(form.school_list.data, form.name.data, form.surname.data, form.patronymic.data,
                               form.sex.data, form.group_list.data, form.email.data)
            return redirect(url_for("add_teacher"))
        if form.submit3.data:
            dbFunc.update_teacher(id=form.teacher_list2.data, name=form.name2.data, surname=form.surname2.data,
                                  patronymic=form.patronymic2.data, subject=form.group_list2.data, sex=form.sex2.data,
                                  email=form.email2.data)
            return redirect(url_for("add_teacher"))
        if form.submit2.data:
            for i in form.a1.data:
                dbFunc.delete_teacher(i)
        return render_template("teachers.html", form=form, rows=dbFunc.teacher_list(), c=True)
    elif current_user.admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form_admin(dbFunc.get_school_id(current_user.id))
        form.teacher_list2.choices = dbFunc.teacher_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.teacher_list3.choices = dbFunc.teacher_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.teacher_list.choices = dbFunc.teacher_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.a1.choices = dbFunc.teacher_list_form_admin(dbFunc.get_school_id(current_user.id))
        a = [
            ("Труды", "Труды"), ("Математика", "Математика"), ("Музыка", "Музыка"), ("ИЗО", "ИЗО"), ("Русский язык и литература", "Русский язык и литература"),
            ("Физкультура", "Физкультура"), ("Родной язык", "Родной язык"), ("Английский язык", "Английский язык"),
            ("История", "История"), ("ОБЖ", "ОБЖ"), ("География", "География"), ("Биология", "Биология"), ("Информатика", "Информатика"),
            ("Обществознание", "Обществознание"), ("Физика", "Физика"), ("Химия", "Химия")
        ]
        form.group_list.choices = a
        form.group_list2.choices = a
        if form.submit.data:
            dbFunc.add_teacher(dbFunc.get_school_id(current_user.id), form.name.data, form.surname.data, form.patronymic.data,
                               form.sex.data, form.group_list.data, form.email.data)
            return redirect(url_for("add_teacher"))
        if form.submit3.data:
            dbFunc.update_teacher(id=form.teacher_list2.data, name=form.name2.data, surname=form.surname2.data,
                                  patronymic=form.patronymic2.data, subject=form.subject2.data, sex=form.sex2.data,
                                  email=form.email2.data)
            return redirect(url_for("add_teacher"))
        if form.submit2.data:
            for i in form.a1.data:
                dbFunc.delete_teacher(i)
            return redirect(url_for("add_teacher"))
        if form.submit4.data:
            return redirect(url_for("add_teacher_file"))
        return render_template("teachers.html", form=form,
                               rows=dbFunc.teacher_list_admin(dbFunc.get_school_id(current_user.id)), b=True, c=False)
    else:
        return redirect(url_for("index"))


@app.route("/add_school", methods=["GET", "POST"])
@login_required
def add_school():
    if current_user.super_admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form()
        if form.submit2.data:
            dbFunc.add_school(form.name.data, form.surname.data)
            return redirect(url_for("add_school"))
        if form.submit.data:
            dbFunc.delete_school(form.school_list.data)
            return redirect(url_for("add_school"))
        return render_template("school.html", form=form, rows=dbFunc.school_list())
    else:
        return redirect(url_for("index"))


@app.route("/add_class", methods=['GET', "POST"])
@login_required
def add_class():
    if current_user.super_admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form()
        form.class_list.choices = dbFunc.class_list_form()
        form.student_list.choices = dbFunc.class_list_form()
        if form.submit.data:
            dbFunc.add_class(form.school_list.data, form.name.data)
            return redirect(url_for("add_class"))
        if form.submit2.data:
            dbFunc.delete_class(form.class_list.data)
            return redirect(url_for("add_class"))
        if form.submit3.data:
            dbFunc.up_class(form.student_list.data, form.surname.data)
            return redirect(url_for("add_class"))
        return render_template("classes.html", form=form, rows=dbFunc.class_list() , b=True)
    elif current_user.admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form_admin(dbFunc.get_school_id(current_user.id))
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.student_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit.data:
            dbFunc.add_class(dbFunc.get_school_id(current_user.id), form.name.data)
            return redirect(url_for("add_class"))
        if form.submit2.data:
            dbFunc.delete_class(form.class_list.data)
            return redirect(url_for("add_class"))
        if form.submit3.data:
            dbFunc.up_class(form.student_list.data, form.surname.data)
            return redirect(url_for("add_class"))
        return render_template("classes.html", form=form, rows=dbFunc.class_list_admin(dbFunc.get_school_id(current_user.id)), b=False)
    else:
        return redirect(url_for("index"))


@app.route("/add_group", methods=['GET', "POST"])
@login_required
def add_group():
    if current_user.super_admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form()
        form.class_list2.choices = dbFunc.class_list_form()
        form.student_list.choices = dbFunc.class_list_form()
        if form.submit.data:
            dbFunc.add_group(form.class_list.data, form.name.data)
            return redirect(url_for("add_group"))
        if form.submit2.data:
            return redirect(url_for("dell_group", class_id=form.class_list2.data))
        if form.submit3.data:
            return redirect(url_for("up_group", class_id=form.student_list.data))
        return render_template("groups.html", form=form, rows=dbFunc.group_list())
    elif current_user.admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.class_list2.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.student_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit.data:
            dbFunc.add_group(form.class_list.data, form.name.data)
            return redirect(url_for("add_group"))
        if form.submit2.data:
            return redirect(url_for("dell_group", class_id=form.class_list2.data))
        if form.submit3.data:
            return redirect(url_for("up_group", class_id=form.student_list.data))
        return render_template("groups.html", form=form,
                               rows=dbFunc.group_list_admin(dbFunc.get_school_id(current_user.id)))
    else:
        return redirect(url_for("index"))


@app.route("/up_group2", methods=['GET', "POST"])
@login_required
def up_group():
    if current_user.admin:
        class_id = request.args.get('class_id')
        form = SelectForm()
        form.group_list.choices = dbFunc.group_list_form(class_id)
        if form.submit.data:
            dbFunc.up_group(form.group_list.data, form.name.data)
            return redirect(url_for("add_group"))
        return render_template("update_group.html", form=form, rows=dbFunc.group_list())
    else:
        return redirect(url_for("index"))


@app.route("/delete_group2", methods=['GET', "POST"])
@login_required
def dell_group():
    if current_user.admin:
        class_id = request.args.get('class_id')
        form = SelectForm()
        form.group_list.choices = dbFunc.group_list_form(class_id)
        if form.submit2.data:
            dbFunc.delete_group(form.group_list.data)
            return redirect(url_for("add_group"))
        return render_template("delete_group.html", form=form, rows=dbFunc.group_list())
    else:
        return redirect(url_for("index"))


@app.route("/add_teachergroup", methods=["GET", "POST"])
@login_required
def add_teacher_to_group():
    if current_user.super_admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form()
        form.group_list.choices = dbFunc.teachergroup_list_form()
        if form.submit2.data:
            return redirect(url_for("add_teacher_to_group2", class_id=form.class_list.data))
        if form.submit.data:
            a = form.group_list.data
            a = a.split(" ")
            dbFunc.delete_teacher_from_group(a[1], a[0])
            return redirect(url_for("add_teacher_to_group"))
        return render_template("teacher_to_group.html", form=form, rows=dbFunc.teachergroup_list_form())
    elif current_user.admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.group_list.choices = dbFunc.teachergroup_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit2.data:
            return redirect(url_for("add_teacher_to_group2", class_id=form.class_list.data))
        if form.submit.data:
            a = form.group_list.data
            a = a.split(" ")
            dbFunc.delete_teacher_from_group(a[1], a[0])
            return redirect(url_for("add_teacher_to_group"))
        return render_template("teacher_to_group.html", form=form,
                               rows=dbFunc.teachergroup_list_form_admin(dbFunc.get_school_id(current_user.id)))
    else:
        return redirect(url_for("index"))


@app.route("/add_teachergroup2", methods=["GET", "POST"])
@login_required
def add_teacher_to_group2():
    if current_user.super_admin:
        class_id = request.args.get('class_id')
        form = SelectForm()
        form.group_list.choices = dbFunc.group_list_form(class_id)
        form.a1.choices = dbFunc.teacher_list_form()
        if form.submit2.data:
            dbFunc.add_teacher_to_group(form.a1.data, form.group_list.data)
            return redirect(url_for("add_teacher_to_group"))
        return render_template("teacher_to_group2.html", form=form, rows=dbFunc.teachergroup_list_form())
    if current_user.admin:
        form = SelectForm()
        class_id = request.args.get('class_id')
        form.group_list.choices = dbFunc.group_list_form(class_id)
        form.a1.choices = dbFunc.teacher_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit2.data:
            dbFunc.add_teacher_to_group(form.a1.data, form.group_list.data)
            return redirect(url_for("add_teacher_to_group"))
        return render_template("teacher_to_group2.html", form=form,
                               rows=dbFunc.teachergroup_list_form_admin(dbFunc.get_school_id(current_user.id)))
    else:
        return redirect(url_for("index"))


@app.route("/add_studentgroup", methods=["GET", "POST"])
@login_required
def add_studentgroup():
    if current_user.super_admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form()
        form.group_list.choices = dbFunc.studentgroup_list_form()
        if form.submit2.data:
            return redirect(url_for("add_studentgroup2", class_id=form.class_list.data))
        if form.submit.data:
            a = form.group_list.data
            a = a.split(" ")
            dbFunc.delete_student_from_group(a[1], a[0])
            return redirect(url_for("add_studentgroup"))
        return render_template("studentgroup.html", form=form, rows=dbFunc.studentgroup_list_form())
    if current_user.admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        form.group_list.choices = dbFunc.studentgroup_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit2.data:
            return redirect(url_for("add_studentgroup2", class_id=form.class_list.data))
        if form.submit.data:
            a = form.group_list.data
            a = a.split(" ")
            dbFunc.delete_student_from_group(a[1], a[0])
            return redirect(url_for("add_studentgroup"))
        return render_template("studentgroup.html", form=form,
                               rows=dbFunc.studentgroup_list_form_admin(dbFunc.get_school_id(current_user.id)))
    else:
        return redirect(url_for("index"))


@app.route("/add_studentgroup2", methods=["GET", "POST"])
@login_required
def add_studentgroup2():
    if current_user.super_admin:
        class_id = request.args.get('class_id')
        form = SelectForm()
        form.group_list.choices = dbFunc.group_list_form2(class_id)
        form.a1.choices = dbFunc.student_list_form2(class_id)
        if form.submit2.data:
            dbFunc.add_student_to_group(form.a1.data, form.group_list.data)
            return redirect(url_for("add_studentgroup"))
        return render_template("stundentgroup2.html", form=form, rows=dbFunc.studentgroup_list_form())
    if current_user.admin:
        class_id = request.args.get('class_id')
        form = SelectForm()
        form.group_list.choices = dbFunc.group_list_form2(class_id)
        form.a1.choices = dbFunc.student_list_form_admin2(dbFunc.get_school_id(current_user.id), class_id)
        if form.submit2.data:
            dbFunc.add_student_to_group(form.a1.data, form.group_list.data)
            return redirect(url_for("add_studentgroup"))
        return render_template("stundentgroup2.html", form=form, rows=dbFunc.studentgroup_list_form_admin(dbFunc.get_school_id(current_user.id)))
    else:
        return redirect(url_for("index"))


@app.route("/add_schedule_class2", methods=["GET", "POST"])
def up_schedule():
    if current_user.super_admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form()
        if form.submit2.data:
            return redirect(url_for("up_schedule2", class_id=form.class_list.data))
        return render_template("schedule1.html", form=form)
    if current_user.admin:
        form = SelectForm()
        form.class_list.choices = dbFunc.class_list_form_admin(dbFunc.get_school_id(current_user.id))
        if form.submit2.data:
            return redirect(url_for("up_schedule2", class_id=form.class_list.data))
        return render_template("schedule1.html", form=form)
    else:
        return redirect(url_for("index"))


@app.route("/add_schedule2", methods=["GET", "POST"])
@login_required
def up_schedule2():
    if current_user.admin:
        class_id = request.args.get('class_id')
        form = ScheduleForm()
        form.monday1.choices = dbFunc.subject_list2(class_id, "monday", 1)
        form.monday2.choices = dbFunc.subject_list2(class_id, "monday", 2)
        form.monday3.choices = dbFunc.subject_list2(class_id, "monday", 3)
        form.monday4.choices = dbFunc.subject_list2(class_id, "monday", 4)
        form.monday5.choices = dbFunc.subject_list2(class_id, "monday", 5)
        form.monday6.choices = dbFunc.subject_list2(class_id, "monday", 6)

        form.tuesday1.choices = dbFunc.subject_list2(class_id, "tuesday", 1)
        form.tuesday2.choices = dbFunc.subject_list2(class_id, "tuesday", 2)
        form.tuesday3.choices = dbFunc.subject_list2(class_id, "tuesday", 3)
        form.tuesday4.choices = dbFunc.subject_list2(class_id, "tuesday", 4)
        form.tuesday5.choices = dbFunc.subject_list2(class_id, "tuesday", 5)
        form.tuesday6.choices = dbFunc.subject_list2(class_id, "tuesday", 6)

        form.wednesday1.choices = dbFunc.subject_list2(class_id, "wednesday", 1)
        form.wednesday2.choices = dbFunc.subject_list2(class_id, "wednesday", 2)
        form.wednesday3.choices = dbFunc.subject_list2(class_id, "wednesday", 3)
        form.wednesday4.choices = dbFunc.subject_list2(class_id, "wednesday", 4)
        form.wednesday5.choices = dbFunc.subject_list2(class_id, "wednesday", 5)
        form.wednesday6.choices = dbFunc.subject_list2(class_id, "wednesday", 6)

        form.thursday1.choices = dbFunc.subject_list2(class_id, "thursday", 1)
        form.thursday2.choices = dbFunc.subject_list2(class_id, "thursday", 2)
        form.thursday3.choices = dbFunc.subject_list2(class_id, "thursday", 3)
        form.thursday4.choices = dbFunc.subject_list2(class_id, "thursday", 4)
        form.thursday5.choices = dbFunc.subject_list2(class_id, "thursday", 5)
        form.thursday6.choices = dbFunc.subject_list2(class_id, "thursday", 6)

        form.friday1.choices = dbFunc.subject_list2(class_id, "friday", 1)
        form.friday2.choices = dbFunc.subject_list2(class_id, "friday", 2)
        form.friday3.choices = dbFunc.subject_list2(class_id, "friday", 3)
        form.friday4.choices = dbFunc.subject_list2(class_id, "friday", 4)
        form.friday5.choices = dbFunc.subject_list2(class_id, "friday", 5)
        form.friday6.choices = dbFunc.subject_list2(class_id, "friday", 6)

        form.saturday1.choices = dbFunc.subject_list2(class_id, "saturday", 1)
        form.saturday2.choices = dbFunc.subject_list2(class_id, "saturday", 2)
        form.saturday3.choices = dbFunc.subject_list2(class_id, "saturday", 3)
        form.saturday4.choices = dbFunc.subject_list2(class_id, "saturday", 4)
        form.saturday5.choices = dbFunc.subject_list2(class_id, "saturday", 5)
        form.saturday6.choices = dbFunc.subject_list2(class_id, "saturday", 6)

        schedule_id = dbFunc.get_schedule_id(class_id)
        if form.submit.data:
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "monday", form.monday6.data, 6)

            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "tuesday", form.tuesday6.data, 6)

            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "wednesday", form.wednesday6.data, 6)

            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "thursday", form.thursday6.data, 6)

            dbFunc.up_schedule_days(schedule_id, "friday", form.friday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "friday", form.friday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "friday", form.friday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "friday", form.friday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "friday", form.friday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "friday", form.friday6.data, 6)

            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday1.data, 1)
            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday2.data, 2)
            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday3.data, 3)
            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday4.data, 4)
            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday5.data, 5)
            dbFunc.up_schedule_days(schedule_id, "saturday", form.saturday6.data, 6)
            return redirect(url_for("index"))
        return render_template("schedule2.html", form=form, a=True)
    else:
        return redirect(url_for("index"))


@app.route("/tst", methods=["GET", "POST"])
@login_required
def tst():
    form = SelectForm()
    if current_user.email is not None:
        a = True
        b = current_user.email
    else:
        a = False
        b = False
    if current_user.super_admin:
        if form.submit.data:
            if dbFunc.check_email(form.email.data):
                User.query.filter_by(id=current_user.id).update({"email": form.email.data})
                db.session.commit()
                token = generate_confirmation_token(current_user.email)
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(current_user.email, subject, html)
                flash('Congratulations, you are now a registered user!')
                return "<h1>На ваш email было высланно письмо <a href='/tst'> Перейти в личный кабинет</a></h1>"
            else:
                return "<h1>Данный email уже зарегистриван введите другой email <a href='/tst'> Перейти в личный кабинет</a></h1>"
        if form.submit2.data:
            token = generate_confirmation_token(form.email2.data)
            confirm_url = url_for('confirm_pass', token=token, _external=True)
            html = render_template('change_pass.html', confirm_url=confirm_url)
            subject = "Сылка для изменения пароля"
            send_email(form.email2.data, subject, html)
            return "На ваш email отправлено письмо"
        return render_template("profile.html", form=form, name="Супер админ", admin=True, a=a, email=b)
    if current_user.admin:
        if form.submit.data:
            if dbFunc.check_email(form.email.data):
                User.query.filter_by(id=current_user.id).update({"email": form.email.data})
                db.session.commit()
                token = generate_confirmation_token(current_user.email)
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(current_user.email, subject, html)
                flash('Congratulations, you are now a registered user!')
                return "<h1>На ваш email было высланно письмо <a href='/tst'> Перейти в личный кабинет</a></h1>"
            else:
                return "<h1>Данный email уже зарегистриван введите другой email <a href='/tst'> Перейти в личный кабинет</a></h1>"
        if form.submit2.data:
            token = generate_confirmation_token(current_user.email)
            confirm_url = url_for('confirm_pass', token=token, _external=True)
            html = render_template('change_pass.html', confirm_url=confirm_url)
            subject = "Сылка для изменения пароля"
            send_email(current_user.email, subject, html)
            return "На ваш email отправлено письмо"
        return render_template("profile.html", form=form, name="Админ", admin=True, a=a, email=b)
    else:
        if form.submit.data:
            if dbFunc.check_email(form.email.data):
                User.query.filter_by(id=current_user.id).update({"email": form.email.data})
                db.session.commit()
                token = generate_confirmation_token(current_user.email)
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(current_user.email, subject, html)
                flash('Congratulations, you are now a registered user!')
                return "<h1>На ваш email было высланно письмо <a href='/tst'> Перейти в личный кабинет</a></h1>"
            else:
                return "<h1>Данный email уже зарегистриван введите другой email <a href='/tst'> Перейти в личный кабинет</a></h1>"
        if form.submit2.data:
            token = generate_confirmation_token(form.email2.data)
            confirm_url = url_for('confirm_pass', token=token, _external=True)
            html = render_template('change_pass.html', confirm_url=confirm_url)
            subject = "Сылка для изменения пароля"
            send_email(current_user.email, subject, html)
            return "На ваш email отправлено письмо"
        return render_template("profile.html", form=form, name=dbFunc.get_student_name(current_user.id), a=a, email=b)


@app.route("/add_admin", methods=['GET', "POST"])
@login_required
def add_admin():
    if current_user.super_admin:
        form = SelectForm()
        form.school_list.choices = dbFunc.list_school_form()
        form.student_list.choices = dbFunc.admin_list2()
        if form.submit.data:
            dbFunc.add_admin(form.school_list.data, form.name.data)
            return render_template("stl.html", u_id=str(dbFunc.get_last_added_userid2()), name=form.name.data, admin=True)
        if form.submit2.data:
            dbFunc.delete_admin(form.student_list.data)
            return redirect(url_for("add_admin"))

        return render_template("admin.html", form=form, rows=dbFunc.admin_list())
    else:
        return redirect(url_for("index"))


@app.route("/star", methods=['GET', "POST"])
@login_required
def star():
    if current_user.admin or current_user.super_admin:
        return redirect(url_for("index"))
    lesson = dbFunc.get_current_lesson(current_user.id)
    school = db.session.query(Students).filter_by(id_user=current_user.id).all()
    teacher = dbFunc.get_current_teacher(current_user.id, id=False)
    if school[0].cooldown < datetime.datetime.now() and lesson is not False:
        form = SelectForm()
        if form.submit.data:
            r1 = form.name.data
            r2 = form.surname.data
            r3 = form.patronymic.data.split("//::spliter::")[0]
            comm = form.patronymic.data.split("//::spliter::")[1]
            school = db.session.query(Students).filter_by(id_user=current_user.id).all()
            now = datetime.datetime.now()
            time = now.strftime("%Y-%m-%d")
            dbFunc.add_rating(school[0].school_id, school[0].id, dbFunc.get_current_teacher(current_user.id), comm, r1, r2, r3,
                              datetime.datetime.now())
            b = dbFunc.get_time(current_user.id)
            student = db.session.query(Students).filter_by(id_user=current_user.id).all()
            school_id = student[0].school_id
            student = student[0].class_id
            schedule = db.session.query(Schedule).filter_by(class_id=student).all()
            schedule = schedule[0].id
            calls_id = db.session.query(ScheduleCalls).filter_by(id_school=school_id).first().id
            now = datetime.datetime.now()
            time = now.strftime("%Y-%m-%d")
            if b == 1:

                db.session.query(Students).filter_by(id=school[0].id).update(
                    {"cooldown": datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=1, lesson_number=1).first().start, '%Y-%m-%d %H:%M') + timedelta(days=1)})
                db.session.commit()
                return redirect(url_for("index"))
            elif b == 2:

                db.session.query(Students).filter_by(id=school[0].id).update(
                    {"cooldown": datetime.datetime.strptime(time + ' ' + db.session.query(ScheduleCallsLesson).filter_by(id_schedule_calls=calls_id, shift=2, lesson_number=1).first().start, '%Y-%m-%d %H:%M') + timedelta(days=1)})
                db.session.commit()
                return redirect(url_for("index"))
            db.session.query(Students).filter_by(id=school[0].id).update(
                ({"cooldown": b}))
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("stars.html", form=form, lesson=lesson, check=True, teacher=teacher)
    else:
        return render_template("stars.html", lesson=lesson, check=False, teacher=teacher)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def send_statistic():
    a = db.session.query(Teachers).all()
    for i in a:
        if i.email is None or i.email == "":
            pass
        else:
            token = generate_confirmation_token(i.id)
            b = "http://127.0.0.1:5000/stats/" + token
            send_mail2(i.email, b)


@app.route("/calls", methods=['GET', "POST"])
@login_required
def calls():
    if current_user.super_admin or not current_user.admin:
        return redirect(url_for("index"))
    form = CallsForm()
    if form.submit.data:

        a = dbFunc.add_calls(dbFunc.get_school_id(current_user.id))

        if form.hidden_form.data == "First":
            for day_of_week in dbFunc.get_day_of_week():
                dbFunc.add_calls_lesson(a, 1, form.pnonest1.data, form.pnonefn1.data, 1, day_of_week)
                dbFunc.add_calls_lesson(a, 2, form.pnonest2.data, form.pnonefn2.data, 1, day_of_week)
                dbFunc.add_calls_lesson(a, 3, form.pnonest3.data, form.pnonefn3.data, 1, day_of_week)
                dbFunc.add_calls_lesson(a, 4, form.pnonest4.data, form.pnonefn4.data, 1, day_of_week)
                dbFunc.add_calls_lesson(a, 5, form.pnonest5.data, form.pnonefn5.data, 1, day_of_week)
                dbFunc.add_calls_lesson(a, 6, form.pnonest6.data, form.pnonefn6.data, 1, day_of_week)

                dbFunc.add_calls_lesson(a, 1, form.pntwost1.data, form.pntwofn1.data, 2, day_of_week)
                dbFunc.add_calls_lesson(a, 2, form.pntwost2.data, form.pntwofn2.data, 2, day_of_week)
                dbFunc.add_calls_lesson(a, 3, form.pntwost3.data, form.pntwofn3.data, 2, day_of_week)
                dbFunc.add_calls_lesson(a, 4, form.pntwost4.data, form.pntwofn4.data, 2, day_of_week)
                dbFunc.add_calls_lesson(a, 5, form.pntwost5.data, form.pntwofn5.data, 2, day_of_week)
                dbFunc.add_calls_lesson(a, 6, form.pntwost6.data, form.pntwofn6.data, 2, day_of_week)
        else:

            dbFunc.add_calls_lesson(a, 1, form.pnonest1.data, form.pnonefn1.data, 1, "monday")
            dbFunc.add_calls_lesson(a, 2, form.pnonest2.data, form.pnonefn2.data, 1, "monday")
            dbFunc.add_calls_lesson(a, 3, form.pnonest3.data, form.pnonefn3.data, 1, "monday")
            dbFunc.add_calls_lesson(a, 4, form.pnonest4.data, form.pnonefn4.data, 1, "monday")
            dbFunc.add_calls_lesson(a, 5, form.pnonest5.data, form.pnonefn5.data, 1, "monday")
            dbFunc.add_calls_lesson(a, 6, form.pnonest6.data, form.pnonefn6.data, 1, "monday")

            dbFunc.add_calls_lesson(a, 1, form.pntwost1.data, form.pntwofn1.data, 2, "monday")
            dbFunc.add_calls_lesson(a, 2, form.pntwost2.data, form.pntwofn2.data, 2, "monday")
            dbFunc.add_calls_lesson(a, 3, form.pntwost3.data, form.pntwofn3.data, 2, "monday")
            dbFunc.add_calls_lesson(a, 4, form.pntwost4.data, form.pntwofn4.data, 2, "monday")
            dbFunc.add_calls_lesson(a, 5, form.pntwost5.data, form.pntwofn5.data, 2, "monday")
            dbFunc.add_calls_lesson(a, 6, form.pntwost6.data, form.pntwofn6.data, 2, "monday")

            dbFunc.add_calls_lesson(a, 1, form.vtonest1.data, form.vtonefn1.data, 1, "tuesday")
            dbFunc.add_calls_lesson(a, 2, form.vtonest2.data, form.vtonefn2.data, 1, "tuesday")
            dbFunc.add_calls_lesson(a, 3, form.vtonest3.data, form.vtonefn3.data, 1, "tuesday")
            dbFunc.add_calls_lesson(a, 4, form.vtonest4.data, form.vtonefn4.data, 1, "tuesday")
            dbFunc.add_calls_lesson(a, 5, form.vtonest5.data, form.vtonefn5.data, 1, "tuesday")
            dbFunc.add_calls_lesson(a, 6, form.vtonest6.data, form.vtonefn6.data, 1, "tuesday")

            dbFunc.add_calls_lesson(a, 1, form.vttwost1.data, form.vttwofn1.data, 2, "tuesday")
            dbFunc.add_calls_lesson(a, 2, form.vttwost2.data, form.vttwofn2.data, 2, "tuesday")
            dbFunc.add_calls_lesson(a, 3, form.vttwost3.data, form.vttwofn3.data, 2, "tuesday")
            dbFunc.add_calls_lesson(a, 4, form.vttwost4.data, form.vttwofn4.data, 2, "tuesday")
            dbFunc.add_calls_lesson(a, 5, form.vttwost5.data, form.vttwofn5.data, 2, "tuesday")
            dbFunc.add_calls_lesson(a, 6, form.vttwost6.data, form.vttwofn6.data, 2, "tuesday")

            dbFunc.add_calls_lesson(a, 1, form.sronest1.data, form.sronefn1.data, 1, "wednesday")
            dbFunc.add_calls_lesson(a, 2, form.sronest2.data, form.sronefn2.data, 1, "wednesday")
            dbFunc.add_calls_lesson(a, 3, form.sronest3.data, form.sronefn3.data, 1, "wednesday")
            dbFunc.add_calls_lesson(a, 4, form.sronest4.data, form.sronefn4.data, 1, "wednesday")
            dbFunc.add_calls_lesson(a, 5, form.sronest5.data, form.sronefn5.data, 1, "wednesday")
            dbFunc.add_calls_lesson(a, 6, form.sronest6.data, form.sronefn6.data, 1, "wednesday")

            dbFunc.add_calls_lesson(a, 1, form.srtwost1.data, form.srtwofn1.data, 2, "wednesday")
            dbFunc.add_calls_lesson(a, 2, form.srtwost2.data, form.srtwofn2.data, 2, "wednesday")
            dbFunc.add_calls_lesson(a, 3, form.srtwost3.data, form.srtwofn3.data, 2, "wednesday")
            dbFunc.add_calls_lesson(a, 4, form.srtwost4.data, form.srtwofn4.data, 2, "wednesday")
            dbFunc.add_calls_lesson(a, 5, form.srtwost5.data, form.srtwofn5.data, 2, "wednesday")
            dbFunc.add_calls_lesson(a, 6, form.srtwost6.data, form.srtwofn6.data, 2, "wednesday")

            dbFunc.add_calls_lesson(a, 1, form.ctonest1.data, form.ctonefn1.data, 1, "thursday")
            dbFunc.add_calls_lesson(a, 2, form.ctonest2.data, form.ctonefn2.data, 1, "thursday")
            dbFunc.add_calls_lesson(a, 3, form.ctonest3.data, form.ctonefn3.data, 1, "thursday")
            dbFunc.add_calls_lesson(a, 4, form.ctonest4.data, form.ctonefn4.data, 1, "thursday")
            dbFunc.add_calls_lesson(a, 5, form.ctonest5.data, form.ctonefn5.data, 1, "thursday")
            dbFunc.add_calls_lesson(a, 6, form.ctonest6.data, form.ctonefn6.data, 1, "thursday")

            dbFunc.add_calls_lesson(a, 1, form.cttwost1.data, form.cttwofn1.data, 2, "thursday")
            dbFunc.add_calls_lesson(a, 2, form.cttwost2.data, form.cttwofn2.data, 2, "thursday")
            dbFunc.add_calls_lesson(a, 3, form.cttwost3.data, form.cttwofn3.data, 2, "thursday")
            dbFunc.add_calls_lesson(a, 4, form.cttwost4.data, form.cttwofn4.data, 2, "thursday")
            dbFunc.add_calls_lesson(a, 5, form.cttwost5.data, form.cttwofn5.data, 2, "thursday")
            dbFunc.add_calls_lesson(a, 6, form.cttwost6.data, form.cttwofn6.data, 2, "thursday")

            dbFunc.add_calls_lesson(a, 1, form.ptonest1.data, form.ptonefn1.data, 1, "friday")
            dbFunc.add_calls_lesson(a, 2, form.ptonest2.data, form.ptonefn2.data, 1, "friday")
            dbFunc.add_calls_lesson(a, 3, form.ptonest3.data, form.ptonefn3.data, 1, "friday")
            dbFunc.add_calls_lesson(a, 4, form.ptonest4.data, form.ptonefn4.data, 1, "friday")
            dbFunc.add_calls_lesson(a, 5, form.ptonest5.data, form.ptonefn5.data, 1, "friday")
            dbFunc.add_calls_lesson(a, 6, form.ptonest6.data, form.ptonefn6.data, 1, "friday")

            dbFunc.add_calls_lesson(a, 1, form.pttwost1.data, form.pttwofn1.data, 2, "friday")
            dbFunc.add_calls_lesson(a, 2, form.pttwost2.data, form.pttwofn2.data, 2, "friday")
            dbFunc.add_calls_lesson(a, 3, form.pttwost3.data, form.pttwofn3.data, 2, "friday")
            dbFunc.add_calls_lesson(a, 4, form.pttwost4.data, form.pttwofn4.data, 2, "friday")
            dbFunc.add_calls_lesson(a, 5, form.pttwost5.data, form.pttwofn5.data, 2, "friday")
            dbFunc.add_calls_lesson(a, 6, form.pttwost6.data, form.pttwofn6.data, 2, "friday")

            dbFunc.add_calls_lesson(a, 1, form.sbonest1.data, form.sbonefn1.data, 1, "saturday")
            dbFunc.add_calls_lesson(a, 2, form.sbonest2.data, form.sbonefn2.data, 1, "saturday")
            dbFunc.add_calls_lesson(a, 3, form.sbonest3.data, form.sbonefn3.data, 1, "saturday")
            dbFunc.add_calls_lesson(a, 4, form.sbonest4.data, form.sbonefn4.data, 1, "saturday")
            dbFunc.add_calls_lesson(a, 5, form.sbonest5.data, form.sbonefn5.data, 1, "saturday")
            dbFunc.add_calls_lesson(a, 6, form.sbonest6.data, form.sbonefn6.data, 1, "saturday")

            dbFunc.add_calls_lesson(a, 1, form.sbtwost1.data, form.sbtwofn1.data, 2, "saturday")
            dbFunc.add_calls_lesson(a, 2, form.sbtwost2.data, form.sbtwofn2.data, 2, "saturday")
            dbFunc.add_calls_lesson(a, 3, form.sbtwost3.data, form.sbtwofn3.data, 2, "saturday")
            dbFunc.add_calls_lesson(a, 4, form.sbtwost4.data, form.sbtwofn4.data, 2, "saturday")
            dbFunc.add_calls_lesson(a, 5, form.sbtwost5.data, form.sbtwofn5.data, 2, "saturday")
            dbFunc.add_calls_lesson(a, 6, form.sbtwost6.data, form.sbtwofn6.data, 2, "saturday")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_cals.html", form=form)


def timer():
    while True:
        send_statistic()
        time.sleep(604800)


th1 = threading.Thread(target=timer)
th1.start()


