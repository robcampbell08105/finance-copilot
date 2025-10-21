import streamlit as st
from copilot import run_from_args  # reuse your existing insight engine
from insights import top_vendors, category_summary, subscription_summary
import db_connection

st.title("💸 Family Spending Insights")

# Select family member
user = st.selectbox("Select a user:", ["(All Users)", "Robert", "Julie", "Maija"])
user_filter = None if user == "(All Users)" else user
days = st.number_input(
    "Look back period (in days):", min_value=1, max_value=3650, value=30, step=1
)
insight = st.radio("Insight type:", ["Categories", "Vendors", "Subscriptions"])

# Connect to the database
conn = db_connection.connect_to_database("/home/rwcampbell/.my.cnf", section="clientfinance")

# Run selected insight
if insight == "Categories":
    st.subheader(f"📂 Top Categories for {user}")
    results = category_summary.run(conn, days, user_filter)
    st.table(results)  # ← Displays result as table
elif insight == "Vendors":
    st.subheader(f"🧾 Top Vendors for {user}")
    results = top_vendors.run(conn, days, user_filter)
    st.table(results)
elif insight == "Subscriptions":
    st.subheader(f"🔁 Recurring Charges for {user}")
    results = subscription_summary.run(conn, days, user_filter)
    st.table(results)

