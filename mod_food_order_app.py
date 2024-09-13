import time
import threading
import sqlite3
import shutil
import logging
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
conn = sqlite3.connect('orders.db')
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
        print(f"\nDispatching orders for {food_item}:")
        for order in order_queue[food_item]:
            print(f" - Deliver to Table {order['table']} (ordered at {time.ctime(order['timestamp'])})")
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
            print(f"New order received for {food_item}. Dispatching in 5 minutes.")
            threading.Timer(5 * 60, dispatch_orders, [food_item]).start()  # 5 minutes delay
        else:
            print(f"Another order for {food_item} added to the batch.")
        logging.info(f"Order queued for {food_item} at table {table}")
    except sqlite3.Error as e:
        logging.error(f"Database error during order queuing: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during order queuing: {e}")

# Function to backup the database
def backup_database():
    try:
        timestamp = time.strftime("%Y%m%d%H%M%S")
        backup_file = f"orders_backup_{timestamp}.db"
        shutil.copy('orders.db', backup_file)
        print(f"Backup created: {backup_file}")
        logging.info(f"Database backup created: {backup_file}")
    except Exception as e:
        logging.error(f"Error during backup: {e}")

# Function to display the menu
def display_menu():
    print("\n--- Menu ---")
    for item, price in menu.items():
        print(f"{item}: ${price}")

# Function to take an order from the customer
def take_order():
    display_menu()
    food_item = input("Select a food item from the menu: ").strip()
    if food_item not in menu:
        print("Invalid item. Please choose from the menu.")
        logging.warning(f"Invalid food item selected: {food_item}")
        return
    table = input("Enter Table number: ").strip()
    if not table:
        print("Table number cannot be empty.")
        logging.warning("Empty table number provided")
        return
    queue_order(food_item, table)
    print(f"Order for {food_item} at table {table} has been placed.")

# Admin panel for managing orders and viewing history
def view_order_history():
    try:
        print("\n--- Order History ---")
        cursor.execute("SELECT * FROM orders ORDER BY timestamp")
        orders = cursor.fetchall()
        if orders:
            for order in orders:
                status = "Pending" if order[4] == 'pending' else "Dispatched"
                print(f"Order ID: {order[0]}, Food: {order[1]}, Table: {order[2]}, Time: {time.ctime(order[3])}, Status: {status}")
        else:
            print("No orders found.")
    except sqlite3.Error as e:
        logging.error(f"Database error during viewing order history: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during viewing order history: {e}")

def generate_summary_report():
    try:
        print("\n--- Order Summary Report ---")
        cursor.execute("SELECT food_item, COUNT(*), SUM(CASE WHEN status='dispatched' THEN 1 ELSE 0 END) as dispatched_count FROM orders GROUP BY food_item")
        report = cursor.fetchall()
        if report:
            for row in report:
                print(f"Food Item: {row[0]}, Total Orders: {row[1]}, Dispatched: {row[2]}")
        else:
            print("No orders available to summarize.")
    except sqlite3.Error as e:
        logging.error(f"Database error during generating summary report: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during generating summary report: {e}")

def admin_menu():
    while True:
        print("\n--- Admin Panel ---")
        print("1. View Order History")
        print("2. Generate Summary Report")
        print("3. Exit Admin Panel")
        choice = input("Select an option: ")
        
        if choice == '1':
            view_order_history()
        elif choice == '2':
            generate_summary_report()
        elif choice == '3':
            print("Exiting Admin Panel.")
            break
        else:
            print("Invalid option. Try again.")

# Main loop to simulate the restaurant app
def main():
    while True:
        print("\n--- DishDispatch App ---")
        print("1. Take an Order")
        print("2. Admin Panel")
        print("3. Backup Database")
        print("4. Exit App")
        choice = input("Select an option: ")
        
        if choice == '1':
            take_order()
        elif choice == '2':
            admin_menu()
        elif choice == '3':
            backup_database()
        elif choice == '4':
            print("Exiting DishDispatch App.")
            conn.close()  # Close the database connection on exit
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()