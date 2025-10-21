import argparse
import logging
import db_connection
from insights import top_vendors, category_summary, subscription_summary
import os

log_level = os.environ.get("COPILOT_LOG_LEVEL", "WARNING").upper()

# Setup basic logging
logging.basicConfig(level=getattr(logging, log_level), format="%(levelname)s: %(message)s")

def run_from_args(insight, days, user=None, config="/home/rwcampbell/.my.cnf", section="clientfinance"):
    start_date = os.getenv("COPILOT_DATE_START")
    end_date = os.getenv("COPILOT_DATE_END")
    category = os.getenv("COPILOT_CATEGORY")

    conn = db_connection.connect_to_database(config, section=section)
    if insight == "vendors":
        results, label = top_vendors.run(conn, days, user, start_date, end_date)
        print(f"\n🧾 {label}")
        for vendor, total, count in results:
            print(f"{vendor:<20} ${total:>8.2f}  ({count} transactions)")
        top_vendors.run(conn, days, user, start_date, end_date)
    elif insight == "categories":
        results = category_summary.run(conn, days, user, category, start_date, end_date)
    elif insight == "subscriptions":
        subscription_summary.run(conn, days, user)
    else:
        print(f"Unknown insight: {insight}")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="📊 Your Financial Copilot")
    parser.add_argument(
        "--insight",
        choices=["vendors", "categories", "subscriptions"],  # ✅ add new insights here
        required=True,
        help="Type of insight to generate"
    )
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    parser.add_argument("--user", help="Filter by username (optional)")
    parser.add_argument("--config", default="/home/rwcampbell/.my.cnf", help="Path to your MySQL config file")
    parser.add_argument("--section", default="clientfinance", help="Section in config file for DB connection")

    args = parser.parse_args()

    #run_from_args(args.insight, args.days, args.user, args.config, args.section)

if __name__ == "__main__":
    main()

