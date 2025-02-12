# email/email_functions.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(smtp_server, port, sender_email, sender_password, recipient_emails, subject, body, attachment_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully to:", ", ".join(recipient_emails))
    except Exception as e:
        print(f"Failed to send email: {e}")
