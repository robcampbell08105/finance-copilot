from db_connection import execute_query
import streamlit as st
import os

def run(connection, days=30, user=None, category=None, start_date=None, end_date=None):
    params = []

    sql = """
        SELECT 
            COALESCE(ms.cat, 'Uncategorized') AS category,
            ROUND(SUM(ms.amount), 2) AS total_spent,
            COUNT(*) AS transactions
        FROM money_spent ms
        WHERE 1=1
    """

    # Date filtering
    if start_date and end_date:
        sql += " AND ms.event_datetime >= %s AND ms.event_datetime < %s"
        params += [start_date, end_date]
    else:
        sql += " AND ms.event_datetime >= NOW() - INTERVAL %s DAY"
        params.append(days)

    # User filtering
    if user:
        sql += " AND ms.username = %s"
        params.append(user)

    exclude_user = os.getenv("COPILOT_EXCLUDE_USER")
    if exclude_user:
        sql += " AND username != %s"
        params.append(exclude_user)

    # Category filter (optional — from NL query)
    if category:
        sql += " AND ms.cat = %s"
        params.append(category)

    sql += """
        GROUP BY category
        ORDER BY total_spent DESC
        LIMIT 10;
    """

    print("🔎 SQL:", sql)
    print("📦 Params:", params)

    results = execute_query(connection, sql, params) or []

    # Fallback message applied immediately
    label = "No data found"

    if results:
        if len(results) == 1:
            cat, total, count = results[0]
            label = f"{user} spent ${total:.2f} on {cat} ({count} transactions)"
            print(f"\n💸 {label}")
        else:
            label = "Top Categories"
            if start_date and end_date:
                label += f" from {start_date} to {end_date}"
            else:
                label += f" (Last {days} Days)"
            if user:
                label += f" for {user}"

            print(f"\n📂 {label}")
            print("-" * len(label))
            print("🧪 Raw results:", results)

    return results, label

