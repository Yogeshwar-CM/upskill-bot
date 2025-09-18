import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_ai_response(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        json_response = response.json()
        return json_response['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        return f"Error: Could not retrieve AI response. Details: {e}"
    except (KeyError, IndexError) as e:
        return "Error: The AI response was not in the expected format."

def send_email(html_content):
    sender_email = os.environ.get("GMAIL_ADDRESS")
    receiver_email = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your AI-Powered Daily Briefing 🚀"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(html_content, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    try:
        with open("config.txt", "r") as f:
            prompts = [line.strip() for line in f if line.strip() and ':' in line]
    except FileNotFoundError:
        print("Error: config.txt not found!")
        prompts = []

    email_body = "<h1>Your Daily Upskilling Briefing</h1>"
# REPLACE IT WITH THIS BLOCK
    for prompt_line in prompts:
        topic, prompt = prompt_line.split(':', 1)
        print(f"Processing topic: {topic.strip()}...")
        ai_response = get_ai_response(prompt.strip())

        # First, format the response string
        formatted_response = ai_response.replace('\n', '<br>')
        # Then, add it to the email body
        email_body += f"<h2>{topic.strip()}</h2><p>{formatted_response}</p><hr>"
    if prompts:
        send_email(email_body)
    else:
        print("No prompts found in config.txt. No email sent.")
