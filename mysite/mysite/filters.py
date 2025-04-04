from datetime import datetime
from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter(name='time_until_next_review')
def time_until_next_review(value):
    """
    This filter calculates the time difference between the current time and
    the given next_review_date, and returns a human-readable format.
    """
    if not value:
        return "No next review date"

    # Ensure value is a datetime object (it should be a datetime in the model)
    now_time = now()
    delta = value - now_time

    # If the review date is in the past
    if delta.days < 0:
        return "This card was due in the past."

    # Time difference in hours, minutes, and days
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    time_diff = []

    if days > 0:
        time_diff.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        time_diff.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        time_diff.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

    return ' '.join(time_diff) if time_diff else "Less than a minute"
