import time
import sqlite3
import shutil
import logging
import streamlit as st
from collections import defaultdict

# Configure logging
logging.basicConfig(filename='dishdispatch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# A defaultdict to store current orders by food item before dispatch
order_queue = defaultdict(list)

# Menu for food items and prices
menu = {
    'Burger': 5.00,
    'Pizza': 8.00,
    'Pasta': 6.50,
    'Salad': 4.50,
    'Soda': 1.50
}

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

# Function to dispatch orders after the timer
def dispatch_orders(food_item):
    try:
        st.write(f"Dispatching orders for {food_item}:")
        for order in order_queue[food_item]:
            st.write(f" - Deliver to Table {order['table']} (ordered at {time.ctime(order['timestamp'])})")
            cursor.execute("UPDATE orders SET status = 'dispatched' WHERE timestamp = ?", (order['timestamp'],))
        order_queue[food_item].clear()
        conn.commit()
        logging.info(f"Dispatched orders for {food_item}")
    except sqlite3.Error as e:
        logging.error(f"Database error during dispatch: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during dispatch: {e}")

# Function to queue new orders and dispatch after a delay
def queue_order(food_item, table):
    try:
        current_time = time.time()
        order = {"table": table, "timestamp": current_time}
        order_queue[food_item].append(order)

        # Save to the database with pending status
        cursor.execute("INSERT INTO orders (food_item, table_number, timestamp, status) VALUES (?, ?, ?, 'pending')", 
                       (food_item, table, current_time))
        conn.commit()

        # Start a timer if it's the first order for that food item
        if len(order_queue[food_item]) == 1:
            st.write(f"New order received for {food_item}. Dispatching in 5 minutes.")
            # Using a shorter time (10 seconds) for demonstration
            time.sleep(10)
            dispatch_orders(food_item)
        else:
            st.write(f"Another order for {food_item} added to the batch.")
        logging.info(f"Order queued for {food_item} at table {table}")
    except sqlite3.Error as e:
        logging.error(f"Database error during order queuing: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during order queuing: {e}")

# Function to display the menu in Streamlit
def display_menu():
    st.write("\n--- Menu ---")
    for item, price in menu.items():
        st.write(f"{item}: ${price}")

# Function to backup the database
def backup_database():
    try:
        timestamp = time.strftime("%Y%m%d%H%M%S")
        backup_file = f"orders_backup_{timestamp}.db"
        shutil.copy('orders.db', backup_file)
        st.write(f"Backup created: {backup_file}")
        logging.info(f"Database backup created: {backup_file}")
    except Exception as e:
        logging.error(f"Error during backup: {e}")

# Function to view order history
def view_order_history():
    try:
        st.write("\n--- Order History ---")
        cursor.execute("SELECT * FROM orders ORDER BY timestamp")
        orders = cursor.fetchall()
        if orders:
            for order in orders:
                status = "Pending" if order[4] == 'pending' else "Dispatched"
                st.write(f"Order ID: {order[0]}, Food: {order[1]}, Table: {order[2]}, Time: {time.ctime(order[3])}, Status: {status}")
        else:
            st.write("No orders found.")
    except sqlite3.Error as e:
        logging.error(f"Database error during viewing order history: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during viewing order history: {e}")

# Function to generate summary report
def generate_summary_report():
    try:
        st.write("\n--- Order Summary Report ---")
        cursor.execute("SELECT food_item, COUNT(*), SUM(CASE WHEN status='dispatched' THEN 1 ELSE 0 END) as dispatched_count FROM orders GROUP BY food_item")
        report = cursor.fetchall()
        if report:
            for row in report:
                st.write(f"Food Item: {row[0]}, Total Orders: {row[1]}, Dispatched: {row[2]}")
        else:
            st.write("No orders available to summarize.")
    except sqlite3.Error as e:
        logging.error(f"Database error during generating summary report: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during generating summary report: {e}")

# Streamlit UI Components
def main():
    st.title("DishDispatch: Restaurant Order Management")

    choice = st.sidebar.selectbox("Menu", ["Take an Order", "Admin Panel", "Backup Database", "Exit"])

    if choice == "Take an Order":
        display_menu()
        food_item = st.selectbox("Select a food item", list(menu.keys()))
        table = st.text_input("Enter Table number")
        if st.button("Place Order"):
            if food_item and table:
                queue_order(food_item, table)
            else:
                st.write("Please provide both food item and table number.")
    
    elif choice == "Admin Panel":
        admin_choice = st.selectbox("Admin Options", ["View Order History", "Generate Summary Report"])
        if admin_choice == "View Order History":
            view_order_history()
        elif admin_choice == "Generate Summary Report":
            generate_summary_report()
    
    elif choice == "Backup Database":
        if st.button("Backup Now"):
            backup_database()

    elif choice == "Exit":
        st.write("Exiting the App")

if __name__ == "__main__":
    main()
