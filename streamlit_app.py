import time
import sqlite3
import shutil
import json  # For serializing items
import logging
import streamlit as st
from collections import defaultdict

# Configure logging
logging.basicConfig(filename='dishdispatch.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# A defaultdict to store current orders by table
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

# Update table to store orders if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number TEXT,
    items TEXT,  -- New column for storing multiple items
    timestamp REAL,
    status TEXT
)
''')
conn.commit()

# Function to dispatch orders after the timer
def dispatch_orders(table):
    try:
        st.write(f"Dispatching orders for Table {table}:")
        for order in order_queue[table]:
            st.write(f" - Deliver to Table {table} (ordered at {time.ctime(order['timestamp'])})")

            # Retrieve the items from the order
            items = order['items']
            for item, quantity in items.items():
                st.write(f"   - {quantity} x {item}")
            
            # Update order status to dispatched in the database
            cursor.execute("UPDATE orders SET status = 'dispatched' WHERE timestamp = ?", (order['timestamp'],))
        order_queue[table].clear()
        conn.commit()
        logging.info(f"Dispatched orders for Table {table}")
    except sqlite3.Error as e:
        logging.error(f"Database error during dispatch: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during dispatch: {e}")

# Function to queue new orders and dispatch after a delay
def queue_order(items, table):
    try:
        current_time = time.time()
        
        # Serialize the items dictionary to store in the database
        items_json = json.dumps(items)
        
        # Save to the database with pending status
        cursor.execute("INSERT INTO orders (table_number, items, timestamp, status) VALUES (?, ?, ?, 'pending')", 
                       (table, items_json, current_time))
        conn.commit()

        # Add the order to the queue
        order_queue[table].append({"items": items, "timestamp": current_time})
        
        if len(order_queue[table]) == 1:
            st.write(f"New order received for Table {table}. Dispatching in 5 minutes.")
            time.sleep(10)  # Short delay for demonstration
            dispatch_orders(table)
        else:
            st.write(f"Another order for Table {table} added to the batch.")
        logging.info(f"Order queued for Table {table} with items: {items}")
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
                items = json.loads(order[2])  # Deserialize items from JSON
                status = "Pending" if order[4] == 'pending' else "Dispatched"
                st.write(f"Order ID: {order[0]}, Table: {order[1]}, Time: {time.ctime(order[3])}, Status: {status}")
                st.write("Items:")
                for item, quantity in items.items():
                    st.write(f"  - {quantity} x {item}")
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
        cursor.execute("SELECT items FROM orders")
        orders = cursor.fetchall()
        
        summary = defaultdict(int)
        
        for order in orders:
            items = json.loads(order[0])
            for item, quantity in items.items():
                summary[item] += quantity
        
        for item, total in summary.items():
            st.write(f"{item}: {total} total orders")
        
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
        take_order()
    
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

# Function to handle multiple item orders
def take_order():
    st.write("### Place an Order")
    
    table_number = st.text_input("Enter Table Number")
    
    st.write("Select Food Items:")
    selected_items = {}
    
    for item, price in menu.items():
        quantity = st.number_input(f"{item} (Quantity)", min_value=0, max_value=10, step=1)
        if quantity > 0:
            selected_items[item] = quantity
    
    if st.button("Place Order"):
        if table_number and selected_items:
            queue_order(selected_items, table_number)
        else:
            st.write("Please select at least one item and provide a table number.")

if __name__ == "__main__":
    main()

