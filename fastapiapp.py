from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import time
import threading
from collections import defaultdict

app = FastAPI()

# In-memory order queue and menu
order_queue = defaultdict(list)
menu = {
    'Burger': 5.00,
    'Pizza': 8.00,
    'Pasta': 6.50,
    'Salad': 4.50,
    'Soda': 1.50
}

# Database setup
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create table to store orders if not exists
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

class Order(BaseModel):
    food_item: str
    table_number: str

# Function to dispatch orders after 5 minutes
def dispatch_orders(food_item):
    print(f"\nDispatching orders for {food_item}:")
    for order in order_queue[food_item]:
        print(f" - Deliver to Table {order['table']} (ordered at {time.ctime(order['timestamp'])})")
        cursor.execute("UPDATE orders SET status = 'dispatched' WHERE timestamp = ?", (order['timestamp'],))
    order_queue[food_item].clear()
    conn.commit()

# Endpoint to place an order
@app.post("/order/")
def place_order(order: Order):
    if order.food_item not in menu:
        raise HTTPException(status_code=400, detail="Invalid food item")
    
    current_time = time.time()
    order_data = {"table": order.table_number, "timestamp": current_time}
    order_queue[order.food_item].append(order_data)
    cursor.execute("INSERT INTO orders (food_item, table_number, timestamp, status) VALUES (?, ?, ?, 'pending')", 
                   (order.food_item, order.table_number, current_time))
    conn.commit()
    
    if len(order_queue[order.food_item]) == 1:
        print(f"New order received for {order.food_item}. Dispatching in 5 minutes.")
        threading.Timer(5 * 60, dispatch_orders, [order.food_item]).start()  # 5 minutes delay
    else:
        print(f"Another order for {order.food_item} added to the batch.")
    
    return {"status": "Order placed"}

# Endpoint to view order history
@app.get("/orders/")
def view_order_history():
    cursor.execute("SELECT * FROM orders ORDER BY timestamp")
    orders = cursor.fetchall()
    result = []
    for order in orders:
        status = "Pending" if order[4] == 'pending' else "Dispatched"
        result.append({
            "id": order[0],
            "food_item": order[1],
            "table_number": order[2],
            "timestamp": time.ctime(order[3]),
            "status": status
        })
    return result

# Endpoint to generate summary report
@app.get("/summary/")
def generate_summary_report():
    cursor.execute("SELECT food_item, COUNT(*), SUM(CASE WHEN status='dispatched' THEN 1 ELSE 0 END) as dispatched_count FROM orders GROUP BY food_item")
    report = cursor.fetchall()
    result = []
    for row in report:
        result.append({
            "food_item": row[0],
            "total_orders": row[1],
            "dispatched": row[2]
        })
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
