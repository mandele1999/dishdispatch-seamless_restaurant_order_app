# DishDispatch: Seamless Restaurant Order App

DishDispatch is a Python-based restaurant order management app designed to streamline the process of grouping and dispatching food orders. Orders placed within a 5-minute window are combined for simultaneous delivery, ensuring efficient table service.

## Features

- **Real-Time Order Queuing**: Orders are dynamically grouped if placed within the same 5-minute window.
- **Table-Specific Dispatching**: Orders are routed to the correct table, ensuring prompt delivery.
- **Timed Delivery**: Orders are dispatched exactly 5 minutes after the first similar order is placed.
- **Efficient Grouping**: Similar orders for the same table or different tables are dispatched together for operational efficiency.

## How It Works

1. Customers place an order by specifying the food item and their table number.
2. Similar orders made within a 5-minute window are grouped.
3. All grouped orders are dispatched at the end of the countdown to the respective tables.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mandele1999/dishdispatch.git
