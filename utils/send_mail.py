import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import cryptocode
import json

def send_mail(errorBot, command):
    """
    Send an email notification when an error occurs.

    Args:
        errorBot (str): The error message.
        command (str): The command that caused the error.
    """

    with open("./data.json") as jsonFile:
        DataJson = json.load(jsonFile)
        jsonFile.close()

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = cryptocode.decrypt(DataJson["MAIL_ID"], DataJson["CRYPT"])
    smtp_password = cryptocode.decrypt(DataJson["MAIL_MDP"], DataJson["CRYPT"])

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)

    sender_email = "IPI Bot"
    recipient_email = DataJson["SEND_TO"]
    subject = "[IPI Bot] Une erreur est survenue"
    message_text = f'Une erreur est survenue le {datetime.now().strftime("%d/%m/%Y")} à {datetime.now().strftime("%H:%M:%S")} dans la commande "{command}" : \n\n{errorBot}'

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message_text, "plain"))
    smtp.sendmail(sender_email, recipient_email, msg.as_string())
    smtp.quit()
