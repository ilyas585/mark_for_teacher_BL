from app.models import *


def get_stats(id_teacher):
    lesson_interest = []
    lesson_comprehensibility = []
    teacher_behavior = []
    r1 = 0
    r2 = 0
    r3 = 0
    b = 0
    a = db.session.query(Assessment).filter_by(id_teacher=id_teacher).all()
    for i in a:
        time = i.time.strftime("%Y-%m-%d")
        lesson_interest.append([i.lesson_interest, time])
        lesson_comprehensibility.append([i.lesson_comprehensibility, time])
        teacher_behavior.append([i.teacher_behavior, time])
    for i in lesson_interest:
        r1 += i[0]
        b += 1
    r1 = r1 / b
    b = 0
    for i in lesson_comprehensibility:
        r2 += i[0]
        b += 1
    r2 = r2 / b
    b = 0
    for i in teacher_behavior:
        r3 += i[0]
        b += 1
    r3 = r3 / b
    a = db.session.query(Teachers).filter_by(id=id_teacher).all()
    name = a[0].name
    surname = a[0].surname
    patronymic = a[0].patronymic
    return [
        {

            "id_teacher": id_teacher,
            "lesson_interest": lesson_interest,
            "lesson_com": lesson_comprehensibility,
            "teacher_behavior": teacher_behavior

        }
        , round(r1, 2), round(r2, 2), round(r3, 2), name, surname, patronymic
    ]
