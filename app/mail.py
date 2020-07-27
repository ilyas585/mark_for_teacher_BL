from flask_mail import Message
from app.models import *
from app import app, mail
from flask import url_for
from app.tokenn import generate_confirmation_token, confirm_token
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


def send_mail2(to, text):
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        msg = MIMEMultipart()                               # Создаем сообщение
        msg['From'] = "onextopplay@gmail.com"                          # Адресат
        msg['To'] = to                            # Получатель
        msg['Subject'] = 'Здравствуйте вот ваша статистика за неделю(Сылка будет доступна в течении недели после получения письма) на сайте будет отображаться актуальная статистика на данный момент времени'
        msg.attach(MIMEText(text, 'plain'))
        smtpObj.login('onextopplay@gmail.com', 'enovzewxqolwlbha')
        smtpObj.send_message(msg)
        smtpObj.quit()
    except:
        pass