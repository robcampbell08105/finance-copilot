from db_connection import execute_query
import streamlit as st
import pandas as pd
import os

def run(connection, days=30, user=None, start_date=None, end_date=None):
    sql = """
        SELECT
            v.vendor AS vendor_name,
            ROUND(SUM(ms.amount), 2) AS total_spent,
            COUNT(*) AS transactions
        FROM money_spent ms
        JOIN money_spent_vendors msv ON ms.event_id = msv.event_id
        JOIN vendors v ON msv.vendor_id = v.vendor_id
        WHERE 1=1
    """
    params = []

    if start_date and end_date:
        sql += " AND ms.event_datetime >= %s AND ms.event_datetime < %s"
        params += [start_date, end_date]
    else:
        sql += " AND ms.event_datetime >= NOW() - INTERVAL %s DAY"
        params.append(days)

    if user:
        sql += " AND ms.username = %s"
        params.append(user)
    
    exclude_user = os.getenv("COPILOT_EXCLUDE_USER")
    if exclude_user:
        sql += " AND username != %s"
        params.append(exclude_user)

    sql += """
        GROUP BY vendor_name
        ORDER BY total_spent DESC
        LIMIT 10;
    """.format("AND ms.username = %s" if user else "")

    params = (days,) if not user else (days, user)
    results = execute_query(connection, sql, params)

    print(f"🔍 Results: {results}")

    label = f"Top Vendors (Last {days} Days)"
    if user:
        label += f" for {user}"
    print(f"\n🧾 {label}")
    print("-" * len(label))
    for vendor, total, count in results:
        print(f"{vendor:<20} ${total:>8.2f}  ({count} transactions)")

    df = pd.DataFrame(results, columns=["Vendor", "Total Spent", "Transactions"])
    return df
    return results, label
