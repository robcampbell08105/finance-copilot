from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import db_connection
from nl_query.parse_nl_input import parse_nl_input
from insights import category_summary

app = FastAPI()

# Allow mobile/WebView access (consider tightening in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def run_query(
    query: str = Form(...),
    user: str = Form(None)
):
    # Parse query
    insight, days, user_parsed, category, start_date, end_date, exclude_user = parse_nl_input(query, user)
    final_user = user_parsed or user

    # Connect to your database
    conn = db_connection.connect_to_database("/home/rwcampbell/.my.cnf", section="clientfinance")

    # Run financial insight logic
    results, label = category_summary.run(
        connection=conn,
        days=days,
        user=final_user,
        category=category,
        start_date=start_date,
        end_date=end_date
    )

    # Format result
    top = results[0] if results else None
    if top:
        cat, total, count = top
        summary = f"{final_user or 'Everyone'} spent ${total:.2f} on {cat} ({count} txns)"
    else:
        summary = f"No spending data found for {final_user or 'anyone'}."

    # Log for debugging
    print(f"📝 Raw query received: {query}")
    print(f"📅 Date range parsed: start={start_date}, end={end_date}")
    print(f"👤 User parsed: {final_user}, Category parsed: {category}")

    return {
        "query": query,
        "user": final_user,
        "category": category,
        "date_range": [start_date, end_date],
        "summary": summary,
        "raw": results,
        "raw_input_debug": {"query": query, "user": user}
    }

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="10.0.0.10", port=8502, reload=True, log_level="debug")

