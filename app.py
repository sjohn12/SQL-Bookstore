from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
app.secret_key = 'this_is_a_secret_key' 

def execute_sql_script(filename):
    with sqlite3.connect('book_store_database.db') as conn:
        with open(filename, 'r') as f:
            sql_script = f.read()
            conn.executescript(sql_script)

# Create the database and tables, and insert sample data
with app.app_context():
    execute_sql_script('term_proj.sql')  # Execute the SQL script

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    conn = sqlite3.connect('book_store_database.db')

    if request.method == 'POST':
        search_value = request.form.get('search')  # Get the search value from the form
        rating = request.form.get('min_rating')
        budget = request.form.get('max_budget')
        
        if search_value:  # Check if the search value is not empty
            # Query to select entries based on the search value
            books = conn.execute('SELECT * FROM BOOK_CATALOG WHERE book_code = ? OR book_title LIKE ?;', (search_value, f'%{search_value}%')).fetchall()
        elif rating and budget:
            books = conn.execute('SELECT * FROM BOOK_CATALOG WHERE rating >= ? AND price <= ?;', (rating, budget, )).fetchall()
        elif rating:
            books = conn.execute('SELECT * FROM BOOK_CATALOG WHERE rating >= ?;', (rating)).fetchall()
        elif budget:
            books = conn.execute('SELECT * FROM BOOK_CATALOG WHERE price <= ?;', (budget, )).fetchall()
        else:
            # If search_value is empty, fetch all books (enter space)
            books = conn.execute('SELECT * FROM BOOK_CATALOG;').fetchall()
    else:
        # If the request method is GET, fetch all books
        books = conn.execute('SELECT * FROM BOOK_CATALOG;').fetchall()


    conn.close()
    return render_template('catalog.html', books=books)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    conn = sqlite3.connect('book_store_database.db')
    
    if request.method == 'POST':
        book_title = request.form.get('title') 
        quantity = request.form.get('quantity')
        customer_id = request.form.get('customer')
        price = request.form.get('price')
        
        # Check if all required fields are provided
        if book_title and quantity and customer_id and price:
            # Check if the order already exists
            existing_order = conn.execute(
                'SELECT * FROM ORDERS WHERE book_title = ? AND customer_id = ? AND quantity = ?;',
                (book_title, customer_id, quantity)
            ).fetchone()
            
            if existing_order:
                message = 'This order already exists. Please check your entries.'
                return render_template('orders.html', orders=message)
            else:
                # Insert the new order
                conn.execute('INSERT INTO ORDERS (book_title, quantity, customer_id, price) VALUES (?, ?, ?, ?);', 
                             (book_title, quantity, customer_id, price))
                conn.commit()  # Commit the transaction

    # Fetch all orders to display
    orders = conn.execute('SELECT * FROM ORDERS;').fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/inventory',  methods=['GET', 'POST'])
def inventory():
    conn = sqlite3.connect('book_store_database.db')
    if request.method == 'POST':
        book_code = request.form.get('book_code') 
        quantity = request.form.get('quantity')
        

        if book_code and quantity:  # Check if the search value is not empty
            # Query to select entries based on the search value
            conn.execute('UPDATE INVENTORY SET item_count = ? WHERE book_code = ?;', (quantity, book_code)).fetchall()
            conn.commit()
    inventory_items = conn.execute('SELECT * FROM INVENTORY;').fetchall()
    conn.close()
    return render_template('inventory.html', inventory=inventory_items)

@app.route('/pending_customers',  methods=['GET', 'POST'])
def pending_customers():
    conn = sqlite3.connect('book_store_database.db')
    if request.method == 'POST':
        pending_order = request.form.get('pending_order_id') 
        

        if pending_order:  # Check if the search value is not empty
            # Query to select entries based on the search value
            customers = conn.execute('DELETE FROM PENDING_CUSTOMER WHERE pending_order_id = ?;', (pending_order)).fetchall()
    customers = conn.execute('SELECT * FROM PENDING_CUSTOMER;').fetchall()
    conn.close()
    return render_template('pending_customers.html', customers=customers)

if __name__ == '__main__':
    app.run(debug=True)
