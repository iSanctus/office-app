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

    # Table for Customers (Extended with contact details)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        email TEXT,
        phone TEXT,
        tax_id TEXT,
        address TEXT,
        work_info TEXT,
        taxis_username TEXT,
        taxis_password TEXT,
        notes TEXT,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
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
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE SET NULL
    )""")

    # Table for Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        table_name TEXT NOT NULL,
        record_id INTEGER,
        description TEXT,
        old_value TEXT,
        new_value TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Table for Company Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        company_name TEXT,
        logo_path TEXT,
        signature_path TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        tax_id TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Add new columns to existing customers table if they don't exist
    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN tax_id TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN address TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN work_info TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN taxis_username TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN taxis_password TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN created_date TEXT DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass

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
        query += " WHERE t.status = ?"
        cursor.execute(query + " ORDER BY t.transaction_date DESC, t.id DESC", (filter_status,))
    else:
        cursor.execute(query + " ORDER BY t.transaction_date DESC, t.id DESC")
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

    # Get old values for audit log
    cursor.execute("SELECT status, notes FROM transactions WHERE id = ?", (transaction_id,))
    old_values = cursor.fetchone()

    cursor.execute("UPDATE transactions SET status = ?, notes = ? WHERE id = ?", (new_status, new_notes, transaction_id))
    conn.commit()

    # Log the change
    add_audit_log("UPDATE", "transactions", transaction_id,
                  f"Ενημέρωση συναλλαγής #{transaction_id}",
                  f"Κατάσταση: {old_values[0]}, Σχόλια: {old_values[1]}",
                  f"Κατάσταση: {new_status}, Σχόλια: {new_notes}")

    conn.close()

def delete_transaction(transaction_id):
    """ Deletes a transaction """
    conn = connect_db()
    cursor = conn.cursor()

    # Get transaction details for audit log
    cursor.execute("""
        SELECT c.name, s.name, t.cost_final, t.transaction_date
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        LEFT JOIN services s ON t.service_id = s.id
        WHERE t.id = ?
    """, (transaction_id,))
    details = cursor.fetchone()

    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()

    # Log the deletion
    if details:
        add_audit_log("DELETE", "transactions", transaction_id,
                      f"Διαγραφή συναλλαγής #{transaction_id}",
                      f"Πελάτης: {details[0]}, Υπηρεσία: {details[1]}, Ποσό: {details[2]}€, Ημ/νία: {details[3]}",
                      "")

    conn.close()

# --- Extended Customer Functions ---
def update_customer_details(customer_id, name, email, phone, tax_id, address, work_info, taxis_username, taxis_password, notes):
    """ Updates full customer details """
    conn = connect_db()
    cursor = conn.cursor()

    # Get old name for audit
    cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
    old_name = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE customers
        SET name = ?, email = ?, phone = ?, tax_id = ?, address = ?, work_info = ?, taxis_username = ?, taxis_password = ?, notes = ?
        WHERE id = ?
    """, (name, email, phone, tax_id, address, work_info, taxis_username, taxis_password, notes, customer_id))
    conn.commit()

    # Log the change
    add_audit_log("UPDATE", "customers", customer_id,
                  f"Ενημέρωση στοιχείων πελάτη: {name}",
                  f"Προηγούμενο όνομα: {old_name}",
                  f"Νέο όνομα: {name}")

    conn.close()

def get_customer_details(customer_id):
    """ Gets full customer details """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, tax_id, address, work_info, taxis_username, taxis_password, notes, created_date
        FROM customers WHERE id = ?
    """, (customer_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_customer_id_by_name(name):
    """ Gets customer ID by name """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customers WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def fuzzy_search_customers(search_term):
    """ Fuzzy search for customers - matches any part of the name """
    conn = connect_db()
    cursor = conn.cursor()

    # Split search term into parts for better matching
    search_parts = search_term.strip().split()

    if not search_parts:
        return []

    # Build query for fuzzy matching
    query = "SELECT id, name FROM customers WHERE "
    conditions = []
    params = []

    for part in search_parts:
        conditions.append("name LIKE ?")
        params.append(f"%{part}%")

    query += " AND ".join(conditions)
    query += " ORDER BY name LIMIT 20"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- Audit Log Functions ---
def add_audit_log(action_type, table_name, record_id, description, old_value="", new_value=""):
    """ Adds an entry to the audit log """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (action_type, table_name, record_id, description, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (action_type, table_name, record_id, description, old_value, new_value))
    conn.commit()
    conn.close()

def get_audit_logs(limit=100, filter_action=None, filter_table=None):
    """ Gets audit log entries with optional filters """
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT id, action_type, table_name, record_id, description, old_value, new_value, timestamp FROM audit_log WHERE 1=1"
    params = []

    if filter_action:
        query += " AND action_type = ?"
        params.append(filter_action)

    if filter_table:
        query += " AND table_name = ?"
        params.append(filter_table)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- Company Settings Functions ---
def get_company_settings():
    """ Gets company settings """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT company_name, logo_path, signature_path, address, phone, email, tax_id
        FROM company_settings WHERE id = 1
    """)
    result = cursor.fetchone()
    conn.close()
    return result

def update_company_settings(company_name, logo_path, signature_path, address, phone, email, tax_id):
    """ Updates or creates company settings """
    conn = connect_db()
    cursor = conn.cursor()

    # Check if settings exist
    cursor.execute("SELECT id FROM company_settings WHERE id = 1")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE company_settings
            SET company_name = ?, logo_path = ?, signature_path = ?, address = ?, phone = ?, email = ?, tax_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (company_name, logo_path, signature_path, address, phone, email, tax_id))
    else:
        cursor.execute("""
            INSERT INTO company_settings (id, company_name, logo_path, signature_path, address, phone, email, tax_id)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (company_name, logo_path, signature_path, address, phone, email, tax_id))

    conn.commit()

    # Log the change
    add_audit_log("UPDATE", "company_settings", 1,
                  "Ενημέρωση ρυθμίσεων εταιρείας", "",
                  f"Όνομα: {company_name}")

    conn.close()

# --- Advanced Search Functions ---
def advanced_search_transactions(customer_name=None, date_from=None, date_to=None,
                                 min_amount=None, max_amount=None, status=None):
    """ Advanced search for transactions with multiple filters """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT t.id, c.name, COALESCE(s.name, 'Διαγραμμένη Υπηρεσία'),
               t.notes, t.transaction_date, t.cost_final, t.status
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        LEFT JOIN services s ON t.service_id = s.id
        WHERE 1=1
    """
    params = []

    if customer_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{customer_name}%")

    if date_from:
        query += " AND t.transaction_date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND t.transaction_date <= ?"
        params.append(date_to)

    if min_amount is not None:
        query += " AND t.cost_final >= ?"
        params.append(min_amount)

    if max_amount is not None:
        query += " AND t.cost_final <= ?"
        params.append(max_amount)

    if status and status != "Όλα":
        query += " AND t.status = ?"
        params.append(status)

    query += " ORDER BY t.transaction_date DESC, t.id DESC"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results