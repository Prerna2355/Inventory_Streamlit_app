import streamlit as st
import sqlite3
import pandas as pd
import os
from typing import List

# ---------- CONFIG ----------
DB_FILE = "inventory.db"
DATA_FILE = "inventory_data.csv"
PAGE_ICON = "📦"
PAGE_TITLE = "Inventory Update"
LOW_STOCK_THRESHOLD = 5

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)



def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Lead_inventory1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Category TEXT NOT NULL,
            Property_Type TEXT NOT NULL,
            Project_Name TEXT,
            Address TEXT NOT NULL,
            Area TEXT NOT NULL,
            phone_number INTEGER NOT NULL,
            Owner_name TEXT NOT NULL,
            price TEXT NOT NULL,
            Cheque TEXT,
            Size TEXT NOT NULL,
            Comments TEXT NOT NULL
            
        )
    """)
    conn.commit()
    conn.close()


init_db()

def fetch_inventory():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        "SELECT id, Category AS 'Category',Property_Type AS 'Property_Type', Project_Name AS 'Project_Name', Address AS 'Address', Area AS 'Area', phone_number AS 'phone_number', Owner_name AS 'Owner_Name',price AS 'price', Cheque As 'Cheque', Size AS 'Size',Comments AS 'Comments' FROM Lead_inventory1",
        conn
    )
    conn.close()
    return df

def insert_item(Category,Property_Type, Project_Name,address, Area, phone_number, Owner_name, price,Cheque,Size, comments):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Lead_inventory1 (Category, Property_Type, Project_Name,address, Area, phone_number, Owner_name, price,Cheque, Size, Comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)",
        (Category, Property_Type, Project_Name,address, Area, phone_number, Owner_name, price,Cheque,Size, comments)
    )
    conn.commit()
    conn.close()

def update_item(item_id, price, Comments):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Lead_inventory1 SET price = ? , Comments= ? WHERE id = ?",
        (price,Comments, item_id)
    )
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Lead_inventory1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# ---------------- SESSION STATE ----------------
if "df" not in st.session_state:
    st.session_state.df = fetch_inventory()

# ---------------- UI ----------------
st.title(PAGE_TITLE)
st.write("Lead Management System.")

# ---------------- METRICS ----------------
col1, = st.columns(1)

df = st.session_state.df

with col1:
    st.metric("Total Items", len(df))

#with col2:
    #st.metric("Total Quantity", int(df["Quantity"].sum()) if not df.empty else 0)

#with col3:
 #   total_value = (df["Quantity"] * df["Price (₹)"]).sum() if not df.empty else 0
  #  st.metric("Inventory Value (₹)", f"{total_value:,.2f}")

#with col4:
 #   low_stock = (df["Quantity"] <= LOW_STOCK_THRESHOLD).sum() if not df.empty else 0
  #  st.metric("Low Stock Items", int(low_stock))"""

st.divider()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Add Item", "View items", "Edit / Delete"]
)

# ---------------- HOME ----------------
if menu == "Home":
    st.subheader("Recent Items")
    if df.empty:
        st.info("No inventory yet.")
    else:
        st.dataframe(df.tail(10), use_container_width=True)

# ---------------- ADD ITEM ----------------
elif menu == "Add Item":
    st.subheader("➕ Add New Lead")

    #AREAS = [
        #"Sector 14",
        #"Sector 15",
        #"Sector 21",
        #"DLF Phase 1",
        #"DLF Phase 2"
    #]
    Categories = ["Residential Land/Plot", "Kothi/Villa", "Builder floor", "Appartement/Flats", "Old/New Floors", "1RK/Studio Apartements"]
    Property_Type= ["Rent", "Sale", "Resale"]

    with st.form("add_form"):
        st.markdown("### 📌 Property Details")
        #category = st.text_input("Category")
        category = st.selectbox(
       "Category",
       Categories)
        Property_Type = st.selectbox("Property_Type", Property_Type)
        Project_Name = st.text_input("Project_Name")
        size = st.text_input("Size")
        
        
        st.markdown("### 📍 Location")
        address = st.text_input("Address")
        area = st.text_input("Area")

        st.markdown("### 👤 Owner Details")
        name = st.text_input("Owner_Name/Reference Name")
        phone_number= st.text_input("Phone Number", max_chars=10)

        st.markdown("### 💰 Pricing")
        price = st.text_input("price")
        Cheque = st.text_input("Cheque")

        comments = st.text_area("Comments / Notes", height=80)

        submit = st.form_submit_button("💾 Save Lead")

    if submit:
        if not name.strip() or not category.strip():
            st.error("Owner_Name and Category are required.")
        elif not phone_number.isdigit() or len(phone_number) != 10:
            st.error("Phone number must be exactly 10 digits.")
        else:
            insert_item(
                category.strip(),
                Property_Type.strip(),
                Project_Name.strip(),
                address.strip(),
                area,
                phone_number,                        # TEXT, not int
                name.strip(),
                price,
                Cheque.strip(),
                size,
                comments.strip()
            )
            st.session_state.df = fetch_inventory()
            st.success("✅ Lead added successfully")

