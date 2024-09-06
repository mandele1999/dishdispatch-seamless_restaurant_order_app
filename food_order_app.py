from collections import defaultdict
import threading
import time

order_queue = defaultdict(list)

def dispatch_orders(food_item):
    print(f"Dispatching order for {food_item}:")
    for order in order_queue[food_item]:
        print(f"  - Deliver to table {order['table']} (ordered at {order['timestamp']})")
    order_queue[food_item].clear()

def queue_order(food_item, table):
    current_time = time.time()
    order = {"table": table, "timestamp": current_time}
    order_queue[food_item].append(order)
    if len(order_queue[food_item]) == 1:
        threading.Timer(10, dispatch_orders, [food_item]).start()

def take_order():
    food_item = input("Enter food item: ")
    table = input("Enter table number: ")
    queue_order(food_item, table)
    print(f"Order for {food_item} at table {table} has been placed.")

if __name__ == "__main__":
    while True:
        take_order()
