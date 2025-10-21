from db_connection import execute_query
import streamlit as st

def run(connection, days=30, user=None):
    sql = """
        SELECT 
            ms.vendor,
            ROUND(SUM(ms.amount), 2) AS total_spent,
            COUNT(*) AS count
        FROM money_spent ms
        WHERE ms.subscription = 'y'
          AND ms.event_datetime >= NOW() - INTERVAL %s DAY
          {user_filter}
        GROUP BY ms.vendor
        ORDER BY total_spent DESC;
    """

    user_filter = "AND ms.username = %s" if user else ""
    final_sql = sql.format(user_filter=user_filter)
    params = (days, user) if user else (days,)

    results = execute_query(connection, final_sql, params)

    title = f"Recurring Charges (Last {days} Days)"
    if user:
        title += f" for {user}"
    print(f"\n🔁 {title}")
    print("-" * len(title))
    for vendor, total, count in results:
        print(f"{vendor:<22} ${total:>8.2f}  ({count} txns)")

    return results

