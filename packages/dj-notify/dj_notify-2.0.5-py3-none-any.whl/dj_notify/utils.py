from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client

def send_email(subject, message, recipient_email):
    sender = getattr(settings, 'DJ_NOTIFY_DEFAULT_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
    try:
        result = send_mail(subject, message, sender, [recipient_email])
        if result:
            return True, None
        return False, 'send_mail returned 0 (not sent)'
    except Exception as e:
        return False, str(e)

def send_whatsapp(message, recipient_number):
    sender = settings.TWILIO_WHATSAPP_NUMBER
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(
            body=message,
            from_=f"whatsapp:{sender}",
            to=f"whatsapp:{recipient_number}",
        )
        if msg.sid:
            return True, None
        return False, 'Twilio response missing SID'
    except Exception as e:
        return False, str(e)
