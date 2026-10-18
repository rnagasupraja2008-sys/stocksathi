import csv
import io
import streamlit as st
from database import add_product, get_products, record_sale, restock_product

st.set_page_config(
    page_title="StockSathi",
    page_icon="📦",
    layout="wide",
)


def generate_inventory_csv(products_list):
    """Converts the product list into an in-memory CSV file without extra libraries."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Product Name", "Available Units", "Alert Threshold", "Stock Status"])
    for p in products_list:
        status = "Low Stock" if p[2] <= p[3] else "In Stock"
        writer.writerow([p[1], p[2], p[3], status])
    return output.getvalue().encode("utf-8")


st.title("📦 StockSathi")
st.caption("Simple inventory management for small shops.")

# Fetch inventory once per page run
products = get_products()

# Dashboard metrics
total_products = len(products)
total_units = sum(p[2] for p in products) if products else 0
low_stock_products = [p for p in products if p[2] <= p[3]]

col1, col2, col3 = st.columns(3)
col1.metric("Products", total_products)
col2.metric("Total Units", total_units)
col3.metric("Low-stock Items", len(low_stock_products))

# Immediate alert banner at top
if low_stock_products:
    for product in low_stock_products:
        st.warning(
            f"⚠️ **{product[1]}**: Only {product[2]} units left! (Alert level: {product[3]})"
        )

st.divider()

# Left Column: Add Product | Right Column: Sell & Restock Tabs
col_add, col_manage = st.columns(2)

with col_add:
    st.header("➕ Add a Product")
    with st.form("add_product_form", clear_on_submit=True):
        product_name = st.text_input("Product name", placeholder="e.g., Maggi Noodles 70g")

        c1, c2 = st.columns(2)
        with c1:
            quantity = st.number_input("Opening quantity", min_value=0, value=10, step=1)
        with c2:
            reorder_level = st.number_input("Alert level", min_value=0, value=5, step=1)

        submitted = st.form_submit_button("Add Product", width="stretch")
        if submitted:
            success, message = add_product(product_name, int(quantity), int(reorder_level))
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

with col_manage:
    st.header("⚡ Manage Stock")
    if products:
        product_options = {
            product[0]: f"{product[1]} — {product[2]} available"
            for product in products
        }

        tab_sale, tab_restock = st.tabs(["🛒 Record Sale", "📥 Restock"])

        with tab_sale:
            with st.form("sale_form"):
                sale_id = st.selectbox(
                    "Product sold",
                    options=list(product_options.keys()),
                    format_func=lambda pid: product_options[pid],
                    key="sale_select",
                )
                quantity_sold = st.number_input(
                    "Quantity sold",
                    min_value=1,
                    value=1,
                    step=1,
                    key="sale_qty",
                )
                sale_submitted = st.form_submit_button("Record Sale", width="stretch")
                if sale_submitted:
                    success, message = record_sale(sale_id, int(quantity_sold))
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        with tab_restock:
            with st.form("restock_form"):
                restock_id = st.selectbox(
                    "Product restocked",
                    options=list(product_options.keys()),
                    format_func=lambda pid: product_options[pid],
                    key="restock_select",
                )
                quantity_added = st.number_input(
                    "Units received",
                    min_value=1,
                    value=10,
                    step=1,
                    key="restock_qty",
                )
                restock_submitted = st.form_submit_button("Add to Stock", width="stretch")
                if restock_submitted:
                    success, message = restock_product(restock_id, int(quantity_added))
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    else:
        st.info("Add a product on the left to start managing stock.")

st.divider()

# Inventory table with CSV Export
st.header("📋 Current Inventory")

if products:
    col_table_label, col_export = st.columns([3, 1])

    with col_table_label:
        st.caption("Real-time view of your current product levels.")

    with col_export:
        csv_data = generate_inventory_csv(products)
        st.download_button(
            label="📥 Export Inventory CSV",
            data=csv_data,
            file_name="stocksathi_inventory.csv",
            mime="text/csv",
            width="stretch",
        )

    st.dataframe(
        [
            {
                "Product": product[1],
                "Quantity": product[2],
                "Alert Level": product[3],
                "Status": (
                    "⚠️ Low stock"
                    if product[2] <= product[3]
                    else "✅ In stock"
                ),
            }
            for product in products
        ],
        width="stretch",
        hide_index=True,
    )
else:
    st.write("Your inventory is empty.")

st.divider()

# Plans section
st.header("💰 StockSathi Plans")
free_col, pro_col = st.columns(2)

with free_col:
    st.subheader("🆓 Free")
    st.title("₹0")
    st.write("For small shops getting started.")
    st.write("✅ Add and manage products")
    st.write("✅ Record sales & restocks")
    st.write("✅ Low-stock alerts")
    st.caption("Available in the current MVP.")

with pro_col:
    st.subheader("⭐ StockSathi Pro")
    st.title("₹49/month")
    st.write("For shops that need more insights.")
    st.write("📊 Downloadable inventory reports (Unlocked in CSV!)")
    st.write("📈 Sales summaries & revenue tracking")
    st.write("🔔 WhatsApp stock notifications")
    st.caption("Pro features are planned, not yet implemented.")

    st.button("Pro — Coming Soon", disabled=True, width="stretch")

st.caption(
    "Pro pricing is a proposal to validate with shopkeepers. "
    "No payments are collected by this prototype."
)