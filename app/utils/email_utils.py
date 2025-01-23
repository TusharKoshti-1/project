import smtplib
from email.mime.text import MIMEText

async def send_email(to_email: str, subject: str, body: str):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
