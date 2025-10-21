import re
from datetime import timedelta
from utils.query_filters import get_date_range
import dateparser

CANDIDATE_NAMES = {
    "robert": "Robert",
    "julie": "Julie",
    "maija": "Maija"
}

def resolve_named_user(text: str):
    for name in CANDIDATE_NAMES:
        if name in text.lower():
            return CANDIDATE_NAMES[name]
    return None

def parse_nl_input(text, current_user=None):
    # Normalize common phrases
    text = text.lower()
    text = text.replace("this past week", "last 7 days")
    text = text.replace("past week", "last 7 days")
    text = text.replace("last weekend", "last saturday to last sunday")
    text = text.replace("past 3 days", "last 3 days")

    print(f"📝 Raw query received: {text}")

    insight = None
    days = 30
    start_date, end_date = None, None
    category = None
    user = None
    exclude_user = None

    me = current_user.strip() if current_user else None

    # 👤 Pronouns
    if me and re.search(r"\b(i|me)\b", text):
        user = me
    elif me and "them" in text:
        exclude_user = me
    else:
        user = resolve_named_user(text)

    # 🧠 Default to current_user if no user detected
    if not user and not exclude_user and me:
        user = me

    # 💡 Type of insight
    if "vendor" in text:
        insight = "vendors"
    elif "category" in text or "categories" in text:
        insight = "categories"
    elif "subscription" in text or "recurring" in text:
        insight = "subscriptions"
    elif "spend" in text or "spent" in text or "spending" in text:
        insight = "categories"

    # 📅 Time window (predefined phrases)
    for phrase in [
        "today", "yesterday", "this week", "this past week", "last week", "this month",
        "last month", "this year", "last year", "a year ago", "last 7 days", "last 3 days",
        "last weekend", "this weekend", "this quarter", "this last quarter", "first quarter",
        "last quarter"
    ]:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            start_date, end_date = get_date_range(phrase)
            break

    # 📅 Absolute date detection
    if start_date is None and end_date is None:
        match = re.search(r"(on\s+)?([a-zA-Z]+\s+\d{1,2}(st|nd|rd|th)?(,?\s+\d{4})?)", text)
        if match:
            date_text = match.group(2)
            parsed = dateparser.parse(date_text)
            if parsed:
                start_date = parsed.date()
                end_date = start_date + timedelta(days=1)

    # 🎯 Categories
    if "fast food" in text:
        category = "Fast Food"
    elif "takeout" in text:
        category = "Takeout"
    elif "groceries" in text:
        category = "Groceries"
    elif "fuel" in text or "gas" in text:
        category = "Fuel"
    elif "shopping" in text:
        category = "Shopping"
    elif "medical" in text:
        category = "Medical"

    return insight, days, user, category, start_date, end_date, exclude_user

