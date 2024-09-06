import time
import threading
from collections import defaultdict

# A pre-defined menu of food and beverages
menu = {
    1: {"name": "Pizza", "price": 10.99},
    2: {"name": "Burger", "price": 8.99},
    3: {"name": "Pasta", "price": 12.99},
    4: {"name": "Salad", "price": 6.99},
    5: {"name": "Soda", "price": 1.99},
    6: {"name": "Coffee", "price": 2.99},
}

# Dictionary to store orders by food item
order_queue = defaultdict(list)

# Function to dispatch orders after 15 seconds
def dispatch_orders(food_item):
    print(f"\nDispatching order for {food_item}:")
    for order in order_queue[food_item]:
        print(f" - Deliver to Table {order['table']} (ordered at {time.ctime(order['timestamp'])})")
    # Clear the orders for the food item after dispatch
    order_queue[food_item].clear()

# Function to queue order and set 15-second timer for dispatch
def queue_order(food_item, table):
    current_time = time.time()
    order = {"table": table, "timestamp": current_time}
    # Add the order to the queue for the specified food item
    order_queue[food_item].append(order)
    # If this is the first order for this item, start a 15-second timer to dispatch
    if len(order_queue[food_item]) == 1:
        print(f"\nNew order received for {food_item}. Starting a 15-second countdown.")
        threading.Timer(0.25 * 60, dispatch_orders, [food_item]).start()  # 15-second countdown
    else:
        print(f"Similar order for {food_item} added to existing batch.")

# Function to display the menu
def display_menu():
    print("\n--- Menu ---")
    for item_id, details in menu.items():
        print(f"{item_id}. {details['name']} - ${details['price']:.2f}")

# Function to take an order from the customer
def take_order():
    display_menu()
    try:
        item_number = int(input("\nEnter the number of the food item you want to order: "))
        if item_number not in menu:
            print("Invalid selection. Please choose a valid item from the menu.")
            return
        table = input("Enter Table number: ")
        food_item = menu[item_number]["name"]
        queue_order(food_item, table)
        print(f"Order for {food_item} at table {table} has been placed.")
    except ValueError:
        print("Please enter a valid number.")

# User-driven interaction for managing orders
def simulation():
    while True:
        print("\nChoose an action:")
        print("1. Place an Order")
        print("2. View Active Orders")
        print("3. Exit Simulation")

        choice = input("\nEnter choice (1-3): ")

        if choice == '1':
            take_order()
        elif choice == '2':
            view_active_orders()
        elif choice == '3':
            print("\nExiting simulation.")
            break
        else:
            print("\nInvalid choice. Please try again.")

# Function to view all active orders
def view_active_orders():
    if not order_queue:
        print("\nNo active orders.")
    else:
        for food_item, orders in order_queue.items():
            print(f"\n{food_item} Orders:")
            for order in orders:
                print(f" - Table {order['table']}, ordered at {time.ctime(order['timestamp'])}")

# Run the improved simulation
simulation()
