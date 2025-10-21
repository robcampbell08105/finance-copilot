import sys
import os
import re
from copilot import run_from_args
from copilot_debug import parse_args_with_debug
from nl_query.parse_nl_input import parse_nl_input

# CLI args
debug, args = parse_args_with_debug(sys.argv[1:])
query = " ".join([arg for arg in args if arg not in ["--debug", "--verbose"]])

def main():
    if not query.strip():
        print("❗ Please provide a natural language query.")
        sys.exit(1)

    insight, days, user, category, start_date, end_date, _ = parse_nl_input(query)

    if not insight:
        print("🤔 I couldn’t detect what kind of insight you want.")
        print("Try asking about vendors, categories, or subscriptions.")
        return

    if start_date:
        os.environ["COPILOT_DATE_START"] = start_date
    if end_date:
        os.environ["COPILOT_DATE_END"] = end_date
    if category:
        os.environ["COPILOT_CATEGORY"] = category

    run_from_args(insight, days, user)

if __name__ == "__main__":
    main()

