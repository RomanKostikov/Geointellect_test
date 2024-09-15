import smtplib
from email.mime.text import MIMEText
import os

# Получаем параметры для отправки писем из переменных среды
MAIL_HOST = os.getenv('MAIL_HOST', 'localhost')
MAIL_PORT = int(os.getenv('MAIL_PORT', 1025))


def send_email(subject, body, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'sender@example.com'
    msg['To'] = recipient

    # Используем переменные среды для хоста и порта
    with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
        server.send_message(msg)
