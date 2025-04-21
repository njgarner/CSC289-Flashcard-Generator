from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from .models import Reminder

@shared_task
def send_reminder_email_task(reminder_id):
    try:
        # Fetch reminder from the database
        reminder = Reminder.objects.get(id=reminder_id)

        # Check if the reminder's date has passed
        if reminder.date_time <= now():
            # Send email
            subject = f"Study Reminder: {reminder.title}"
            message = f"Hey there!\n\nThis is a reminder for your scheduled study time.\n\nTitle: {reminder.title}\nDescription: {reminder.description}\n\nDon't forget to study! 📚"
            from_email = "noreply@yourdomain.com"
            recipient_list = [reminder.email]

            send_mail(subject, message, from_email, recipient_list)

            return f"Reminder email sent to {reminder.email}"
        else:
            return "Reminder not due yet"
    except Reminder.DoesNotExist:
        return "Reminder not found"