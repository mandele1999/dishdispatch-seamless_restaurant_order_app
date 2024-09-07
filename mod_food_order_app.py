import sqlite3
import threading
import time

# Create and initialize the database
def initialize_database():
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    
    # Create a table for menu items
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_item TEXT NOT NULL
                    )''')
    
    # Create a table for orders
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_item TEXT NOT NULL,
                        table_number INTEGER NOT NULL,
                        order_time REAL NOT NULL,
                        status TEXT NOT NULL
                    )''')
    
    conn.commit()
    conn.close()

# Function to add a menu item
def add_menu_item(food_item):
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO menu (food_item) VALUES (?)', (food_item,))
    conn.commit()
    conn.close()

# Function to place an order
def place_order(food_item, table_number):
    current_time = time.time()
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (food_item, table_number, order_time, status) VALUES (?, ?, ?, ?)', 
                   (food_item, table_number, current_time, 'pending'))
    conn.commit()
    conn.close()
    
    # Start a 15-second timer for the order if it's the first of its kind
    if not check_pending_orders(food_item):
        threading.Timer(15, dispatch_orders, [food_item]).start()

# Check if there are pending orders for a specific food item
def check_pending_orders(food_item):
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE food_item = ? AND status = ?', (food_item, 'pending'))
    result = cursor.fetchall()
    conn.close()
    return len(result) > 1

# Dispatch the orders
def dispatch_orders(food_item):
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    
    # Select all pending orders for the food item
    cursor.execute('SELECT * FROM orders WHERE food_item = ? AND status = ?', (food_item, 'pending'))
    orders = cursor.fetchall()
    
    if orders:
        print(f"Dispatching order for {food_item}:")
        for order in orders:
            order_id, _, table_number, order_time, _ = order
            print(f" - deliver to Table {table_number} (ordered at {time.ctime(order_time)})")
            # Mark the order as dispatched
            cursor.execute('UPDATE orders SET status = ? WHERE id = ?', ('dispatched', order_id))
    
    conn.commit()
    conn.close()

# Take an order from the customer
def take_order():
    food_item = input("Enter Food Item: ")
    table_number = input("Enter Table number: ")
    
    # Ensure food_item exists in menu before placing an order
    if validate_menu_item(food_item):
        place_order(food_item, table_number)
        print(f"Order for {food_item} at table {table_number} has been placed.")
    else:
        print(f"Invalid menu item: {food_item}. Please select an item from the menu.")

# Validate if the menu item exists
def validate_menu_item(food_item):
    conn = sqlite3.connect('dishdispatch.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu WHERE food_item = ?', (food_item,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Add some menu items
def setup_menu():
    add_menu_item("Pizza")
    add_menu_item("Burger")
    add_menu_item("Pasta")
    add_menu_item("Salad")
    add_menu_item("Soda")

# Main function to initialize and simulate orders
def main():
    # Initialize the database and setup the menu
    initialize_database()
    setup_menu()
    
    # Simulate taking orders
    while True:
        take_order()

if __name__ == "__main__":
    main()
