import os

from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def add(x, y):
    print(x + y)
    return x + y


def send_mail(recipient, subject, text):
    import smtplib, ssl

    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "my5454@gmail.com"
    receiver_email = recipient
    password = os.environ.get("EMAIL_PASSWORD")
    message = text

    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv2)
    with smtplib.SMTP(host=smtp_server, port=port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
