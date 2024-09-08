import threading
import time
import sqlite3
from collections import defaultdict

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
    print(f"\nDispatching orders for {food_item}:")
    for order in order_queue[food_item]:
        print(f" - Deliver to Table {order['table']} (ordered at {time.ctime(order['timestamp'])})")
        cursor.execute("UPDATE orders SET status = 'dispatched' WHERE timestamp = ?", (order['timestamp'],))
    # Clear the order queue for that food item
    order_queue[food_item].clear()
    conn.commit()

# Function to queue new orders and dispatch after a delay
def queue_order(food_item, table):
    current_time = time.time()
    order = {"table": table, "timestamp": current_time}
    # Add the order to the queue for that food item
    order_queue[food_item].append(order)
    # Save to the database with pending status
    cursor.execute("INSERT INTO orders (food_item, table_number, timestamp, status) VALUES (?, ?, ?, 'pending')", 
                   (food_item, table, current_time))
    conn.commit()
    # Start a timer if it's the first order for that food item
    if len(order_queue[food_item]) == 1:
        print(f"New order received for {food_item}. Dispatching in 5 minutes.")
        threading.Timer(5 * 60, dispatch_orders, [food_item]).start()  # Change to 5 minutes (300 seconds)
    else:
        print(f"Another order for {food_item} added to the batch.")

# Function to take an order from the customer
def display_menu():
    print("\n--- Menu ---")
    for item, price in menu.items():
        print(f"{item}: ${price}")

def take_order():
    display_menu()
    food_item = input("Select a food item from the menu: ")
    if food_item not in menu:
        print("Invalid item. Please choose from the menu.")
        return
    table = input("Enter Table number: ")
    queue_order(food_item, table)
    print(f"Order for {food_item} at table {table} has been placed.")

# Admin panel for managing orders and viewing history
def view_order_history():
    print("\n--- Order History ---")
    cursor.execute("SELECT * FROM orders ORDER BY timestamp")
    orders = cursor.fetchall()
    if orders:
        for order in orders:
            status = "Pending" if order[4] == 'pending' else "Dispatched"
            print(f"Order ID: {order[0]}, Food: {order[1]}, Table: {order[2]}, Time: {time.ctime(order[3])}, Status: {status}")
    else:
        print("No orders found.")

def generate_summary_report():
    print("\n--- Order Summary Report ---")
    cursor.execute("SELECT food_item, COUNT(*), SUM(CASE WHEN status='dispatched' THEN 1 ELSE 0 END) as dispatched_count FROM orders GROUP BY food_item")
    report = cursor.fetchall()
    if report:
        for row in report:
            print(f"Food Item: {row[0]}, Total Orders: {row[1]}, Dispatched: {row[2]}")
    else:
        print("No orders available to summarize.")

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
        print("3. Exit App")
        choice = input("Select an option: ")
        
        if choice == '1':
            take_order()
        elif choice == '2':
            admin_menu()
        elif choice == '3':
            print("Exiting DishDispatch App.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

# Close the database connection on exit
conn.close()
