from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
import os
import smtplib

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USERNAME = 'malikdayat1207@gmail.com'
SMTP_PASSWORD = ''
SECRET_KEY = os.environ.get('AKU', 'default_secret_key')

# Ensure SECRET_KEY is not None or empty
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")

# Serializer for generating and validating tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)

def send_reset_email(email, reset_link):
    msg = MIMEMultipart()
    msg['From'] = "admin@rootme.com
    msg['To'] = email
    msg['Subject'] = 'Password Reset Request'

    body = f'Please click the link to reset your password: {reset_link}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()
        print("SUCCESS")
        return {"message": "Reset email sent successfully", "status": "success"}
    except Exception as e:
        print("ERROR", e)
        return {"message": "Failed to send reset email", "error": str(e), "status": "failed"}

def generate_reset_link(email):
    token = serializer.dumps(email, salt='INIRESET')
    reset_link = f'http://localhost:5000/reset_password/{token}'
    return reset_link

def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt='INIRESET', max_age=expiration)
        print(email)
    except Exception as e:
        return None
    return email

# TEsting
send_reset_email("azka.naim0103@gmail.com", "INI LINK")
