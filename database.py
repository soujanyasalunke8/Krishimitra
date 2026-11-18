
import sqlite3

def create_database():
    conn = sqlite3.connect(
    "krishimitra.db",
    timeout=30
)
    cursor = conn.cursor()

    # Farmer table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        village TEXT,
        state TEXT,
        district TEXT,
        crop TEXT
    )
    """)

    # Buyer table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        buyer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT,
        phone TEXT,
        location TEXT
    )
    """)

    # Contract table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        buyer_id INTEGER,
        crop TEXT,
        quantity REAL,
        price REAL,
        delivery_date TEXT,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id),
        FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Krishimitra database created successfully!")

if __name__ == "__main__":
    create_database()

def register_buyer(buyer_name, mobile, email,
                   business_type, state, district, crop):

    conn = sqlite3.connect("krishimitra.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT,
            business_type TEXT,
            state TEXT,
            district TEXT,
            crop TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO buyers
        (buyer_name, mobile, email, business_type,
         state, district, crop)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (buyer_name, mobile, email, business_type,
          state, district, crop))

    conn.commit()
    conn.close()
def update_buyer_table():
    conn = sqlite3.connect("krishimitra.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(buyers)")
    columns = [column[1] for column in cursor.fetchall()]

    required_columns = {
        "buyer_name": "TEXT",
        "mobile": "TEXT",
        "email": "TEXT",
        "business_type": "TEXT",
        "state": "TEXT",
        "district": "TEXT",
        "crop": "TEXT"
    }

    for column, datatype in required_columns.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE buyers ADD COLUMN {column} {datatype}"
            )

    conn.commit()
    conn.close()

    print("Buyer table updated successfully!")