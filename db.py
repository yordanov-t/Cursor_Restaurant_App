import sqlite3
import os
import shutil
from datetime import datetime, timedelta


class DBManager:
    """
    Thread-safe database manager using per-call connections.
    
    Each method opens its own connection to avoid SQLite threading issues
    with Flet's multi-threaded event handlers.
    """
    
    def __init__(self, db_name='restaurant.db'):
        self.db_name = db_name
        # Initialize database schema (uses its own connection)
        self.initialize_db()
    
    def _get_connection(self):
        """
        Create a new database connection with proper settings.
        
        Returns a connection configured with:
        - row_factory = sqlite3.Row for dict-like access
        - Foreign keys enabled
        """
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def initialize_db(self):
        """Create the tables if they do not exist yet."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Create waiters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS waiters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            # Create reservations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER NOT NULL,
                    time_slot TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone_number TEXT,
                    additional_info TEXT,
                    waiter_id INTEGER,
                    status TEXT NOT NULL,
                    FOREIGN KEY(waiter_id) REFERENCES waiters(id)
                )
            ''')
            # Create orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER NOT NULL,
                    order_details TEXT NOT NULL,
                    waiter_id INTEGER,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(waiter_id) REFERENCES waiters(id)
                )
            ''')
            # Create shifts table for waiter check-ins
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    waiter_id INTEGER,
                    shift_date TEXT NOT NULL,
                    FOREIGN KEY(waiter_id) REFERENCES waiters(id)
                )
            ''')
            # Create sections table for table grouping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    display_order INTEGER DEFAULT 0
                )
            ''')
            # Create section_tables junction table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS section_tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_id INTEGER NOT NULL,
                    table_number INTEGER NOT NULL,
                    FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE,
                    UNIQUE(table_number)
                )
            ''')
            # Create tables metadata table for shapes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tables_metadata (
                    table_number INTEGER PRIMARY KEY,
                    shape TEXT NOT NULL DEFAULT 'RECTANGLE'
                )
            ''')
            conn.commit()
            
            # Initialize default sections if none exist
            self._initialize_default_sections(conn)
            # Initialize default tables if none exist
            self._initialize_default_tables(conn)
        finally:
            conn.close()
    
    # -------------------------
    # Waiter management methods
    # -------------------------
    def add_waiter(self, name):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO waiters (name) VALUES (?)", (name,))
            conn.commit()
        finally:
            conn.close()
    
    def remove_waiter(self, waiter_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM waiters WHERE id = ?", (waiter_id,))
            conn.commit()
        finally:
            conn.close()
    
    def update_waiter(self, waiter_id, new_name):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE waiters SET name = ? WHERE id = ?", (new_name, waiter_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_waiters(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM waiters")
            return cursor.fetchall()
        finally:
            conn.close()
    
    def check_in_waiter(self, waiter_id):
        """Record a check‐in entry for a waiter for the current shift."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            shift_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO shifts (waiter_id, shift_date) VALUES (?, ?)", (waiter_id, shift_date))
            conn.commit()
        finally:
            conn.close()
    
    def get_shifts(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shifts")
            return cursor.fetchall()
        finally:
            conn.close()
    
    # -------------------------
    # Reservation management
    # -------------------------
    def create_reservation(self, table_number, time_slot, customer_name, phone_number, additional_info, waiter_id):
        """
        time_slot is a string in format "YYYY-MM-DD HH:MM".
        We block 1 hour and 30 minutes from the start time.
        """
        # Parse the new reservation start time
        try:
            new_start = datetime.strptime(time_slot, "%Y-%m-%d %H:%M")
        except ValueError:
            # If the time format is invalid, handle the error
            return False

        new_end = new_start + timedelta(hours=1, minutes=30)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Fetch existing "Reserved" reservations for this table
            cursor.execute(
                "SELECT time_slot FROM reservations WHERE table_number = ? AND status = 'Reserved'",
                (table_number,)
            )
            existing_reservations = cursor.fetchall()

            # Check for overlap with each existing reservation
            for row in existing_reservations:
                existing_slot = row["time_slot"]
                try:
                    existing_start = datetime.strptime(existing_slot, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue  # skip malformed data, or handle as needed

                existing_end = existing_start + timedelta(hours=1, minutes=30)

                # Overlap condition:
                # Two intervals [new_start, new_end) and [existing_start, existing_end)
                # overlap if new_start < existing_end and existing_start < new_end
                if (new_start < existing_end) and (existing_start < new_end):
                    # Found an overlap -> double booking
                    return False

            # If we reach here, no overlap found. Proceed to insert the reservation.
            cursor.execute(
                """INSERT INTO reservations 
                (table_number, time_slot, customer_name, phone_number, additional_info, waiter_id, status) 
                VALUES (?, ?, ?, ?, ?, ?, 'Reserved')""",
                (table_number, time_slot, customer_name, phone_number, additional_info, waiter_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()
    
    def update_reservation(self, reservation_id, table_number, time_slot, customer_name,
                           phone_number, additional_info, waiter_id, status):
        """
        Update an existing reservation.
        1. If the time_slot changed, enforce no double booking within 1h30 of the new time.
        2. Update phone_number and additional_info as well.
        """
        # 1) Parse the new time_slot if user changed it
        try:
            new_start = datetime.strptime(time_slot, "%Y-%m-%d %H:%M")
            new_end = new_start + timedelta(hours=1, minutes=30)
        except ValueError:
            # If invalid date/time format, handle as needed
            return False

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 2) Check for overlap with other reservations (if still 'Reserved')
            if status == "Reserved":
                cursor.execute("""
                    SELECT id, time_slot
                    FROM reservations
                    WHERE table_number = ?
                    AND status = 'Reserved'
                    AND id != ?
                """, (table_number, reservation_id))
                existing = cursor.fetchall()

                for row in existing:
                    try:
                        existing_start = datetime.strptime(row["time_slot"], "%Y-%m-%d %H:%M")
                    except ValueError:
                        continue
                    existing_end = existing_start + timedelta(hours=1, minutes=30)

                    # Overlap check: [new_start, new_end) vs [existing_start, existing_end)
                    if (new_start < existing_end) and (existing_start < new_end):
                        # Found overlap => double booking
                        return False

            # 3) Proceed with the update
            cursor.execute('''
                UPDATE reservations
                SET table_number = ?,
                    time_slot = ?,
                    customer_name = ?,
                    phone_number = ?,
                    additional_info = ?,
                    waiter_id = ?,
                    status = ?
                WHERE id = ?
            ''', (table_number, time_slot, customer_name, phone_number, additional_info,
                  waiter_id, status, reservation_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def delete_reservation(self, reservation_id):
        """
        Instead of deleting, we mark the reservation as Cancelled.
        This helps in preserving the history.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (reservation_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_reservations(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservations")
            return cursor.fetchall()
        finally:
            conn.close()
    
    # -------------------------
    # Order management
    # -------------------------
    def create_order(self, table_number, order_details, waiter_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO orders (table_number, order_details, waiter_id, timestamp) VALUES (?, ?, ?, ?)",
                (table_number, order_details, waiter_id, timestamp)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_orders(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            return cursor.fetchall()
        finally:
            conn.close()
    
    # -------------------------
    # Reports & Analytics
    # -------------------------
    def generate_report(self, period='daily'):
        """
        Generate a simple report based on the reservation time slots.
        period: 'daily', 'weekly', or 'monthly'
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if period == 'daily':
                cursor.execute("SELECT * FROM reservations WHERE date(time_slot)=date('now')")
            elif period == 'weekly':
                cursor.execute("SELECT * FROM reservations WHERE strftime('%W', time_slot)=strftime('%W','now')")
            elif period == 'monthly':
                cursor.execute("SELECT * FROM reservations WHERE strftime('%m', time_slot)=strftime('%m','now')")
            else:
                return []
            return cursor.fetchall()
        finally:
            conn.close()
    
    # -------------------------
    # Backup & Restore
    # -------------------------
    def backup_database(self, backup_file='backup.db'):
        """Back up the database to a file using file copy (thread-safe)."""
        # Use shutil for file-based copy (no connection needed)
        shutil.copy2(self.db_name, backup_file)
        return backup_file
    
    def restore_database(self, backup_file='backup.db'):
        """Restore the database from a backup file."""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Simply copy the backup file over the current database
        shutil.copy2(backup_file, self.db_name)
        
        # Reinitialize to ensure schema is up to date
        self.initialize_db()
    
    def close(self):
        """No-op for compatibility - connections are closed after each operation."""
        pass
    
    # -------------------------
    # Section management
    # -------------------------
    def _initialize_default_sections(self, conn):
        """Initialize default sections if none exist."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sections")
        count = cursor.fetchone()[0]
        if count == 0:
            # Create default sections
            default_sections = [
                ("Основна зала", 1, list(range(1, 21))),      # Tables 1-20
                ("Затворена градина", 2, list(range(21, 36))), # Tables 21-35
                ("Градина", 3, list(range(36, 51))),          # Tables 36-50
            ]
            for name, order, tables in default_sections:
                cursor.execute(
                    "INSERT INTO sections (name, display_order) VALUES (?, ?)",
                    (name, order)
                )
                section_id = cursor.lastrowid
                for table_num in tables:
                    cursor.execute(
                        "INSERT INTO section_tables (section_id, table_number) VALUES (?, ?)",
                        (section_id, table_num)
                    )
            conn.commit()
    
    def get_sections(self):
        """Get all sections ordered by display_order."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sections ORDER BY display_order")
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_section_by_id(self, section_id):
        """Get a section by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def get_section_tables(self, section_id):
        """Get all table numbers assigned to a section."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT table_number FROM section_tables WHERE section_id = ? ORDER BY table_number",
                (section_id,)
            )
            return [row["table_number"] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_section_tables(self):
        """Get all sections with their table assignments."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.name, s.display_order, 
                       GROUP_CONCAT(st.table_number) as tables
                FROM sections s
                LEFT JOIN section_tables st ON s.id = st.section_id
                GROUP BY s.id
                ORDER BY s.display_order
            """)
            result = []
            for row in cursor.fetchall():
                tables = []
                if row["tables"]:
                    tables = [int(t) for t in row["tables"].split(",")]
                result.append({
                    "id": row["id"],
                    "name": row["name"],
                    "display_order": row["display_order"],
                    "tables": sorted(tables)
                })
            return result
        finally:
            conn.close()
    
    def create_section(self, name, display_order=None):
        """Create a new section."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if display_order is None:
                cursor.execute("SELECT COALESCE(MAX(display_order), 0) + 1 FROM sections")
                display_order = cursor.fetchone()[0]
            try:
                cursor.execute(
                    "INSERT INTO sections (name, display_order) VALUES (?, ?)",
                    (name, display_order)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None  # Duplicate name
        finally:
            conn.close()
    
    def update_section(self, section_id, name):
        """Update a section's name."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE sections SET name = ? WHERE id = ?",
                    (name, section_id)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Duplicate name
        finally:
            conn.close()
    
    def delete_section(self, section_id):
        """Delete a section and its table assignments."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM section_tables WHERE section_id = ?", (section_id,))
            cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
            conn.commit()
        finally:
            conn.close()
    
    def assign_tables_to_section(self, section_id, table_numbers):
        """
        Assign tables to a section (replaces existing assignments).
        Tables are removed from other sections before assignment.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Remove tables from all sections first
            for table_num in table_numbers:
                cursor.execute("DELETE FROM section_tables WHERE table_number = ?", (table_num,))
            # Remove existing tables from this section
            cursor.execute("DELETE FROM section_tables WHERE section_id = ?", (section_id,))
            # Add new table assignments
            for table_num in table_numbers:
                cursor.execute(
                    "INSERT INTO section_tables (section_id, table_number) VALUES (?, ?)",
                    (section_id, table_num)
                )
            conn.commit()
        finally:
            conn.close()
    
    # -------------------------
    # Tables metadata management
    # -------------------------
    def _initialize_default_tables(self, conn):
        """Initialize default tables (1-50) if none exist."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tables_metadata")
        count = cursor.fetchone()[0]
        if count == 0:
            # Create default 50 tables with RECTANGLE shape
            for table_num in range(1, 51):
                cursor.execute(
                    "INSERT INTO tables_metadata (table_number, shape) VALUES (?, ?)",
                    (table_num, "RECTANGLE")
                )
            conn.commit()
    
    def get_all_tables(self):
        """Get all tables with their metadata."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables_metadata ORDER BY table_number")
            return [{"table_number": row["table_number"], "shape": row["shape"]} for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_table(self, table_number):
        """Get a single table's metadata."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables_metadata WHERE table_number = ?", (table_number,))
            row = cursor.fetchone()
            if row:
                return {"table_number": row["table_number"], "shape": row["shape"]}
            return None
        finally:
            conn.close()
    
    def get_table_shape(self, table_number):
        """Get the shape of a table (returns 'RECTANGLE' as default if not found)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT shape FROM tables_metadata WHERE table_number = ?", (table_number,))
            row = cursor.fetchone()
            return row["shape"] if row else "RECTANGLE"
        finally:
            conn.close()
    
    def create_table(self, table_number, shape="RECTANGLE"):
        """Create a new table with the given shape."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO tables_metadata (table_number, shape) VALUES (?, ?)",
                    (table_number, shape)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Table already exists
        finally:
            conn.close()
    
    def update_table_shape(self, table_number, shape):
        """Update a table's shape."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tables_metadata SET shape = ? WHERE table_number = ?",
                (shape, table_number)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_table(self, table_number):
        """
        Delete a table. Returns False if table has active reservations.
        Also removes from section assignments.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Check for active reservations
            cursor.execute(
                "SELECT COUNT(*) FROM reservations WHERE table_number = ? AND status = 'Reserved'",
                (table_number,)
            )
            if cursor.fetchone()[0] > 0:
                return False  # Has active reservations
            
            # Remove from section assignments
            cursor.execute("DELETE FROM section_tables WHERE table_number = ?", (table_number,))
            # Delete the table
            cursor.execute("DELETE FROM tables_metadata WHERE table_number = ?", (table_number,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_available_table_numbers(self):
        """Get list of all existing table numbers."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT table_number FROM tables_metadata ORDER BY table_number")
            return [row["table_number"] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_next_available_table_number(self):
        """Get the next available table number."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(table_number) FROM tables_metadata")
            max_num = cursor.fetchone()[0]
            return (max_num or 0) + 1
        finally:
            conn.close()
