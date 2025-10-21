import re
import sys
import os
from datetime import datetime, timedelta

from copilot import run_from_args
from copilot_debug import parse_args_with_debug
from utils.query_filters import get_date_range

# 💡 Mapping of recognized user names
CANDIDATE_NAMES = {
    "robert": "Robert",
    "julie": "Julie",
    "maija": "Maija"
}

# Parse CLI args (for standalone mode)
debug, args = parse_args_with_debug(sys.argv[1:])
args = [arg for arg in sys.argv[1:] if arg not in ["--debug", "--verbose"]]
query = " ".join(args)

def resolve_named_user(text: str):
    for name in CANDIDATE_NAMES:
        if name in text:
            return CANDIDATE_NAMES[name]
    return None

def parse_nl_input(text, current_user=None):
    text = text.lower()
    print(f"📝 Raw query received: {text}")

    # Set defaults
    insight = None
    days = 30
    start_date, end_date = None, None
    category = None
    user = None
    exclude_user = None

    # Resolve current user ("me") from sidebar or env
    me = current_user.strip() if current_user else None
    print(f"🧭 Pronoun debug — current_user: {current_user}, me: {me}")

    # Pronoun matching
    if me and re.search(r"\b(i|me)\b", text):
        print("✅ Detected pronoun match for 'I' or 'me'")
        user = me
    elif me and "them" in text:
        exclude_user = me
    else:
        user = resolve_named_user(text)

    # Detect insight type
    if "vendor" in text:
        insight = "vendors"
    elif "category" in text or "categories" in text:
        insight = "categories"
    elif "subscription" in text or "recurring" in text:
        insight = "subscriptions"
    elif "spend" in text or "spent" in text or "spending" in text:
        insight = "categories"

    # Date detection
    for phrase in [
        "today", "yesterday", "this week", "last week", "this month",
        "last month", "this year", "last year", "a year ago"
    ]:
        if re.search(rf"\b{re.escape(phrase)}\b", text):
            start_date, end_date = get_date_range(phrase)
            print(f"📆 Detected phrase: '{phrase}' → start={start_date}, end={end_date}")
            break

    # Category match
    if "fast food" in text:
        category = "Fast Food"

    return insight, days, user, category, start_date, end_date, exclude_user

def main():
    if not query.strip():
        if debug:
            print("❗ Please provide a natural language query.")
        sys.exit(1)

    insight, days, user, category, start_date, end_date, _ = parse_nl_input(query)

    if not insight:
        print("🤔 I couldn’t detect what kind of insight you want.")
        print("Try asking about vendors, categories, or subscriptions.")
        return

    if start_date and end_date:
        os.environ["COPILOT_DATE_START"] = start_date
        os.environ["COPILOT_DATE_END"] = end_date

    if category:
        os.environ["COPILOT_CATEGORY"] = category

    if not start_date and not end_date:
        match = re.search(r"last (\d+)\s*(day|week|month|year)s?", query)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            days = value * {"day": 1, "week": 7, "month": 30, "year": 365}[unit]

    if debug:
        print(f"🔍 Interpreted: insight='{insight}', days={days}, user='{user}'")

    os.environ["COPILOT_LOG_LEVEL"] = "DEBUG" if debug else "WARNING"
    run_from_args(insight, days, user)

if __name__ == "__main__":
    main()

