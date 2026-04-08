import logging
import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

def format_email_body(episodes):
	'''
	Constructs a plain text email body with clearly separated section headers
	from a dictionary of episodes grouped by feed.
	'''
	if not len(episodes):
		return "No new AI updates in the last 24 hours."
	
	lines = ["Here is your daily AI feed update:\n"]

	for ep in episodes:
		#source header
		lines.append('='*50)
		lines.append(f'Source: {ep.source.upper()}')
		lines.append('='*50+'\n')

		lines.append(f'TITLE: {ep.title} | {ep.duration}')
		lines.append(f'PUBLISHED: {ep.pub_date_mt}')
		lines.append(f'LINK: {ep.episode_link}\n')
		lines.append(f'SUMMARY:\n{ep.summary}\n')
		lines.append(f'-'*100+'\n')

	return '\n'.join(lines)

def send_email(body_text):
	'''
	Connects to an SMTP server, authenticates, and dispatches the email.
	'''
	SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
	SENDER_APP_PASS = os.environ.get("SENDER_APP_PASS")
	RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

	if not all([SENDER_EMAIL, SENDER_APP_PASS, RECEIVER_EMAIL]):
		logger.error("Missing email credentials. Ensure SENDER_EMAIL, SENDER_APP_PASS, and RECEIVER_EMAIL are set in your environment.")
		return
	
	#compile email
	msg = EmailMessage()
	msg.set_content(body_text)
	msg['Subject'] = f"Daily AI Feed Update - {datetime.now().strftime('%Y-%m-%d')}"
	msg['From'] = SENDER_EMAIL
	msg['To'] = RECEIVER_EMAIL

	try:
		#setup smtplib using Gmail's standard TLS port
		with smtplib.SMTP('smtp.gmail.com', 587) as server:
			server.starttls()
			#authenticate
			server.login(SENDER_EMAIL, SENDER_APP_PASS)#type: ignore
			server.send_message(msg)
			logger.info("Email successfully dispatched.")
	except smtplib.SMTPAuthenticationError:
		logger.error("SMTP Authentication Error: Check the App Password.")
	except Exception as e:
		logger.error(f'Failed to send email. Error: {e}')

