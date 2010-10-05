from django import template
from datetime import timedelta, datetime

register = template.Library()

@register.filter
def date_within_past_days(value, arg):
    # question: does datetime.now() do a syscall each time is it called?
    return value > (datetime.now() - timedelta(days=int(arg)))
