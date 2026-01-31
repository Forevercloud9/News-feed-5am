import logging
import datetime
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv() # Load environment variables

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, provider='mock', sender_email=None, password=None):
        self.provider = provider
        self.sender_email = sender_email or os.getenv('GMAIL_SENDER')
        self.password = password or os.getenv('GMAIL_APP_PASSWORD')
        
    def format_email_content(self, title, summary):
        """
        Creates a simple HTML template for the email.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">Morning 5 Daily Digest</h1>
                <p style="color: #7f8c8d;">{today}</p>
                <hr>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="margin-top: 0;">{title}</h2>
                    <p style="line-height: 1.6;">{summary}</p>
                    <a href="#" style="color: #3498db; text-decoration: none;">Read full article</a>
                </div>

                <div style="font-size: 12px; color: #999; text-align: center; margin-top: 30px;">
                    <p>You received this email because you are subscribed to Morning 5.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def send_daily_digest(self, recipients, content):
        """
        Sends the digest to a list of recipients.
        """
        for recipient in recipients:
            self.send_email(recipient, "Morning 5 Daily Digest", content)

    def send_email(self, to_email, subject, body):
        """
        Sends a single email. 
        """
        if self.provider == 'mock':
            logger.info(f"[MOCK] Sending email to {to_email} | Subject: {subject}")
            filename = f"email_to_{to_email}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"<!-- To: {to_email} -->\n")
                f.write(f"<!-- Subject: {subject} -->\n")
                f.write(body)
            logger.info(f"[MOCK] Email content saved to {filename}")
            return True

        elif self.provider == 'gmail':
            if not self.sender_email or not self.password:
                logger.error("Gmail credentials (sender_email, password) are missing.")
                return False

            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))

                # Connect to Gmail SMTP Server
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(self.sender_email, self.password)
                text = msg.as_string()
                server.sendmail(self.sender_email, to_email, text)
                server.quit()
                
                logger.info(f"[GMAIL] Email sent successfully to {to_email}")
                return True
            except Exception as e:
                logger.error(f"[GMAIL] Failed to send email: {str(e)}")
                return False

        else:
            logger.warning(f"Provider {self.provider} not supported.")
            return False
