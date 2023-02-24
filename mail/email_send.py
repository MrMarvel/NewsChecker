import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config_utils import ConfigConstants, create_or_update_config


def send():
    # Read email information from configuration file
    config = create_or_update_config()
    from_email = config.get("email", "from_email")
    to_email = config.get("email", "to_email")
    password = config.get(ConfigConstants.EMAIL_TOPIC, ConfigConstants.PASSWORD, raw=True)
    subject = "Test HTML email"

    # HTML body of the email
    html = """
    <html>
      <head></head>
      <body>
        <p>This is a test HTML email.</p>
        <p>You can add <strong>bold</strong> and <em>italic</em> text.</p>
      </body>
    </html>
    """

    # Create the email message object
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    # Attach the HTML body to the email
    html_body = MIMEText(html, "html")
    message.attach(html_body)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
        server.ehlo()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message.as_string())
        server.close()

    print("Email sent!")
