import sqlite3
from typing import List, Tuple

DB_PATH = "stocksathi.db"


def get_connection():
    """Returns a connection configured with WAL mode to avoid database locks in Streamlit."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    """Initializes tables with database-level constraints against negative stock."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                reorder_level INTEGER NOT NULL DEFAULT 5 CHECK(reorder_level >= 0)
            );
            """
        )
        conn.commit()


def add_product(name: str, quantity: int, reorder_level: int) -> Tuple[bool, str]:
    """Inserts a new product, ensuring no empty or duplicate names."""
    cleaned_name = name.strip()
    if not cleaned_name:
        return False, "Product name cannot be empty."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO products (name, quantity, reorder_level)
                VALUES (?, ?, ?);
                """,
                (cleaned_name, quantity, reorder_level),
            )
            conn.commit()
            return True, f"Product '{cleaned_name}' added successfully!"
    except sqlite3.IntegrityError:
        return False, f"A product named '{cleaned_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_products() -> List[Tuple]:
    """Retrieves all products ordered by name as tuples: (id, name, quantity, reorder_level)."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, quantity, reorder_level 
            FROM products 
            ORDER BY name ASC;
            """
        )
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]


def record_sale(product_id: int, quantity_sold: int) -> Tuple[bool, str]:
    """Atomically decrements stock. Prevents negative stock and race conditions."""
    if quantity_sold <= 0:
        return False, "Quantity sold must be greater than 0."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ? AND quantity >= ?;
                """,
                (quantity_sold, product_id, quantity_sold),
            )

            if cursor.rowcount == 0:
                cursor.execute("SELECT quantity FROM products WHERE id = ?;", (product_id,))
                row = cursor.fetchone()
                if row is None:
                    return False, "Product not found."
                return False, f"Insufficient stock. Only {row['quantity']} units left."

            cursor.execute("SELECT name, quantity FROM products WHERE id = ?;", (product_id,))
            row = cursor.fetchone()
            conn.commit()
            return True, f"Sale recorded! {row['name']} now has {row['quantity']} units left."
    except Exception as e:
        return False, f"Transaction error: {str(e)}"


def restock_product(product_id: int, quantity_added: int) -> Tuple[bool, str]:
    """Atomically increments stock for an existing product."""
    if quantity_added <= 0:
        return False, "Restock quantity must be greater than 0."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE products
                SET quantity = quantity + ?
                WHERE id = ?;
                """,
                (quantity_added, product_id),
            )

            if cursor.rowcount == 0:
                return False, "Product not found."

            cursor.execute("SELECT name, quantity FROM products WHERE id = ?;", (product_id,))
            row = cursor.fetchone()
            conn.commit()
            return True, f"Restocked {row['name']}! New total: {row['quantity']} units."
    except Exception as e:
        return False, f"Database error: {str(e)}"