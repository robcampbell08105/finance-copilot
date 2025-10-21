import streamlit as st
from copilot import run_from_args
from insights import top_vendors, category_summary, subscription_summary
import nl_query
import db_connection
import pandas as pd
import sys
import logging
import os
from nl_query.parse_nl_input import parse_nl_input
from vendor_dashboard import run_vendor_mapping_dashboard

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

st.set_page_config(page_title="💸 Family Spending", layout="wide")

# Sidebar navigation
st.sidebar.title("🔍 Explore Insights")
page = st.sidebar.radio("Choose a view:", ["Natural Language", "Categories", "Vendors", "Subscriptions", "🧠 Vendor Mapping"])

user = st.sidebar.selectbox("Select a user:", ["(All Users)", "Robert", "Julie", "Maija"])
user_filter = None if user == "(All Users)" else user

days = st.sidebar.number_input("Look back (days):", min_value=1, max_value=3650, value=30, step=1)

# Connect to the database
conn = db_connection.connect_to_database("/home/rwcampbell/.my.cnf", section="clientfinance")

def run_nl_query(connection):

    st.subheader("💬 Ask a Question About Spending")

    query_text = st.text_input("Type your question:", placeholder="e.g. How much did Robert spend on fast food?")

    if not query_text:
        return

    if not user_filter:
        st.warning("⚠️ To use phrases like 'I spent...' please select a user from the sidebar.")
    
    # 🩹 NEW: Enforce a valid user for pronoun resolution
    current_user = user_filter or None
    if not current_user:
        st.warning("⚠️ Select a user from the sidebar to use 'I' or 'me' in natural language queries.")
        return

    sys.stderr.write(f"✅ Passing current_user = {current_user}\n")
    insight, days, user, category, start_date, end_date, exclude_user = parse_nl_input(query_text, current_user)

    sql_total = "SELECT ROUND(COALESCE(SUM(amount), 0), 2) AS total_spent FROM money_spent WHERE 1=1"
    params_total = []

    if user:
        sql_total += " AND username = %s"
        params_total.append(user)

    if category:
        sql_total += " AND cat = %s"
        params_total.append(category)

    if start_date and end_date:
        sql_total += " AND event_datetime >= %s AND event_datetime < %s"
        params_total += [start_date, end_date]

    result_total = db_connection.execute_query(connection, sql_total, params_total)
    df_total = pd.DataFrame(result_total, columns=["Total Spent"])

    sql_vendor = """
    SELECT vendor, ROUND(SUM(amount), 2) AS spent
    FROM money_spent WHERE 1=1
    """
    params_vendor = []

    if user:
        sql_vendor += " AND username = %s"
        params_vendor.append(user)

    if category:
        sql_vendor += " AND cat = %s"
        params_vendor.append(category)

    if start_date and end_date:
        sql_vendor += " AND event_datetime >= %s AND event_datetime < %s"
        params_vendor += [start_date, end_date]

    sql_vendor += " GROUP BY vendor ORDER BY spent DESC"

    result_vendor = db_connection.execute_query(connection, sql_vendor, params_vendor)
    df_vendor = pd.DataFrame(result_vendor, columns=["Vendor", "Spent"])

    sql_cat = """
    SELECT cat, ROUND(SUM(amount), 2) AS spent
    FROM money_spent WHERE 1=1
    """
    params_cat = []

    if user:
        sql_cat += " AND username = %s"
        params_cat.append(user)

    if category:
        sql_cat += " AND cat = %s"
        params_cat.append(category)

    if start_date and end_date:
        sql_cat += " AND event_datetime >= %s AND event_datetime < %s"
        params_cat += [start_date, end_date]

    sql_cat += " GROUP BY cat ORDER BY spent DESC"

    result_cat = db_connection.execute_query(connection, sql_cat, params_cat)
    df_cat = pd.DataFrame(result_cat, columns=["Category", "Spent"])

    sys.stderr.write("🌐 [WEB QUERY DEBUG]\n")
    sys.stderr.write(f"start_date: {start_date}\n")
    sys.stderr.write(f"end_date  : {end_date}\n")
    sys.stderr.write(f"user      : {user}\n")
    sys.stderr.write(f"category  : {category}\n")


    group_by_user = "each person" in query_text.lower() or "each user" in query_text.lower()

    st.info(f"🧠 Interpreted: user = {user}, exclude = {exclude_user}, start = {start_date}, category = {category}")

    sql = "SELECT "
    if group_by_user:
        sql += "username, "
    sql += "ROUND(COALESCE(SUM(amount), 0), 2) AS total_spent FROM money_spent WHERE 1=1"

    params = []
    if category:
        sql += " AND cat = %s"
        params.append(category)

    if user:
        sql += " AND username = %s"
        params.append(user)

    if group_by_user:
        sql += " GROUP BY username ORDER BY total_spent DESC"

    if start_date and end_date:
        sql += " AND event_datetime >= %s AND event_datetime < %s"
        params += [start_date, end_date]

    results = db_connection.execute_query(connection, sql, params)
    columns = ["User", "Total Spent"] if group_by_user else ["Total Spent"]
    df = pd.DataFrame(results, columns=columns)
    
    # Optional defensive fix:
    df.fillna(0, inplace=True)
   
    st.subheader("🧾 Total Spent")
    st.dataframe(df_total)

    st.subheader("🏷️ Spending by Vendor")
    st.dataframe(df_vendor)

    st.subheader("📂 Spending by Category")
    st.dataframe(df_cat)

    st.warning(f"🚧 No data found for {user or current_user} on {start_date}")

    st.success("✅ Query executed successfully!")
    if df.empty:
        st.warning("No spending found for this query — try broadening the date or user.")
        df = pd.DataFrame([[0]], columns=["Total Spent"])  # force display
    else:
        st.dataframe(df)

    st.info(f"Filters → user: {user}, dates: {start_date} to {end_date}, category: {category}")

# Render selected page
if page == "Natural Language":
    run_nl_query(conn)

elif page == "Categories":
    st.subheader(f"📂 Top Categories for {user}")
    results, label = category_summary.run(conn, days, user_filter)
    st.subheader(f"📂 {label}")
    st.table(results)

elif page == "Vendors":
    st.subheader(f"🧾 Top Vendors for {user}")
    results = top_vendors.run(conn, days, user_filter)
    st.table(results)

elif page == "Subscriptions":
    st.subheader(f"🔁 Recurring Charges for {user}")
    results = subscription_summary.run(conn, days, user_filter)
    st.table(results)

elif page == "🧠 Vendor Mapping":
    run_vendor_mapping_dashboard(conn)


