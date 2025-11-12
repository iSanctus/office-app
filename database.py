# database.py (Complete Final Version)
import sqlite3
import os

# --- Configuration ---
# Change this to your network path when you are ready to deploy
# Example: SHARED_PATH = r"\\SERVER-PC\Shared\CRM_Data"
SHARED_PATH = r"\\MYCLOUDEX2ULTRA\documentszis\Τα έγγραφά μου\CRM"  # This means the current folder (for local testing)

DB_FILE = os.path.join(SHARED_PATH, "company_data.db")
ATTACHMENTS_DIR = os.path.join(SHARED_PATH, "attachments")

def connect_db():
    """ Connects to the database and creates the full structure if it doesn't exist """
    if not os.path.exists(ATTACHMENTS_DIR):
        os.makedirs(ATTACHMENTS_DIR)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;") # Important for deleting services correctly

    # Table for Customers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )""")

    # Table for Services
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )""")

    # Table for Transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        service_id INTEGER,
        notes TEXT,
        transaction_date TEXT NOT NULL,
        cost_pre_vat REAL,
        cost_final REAL,
        status TEXT NOT NULL,
        attachment_path TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE SET NULL
    )""")
    conn.commit()
    return conn

# --- Customer Functions ---
def add_customer(name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()

def get_customer_by_name(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customers WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def search_customers_by_prefix(prefix):
    """ For autocomplete search """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM customers WHERE name LIKE ? ORDER BY name LIMIT 10", (prefix + '%',))
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

# --- Service Functions ---
def add_service(name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO services (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()

def get_services():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM services ORDER BY name")
    services = cursor.fetchall()
    conn.close()
    return services

def delete_service(service_id):
    conn = connect_db()
    cursor = conn.cursor()
    # Using 'ON DELETE SET NULL' for service_id handles transactions of deleted services
    cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
    conn.commit()
    conn.close()

# --- Transaction Functions ---
def add_transaction(customer_id, service_id, notes, date, cost_pre, cost_final, status, attachment=""):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO transactions (customer_id, service_id, notes, transaction_date, cost_pre_vat, cost_final, status, attachment_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, service_id, notes, date, cost_pre, cost_final, status, attachment))
    conn.commit()
    conn.close()

def get_all_transactions(filter_status="Όλα"):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        t.id, 
        c.name, 
        COALESCE(s.name, 'Διαγραμμένη Υπηρεσία'), 
        t.notes,
        t.transaction_date, 
        t.cost_final, 
        t.status
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    LEFT JOIN services s ON t.service_id = s.id
    """
    if filter_status != "Όλα":
        query += f" WHERE t.status = '{filter_status}'"
    query += " ORDER BY t.transaction_date DESC, t.id DESC"
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records

def get_transaction_details(transaction_id):
    """ Gets full details for editing """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, notes, status FROM transactions WHERE id = ?", (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_transaction_attachment(transaction_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT attachment_path FROM transactions WHERE id = ?", (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_transactions_by_customer(customer_name):
    """ Includes transaction ID for editing """
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        t.id, 
        COALESCE(s.name, 'Διαγραμμένη Υπηρεσία'), 
        t.notes, 
        t.transaction_date, 
        t.cost_final, 
        t.status
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    LEFT JOIN services s ON t.service_id = s.id
    WHERE c.name = ? 
    ORDER BY t.transaction_date DESC
    """
    cursor.execute(query, (customer_name,))
    records = cursor.fetchall()
    conn.close()
    return records

def update_transaction(transaction_id, new_status, new_notes):
    """ Updates a transaction's status and notes """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status = ?, notes = ? WHERE id = ?", (new_status, new_notes, transaction_id))
    conn.commit()
    conn.close()