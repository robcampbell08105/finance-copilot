from datetime import datetime, timedelta
import calendar

from datetime import datetime, timedelta

def get_date_range(term: str):
    today = datetime.today().date()
    weekday = today.weekday()
    term = term.lower()
    start = end = None

    if term == "today":
        start = today
        end = today + timedelta(days=1)

    elif term == "yesterday":
        start = today - timedelta(days=1)
        end = today

    elif term == "this week":
        start = today - timedelta(days=weekday)
        end = start + timedelta(days=7)

    elif term == "last week":
        start = today - timedelta(days=weekday + 7)
        end = start + timedelta(days=7)

    elif term == "this month":
        start = today.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1)
        else:
            end = start.replace(month=start.month + 1, day=1)

    elif term == "last month":
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = first_this_month

    elif term == "this year":
        start = today.replace(month=1, day=1)
        end = start.replace(year=start.year + 1)

    elif term == "last year":
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(month=1, day=1)

    elif term == "a year ago":
        start = today - timedelta(days=365)
        end = start + timedelta(days=1)

    elif term == "last 7 days":
        start = today - timedelta(days=7)
        end = today + timedelta(days=1)

    elif term == "last 3 days":
        start = today - timedelta(days=3)
        end = today + timedelta(days=1)

    elif term == "last weekend":
        # Saturday and Sunday of the previous week
        last_saturday = today - timedelta(days=weekday + 2)
        last_sunday = last_saturday + timedelta(days=1)
        start = last_saturday
        end = last_sunday + timedelta(days=1)

    return (str(start), str(end)) if start and end else (None, None)

def resolve_user_pronouns(text: str, current_user: str = None):
    text = text.lower()
    user = None
    exclude_user = None

    if "me" in text or "i " in text or text.startswith("i "):
        user = current_user
    elif "them" in text:
        user = None
        exclude_user = current_user

    return user, exclude_user

