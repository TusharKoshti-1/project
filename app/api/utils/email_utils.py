import smtplib
from email.mime.text import MIMEText


class EmailUtils:
    def __init__(self, sender_email: str, sender_password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, to_email: str, subject: str, body: str):
        # Create the email message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = to_email

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted TLS connection
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