# ---------------- INVENTORY VIEW ----------------
elif menu == "View items":
    st.subheader("Inventory List")

    search = st.text_input("Search by Owner Name")

    category_filter = st.selectbox(
        "Filter by Category",
        ["All"] + sorted(df["Category"].unique().tolist()) if not df.empty else ["All"]
    )

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["Owner_Name"].str.contains(search, case=False)
        ]

    if category_filter != "All":
        filtered = filtered[filtered["Category"] == category_filter]

    st.dataframe(filtered, use_container_width=True)


# ---------------- EDIT / DELETE ----------------
elif menu == "Edit / Delete":
    st.subheader("Edit or Delete Lead")

    df = st.session_state.df  # latest data

    if df.empty:
        st.info("No leads available.")
    else:
        # ---------------- SEARCH / FILTER ----------------
        search_text = st.text_input("Search by Owner Name")
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(df["Category"].unique().tolist())
        )

        filtered_df = df.copy()
        if search_text:
            filtered_df = filtered_df[filtered_df["Owner_Name"].str.contains(search_text, case=False)]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df["Category"] == category_filter]

        if filtered_df.empty:
            st.warning("No leads match your search/filter.")
        else:
            # ---------------- SELECT LEAD ----------------
            selected = st.selectbox(
                "Select Lead",
                filtered_df.itertuples(),
                format_func=lambda x: f"{x.Owner_Name} ({x.Category} - {x.Area})"
            )

            # ---------------- CURRENT DETAILS ----------------
            st.markdown("### Current Details")
            st.write({
                "Category": selected.Category,
                "Address": selected.Address,
                "Area": selected.Area,
                "phone_number": selected.phone_number,
                "price": selected.price,
                "Size": selected.Size,
                "Comments": selected.Comments
            })

            # ---------------- EDIT ----------------
            st.markdown("### ✏️ Edit Details")
            col1, col2 = st.columns(2)

           

            with col1:
                new_price = st.text_input(
                    "price",
                    value=selected.price,
                )
                #new_size = st.number_input(
                    #"Size (sq ft)",
                    #min_value=0,
                    #value=int(selected.Size)
               # )
             
           # with col2: new_category = st.selectbox( "Category", Category, index=Category.index(selected.Category) if selected.Category in Category else 0 ) 
            new_comments = st.text_area( "Comments", value=selected.Comments )

            # ---------------- ACTION BUTTONS ----------------
            col1_btn, col2_btn = st.columns(2)

            with col1_btn:
                if st.button("💾 Update"):
                    # update_item should be updated to include all editable fields
                    update_item(
                        selected.id,
                        new_price,
                        new_comments
                    )
                    st.session_state.df = fetch_inventory()
                    st.success("✅ Lead updated successfully")
                    st.experimental_rerun()

            with col2_btn:
                if st.button("Delete"):
                    confirm = st.confirm(f"Are you sure you want to delete '{selected.Owner_Name}'?")
                    if confirm:
                        delete_item(selected.id)
                        st.session_state.df = fetch_inventory()
                        st.warning("❌ Lead deleted")
                        st.experimental_rerun()

                
    st.subheader("📤 Export Data")

#csv = df.to_csv(index=False).encode("utf-8")

#st.download_button(
 #   label="Download as CSV",
  #  data=csv,
   # file_name="inventory_data.csv",
    #mime="text/csv"
#)

import io

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Full_Data")
    
    if not df.empty:
       for area in df["Area"].dropna().unique():
           area_df = df[df["Area"] == area]

           # Excel sheet name safety
           safe_sheet_name = area.replace("/", "-")[:31]

           area_df.to_excel(
               writer,
               index=False,
               sheet_name=safe_sheet_name
           )

st.download_button(
    label="Download as Excel",
    data=excel_buffer.getvalue(),
    file_name="inventory_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
