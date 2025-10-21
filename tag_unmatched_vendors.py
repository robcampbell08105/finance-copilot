import db_connection
import logging
import os

logging.basicConfig(level=logging.INFO)

def fetch_unlinked_transactions(conn):
    query = """
        SELECT ms.event_id, ms.vendor
        FROM money_spent ms
        LEFT JOIN money_spent_vendors msv ON ms.event_id = msv.event_id
        WHERE msv.event_id IS NULL AND ms.vendor IS NOT NULL
    """
    return db_connection.execute_query(conn, query)

def fetch_vendor_aliases(conn):
    query = """
        SELECT vm.vendor_id, vm.vendor
        FROM vendor_match vm
    """
    return db_connection.execute_query(conn, query)

def insert_matches(conn, matches):
    if not matches:
        return
    cursor = conn.cursor()
    inserted = 0
    for event_id, vendor_id in matches:
        try:
            cursor.execute(
                "INSERT IGNORE INTO money_spent_vendors (event_id, vendor_id) VALUES (%s, %s)",
                (event_id, vendor_id)
            )
            inserted += 1
        except Exception as e:
            logging.warning(f"⚠️ Failed insert: {event_id} → {vendor_id}: {e}")
    conn.commit()
    cursor.close()
    logging.info(f"✅ Inserted {inserted} vendor links")

def run_partial_match(conn):
    unmatched = fetch_unlinked_transactions(conn)
    aliases = fetch_vendor_aliases(conn)  # [(vendor_id, vendor), ...]

    matches = []
    for event_id, raw_vendor in unmatched:
        vendor_norm = (raw_vendor or "").strip().lower()
        found = False
        for vendor_id, alias in aliases:
            alias_norm = (alias or "").strip().lower()
            if alias_norm in vendor_norm:
                matches.append((event_id, vendor_id))
                logging.info(f"🔗 Matched via partial: '{raw_vendor}' → '{alias}'")
                found = True
                break
        if not found:
            logging.info(f"❌ No match for: '{raw_vendor}'")

    insert_matches(conn, matches)

if __name__ == "__main__":
    conn = db_connection.connect_to_database(os.path.expanduser("~/.my.cnf"), section="clientfinance")
    run_partial_match(conn)
    conn.close()

