import streamlit as st
import pandas as pd

def run_vendor_mapping_dashboard(conn):
    st.title("🧠 Vendor Categorization Dashboard")
    st.markdown("Review unmatched vendor names and assign them to known vendors and categories.")

    # Load unmatched vendors
    unmatched = pd.read_sql("""
        SELECT vendor FROM unmatched_vendors
        WHERE reviewed = FALSE
        ORDER BY first_seen
        LIMIT 50;
    """, conn)

    if unmatched.empty:
        st.success("🎉 All unmatched vendors have been reviewed!")
        return

    # Load known vendors and categories once
    known_vendors = pd.read_sql("SELECT vendor FROM vendors ORDER BY vendor", conn)['vendor'].tolist()
    known_categories = pd.read_sql("SELECT category_name FROM categories ORDER BY category_name", conn)['category_name'].tolist()

    for i, row in unmatched.iterrows():
        raw_vendor = row["vendor"]
        st.markdown(f"---\n#### 🏷️ Raw Vendor: `{raw_vendor}`")

        col1, col2 = st.columns(2)

        with col1:
            vendor_choice = st.selectbox(
                "🔍 Pick known vendor (optional)", 
                options=[""] + known_vendors,
                index=0,
                key=f"vendor_select_{i}"
            )
            vendor_input = st.text_input(
                "🆕 Or enter new vendor", 
                value="", 
                key=f"vendor_input_{i}"
            )
            selected_vendor = vendor_input.strip() or vendor_choice.strip()

        with col2:
            category_choice = st.selectbox(
                "🔍 Pick known category (optional)", 
                options=[""] + known_categories,
                index=0,
                key=f"category_select_{i}"
            )
            category_input = st.text_input(
                "🏷️ Or enter new category", 
                value="", 
                key=f"category_input_{i}"
            )
            selected_category = category_input.strip() or category_choice.strip()

        if selected_vendor and selected_category:
            save_btn = st.button("💾 Save Mapping", key=f"save_btn_{i}")
            if save_btn:
                with conn.cursor() as cur:
                    # Insert vendor if new
                    cur.execute("""
                        INSERT IGNORE INTO vendors (vendor)
                        VALUES (%s);
                    """, (selected_vendor,))

                    # Insert category if new
                    cur.execute("""
                        INSERT IGNORE INTO categories (category_name)
                        VALUES (%s);
                    """, (selected_category,))

                    # Insert vendor_match
                    cur.execute("""
                        INSERT IGNORE INTO vendor_match (vendor_id, vendor)
                        SELECT vendor_id, %s
                        FROM vendors
                        WHERE vendor = %s;
                    """, (raw_vendor, selected_vendor))

                    # Link vendor to category
                    cur.execute("""
                        INSERT IGNORE INTO vendors_categories (vendor_id, category_id)
                        SELECT v.vendor_id, c.category_id
                        FROM vendors v, categories c
                        WHERE v.vendor = %s AND c.category_name = %s;
                    """, (selected_vendor, selected_category))

                    # Mark as reviewed
                    cur.execute("""
                        UPDATE unmatched_vendors 
                        SET reviewed = TRUE 
                        WHERE vendor = %s;
                    """, (raw_vendor,))

                    # Update money_spent.cat where applicable
                    cur.execute("""
                        UPDATE money_spent ms
                        JOIN vendor_match vm ON ms.vendor LIKE CONCAT(vm.vendor, '%')
                        JOIN vendors_categories vc ON vm.vendor_id = vc.vendor_id
                        JOIN categories c ON vc.category_id = c.category_id
                        SET ms.cat = c.category_name
                        WHERE ms.vendor = %s
                          AND (ms.cat IS NULL OR ms.cat = '');
                    """, (raw_vendor,))

                conn.commit()
                st.success(f"✅ `{raw_vendor}` → `{selected_vendor}` → `{selected_category}` saved and applied.")
        else:
            st.info("ℹ️ Please select or enter both a vendor and a category to continue.")

