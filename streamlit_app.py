import streamlit as st
import sqlite3
import time

# Database connection for storing orders
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create table to store orders if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_item TEXT,
    table_number TEXT,
    timestamp REAL,
    status TEXT
)
''')
conn.commit()

# Menu for food items and prices
menu = {
    'Burger': 5.00,
    'Pizza': 8.00,
    'Pasta': 6.50,
    'Salad': 4.50,
    'Soda': 1.50
}

# Streamlit app layout
st.title("Restaurant Order Management")

# Function to queue new orders
def queue_order(food_item, table):
    current_time = time.time()
    # Save to the database with pending status
    cursor.execute("INSERT INTO orders (food_item, table_number, timestamp, status) VALUES (?, ?, ?, 'pending')",
                   (food_item, table, current_time))
    conn.commit()
    st.success(f"Order for {food_item} at table {table} has been placed.")

# Function to view order history
def view_order_history():
    st.subheader("Order History")
    cursor.execute("SELECT * FROM orders ORDER BY timestamp")
    orders = cursor.fetchall()
    if orders:
        for order in orders:
            status = "Pending" if order[4] == 'pending' else "Dispatched"
            st.write(f"Order ID: {order[0]}, Food: {order[1]}, Table: {order[2]}, Time: {time.ctime(order[3])}, Status: {status}")
    else:
        st.write("No orders found.")

# Function to generate summary report
def generate_summary_report():
    st.subheader("Order Summary Report")
    cursor.execute("SELECT food_item, COUNT(*), SUM(CASE WHEN status='dispatched' THEN 1 ELSE 0 END) as dispatched_count FROM orders GROUP BY food_item")
    report = cursor.fetchall()
    if report:
        for row in report:
            st.write(f"Food Item: {row[0]}, Total Orders: {row[1]}, Dispatched: {row[2]}")
    else:
        st.write("No orders available to summarize.")

# Sidebar menu
option = st.sidebar.selectbox("Menu", ("Take an Order", "View Order History", "Generate Summary Report"))

# "Take an Order" section
if option == "Take an Order":
    st.subheader("Take an Order")
    food_item = st.selectbox("Select a food item from the menu:", list(menu.keys()))
    table = st.text_input("Enter Table number")
    if st.button("Place Order"):
        if table:
            queue_order(food_item, table)
        else:
            st.error("Please enter a valid table number.")

# "View Order History" section
elif option == "View Order History":
    view_order_history()

# "Generate Summary Report" section
elif option == "Generate Summary Report":
    generate_summary_report()
