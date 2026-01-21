# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 14:51:24 2025

@author: Sonu chauhan
"""

import streamlit as st
import pandas as pd
import os

# ---------- FILE SETUP ----------
DATA_FILE = "inventory_data.csv"

# Load data if exists, else create new
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Item Name", "Category", "Quantity", "Price (₹)"])

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Inventory System", page_icon="📦", layout="centered")

st.title("📦 Simple Inventory Management System")
st.write("A user-friendly local inventory app built with Streamlit.")

# ---------- SIDEBAR MENU ----------
menu = ["🏠 Home", "➕ Add Item", "📋 View Inventory", "✏️ Update/Delete Item"]
choice = st.sidebar.radio("Navigation", menu)

# ---------- HOME PAGE ----------
if choice == "🏠 Home":
    st.subheader("Welcome to Your Inventory System")
    st.info("Use the sidebar to navigate between adding, viewing, or editing items.")
    st.metric("Total Items", len(df))
    if not df.empty:
        st.metric("Total Stock Quantity", int(df["Quantity"].sum()))
    else:
        st.warning("No items in inventory yet.")

# ---------- ADD ITEM ----------
elif choice == "➕ Add Item":
    st.subheader("Add New Inventory Item")

    name = st.text_input("Item Name")
    category = st.text_input("Category")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")

    if st.button("Save Item"):
        if name and category:
            new_data = pd.DataFrame([[name, category, quantity, price]], columns=df.columns)
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"✅ '{name}' added successfully!")
        else:
            st.error("Please enter both Item Name and Category.")

# ---------- VIEW INVENTORY ----------
elif choice == "📋 View Inventory":
    st.subheader("Current Inventory List")
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No items available in inventory.")

# ---------- UPDATE OR DELETE ----------
elif choice == "✏️ Update/Delete Item":
    st.subheader("Update or Delete Existing Item")

    if not df.empty:
        item_list = df["Item Name"].tolist()
        selected_item = st.selectbox("Select Item", item_list)

        item_data = df[df["Item Name"] == selected_item].iloc[0]
        new_qty = st.number_input("New Quantity", value=int(item_data["Quantity"]))
        new_price = st.number_input("New Price (₹)", value=float(item_data["Price (₹)"]))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Item"):
                df.loc[df["Item Name"] == selected_item, ["Quantity", "Price (₹)"]] = [new_qty, new_price]
                df.to_csv(DATA_FILE, index=False)
                st.success(f"✅ '{selected_item}' updated successfully!")

        with col2:
            if st.button("Delete Item"):
                df = df[df["Item Name"] != selected_item]
                df.to_csv(DATA_FILE, index=False)
                st.warning(f"🗑️ '{selected_item}' deleted.")
    else:
        st.info("No items to update or delete.")
