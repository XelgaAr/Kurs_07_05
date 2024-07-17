import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery, shared_task

app = Celery('tasks', broker=f'pyamqp://guest@{os.environ.get("RABBIT_HOST", "localhost")}:5432')


@app.task
def send_mail(recipient, subject, text):
    import ssl
    import smtplib

    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "jttjdev@gmail.com"
    receiver_email = recipient
    password = os.environ.get("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(text, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(host=smtp_server, port=port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
