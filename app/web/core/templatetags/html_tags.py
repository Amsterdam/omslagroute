from django import template
from django.contrib.auth.models import Group
from web.users.auth import auth_test
register = template.Library()
from datetime import datetime, date
from django.utils.html import mark_safe


@register.filter(name='linebreaks2html')
def linebreaks2html(txt):
    if txt:
        return txt.replace("\n", "<br />")
    return ''


@register.filter(name='is_date')
def is_date(str_date):
    try:
        return isinstance(datetime.strptime(str_date, "%d-%m-%Y"), (date, datetime))
    except:
        return False


@register.filter(name='str_date_to_date')
def str_date_to_date(str_date):
    return datetime.strptime(str_date, "%d-%m-%Y")


@register.filter(name='timestamp_to_date')
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)


@register.filter(name='textile')
def textile(textile_str):
    from textile import textile
    return mark_safe(textile(str(textile_str)))


@register.filter(name='range')
def _range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)


@register.filter
def duration(td):

    total_seconds = int(td.total_seconds())

    if total_seconds <= 0:
        return 'Kan verwijderd worden'

    days = total_seconds // 86400
    remaining_hours = total_seconds % 86400
    remaining_minutes = remaining_hours % 3600
    hours = remaining_hours // 3600
    minutes = remaining_minutes // 60
    seconds = remaining_minutes % 60

    days_str = f'{days}d ' if days else ''
    hours_str = f'{hours}u ' if hours else ''
    minutes_str = f'{minutes}m ' if minutes else ''
    seconds_str = f'{seconds}s' if seconds and not hours_str else ''

    return f'{days_str}{hours_str}{minutes_str}{seconds_str}'
