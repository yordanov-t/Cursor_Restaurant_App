import sqlite3
import os
from datetime import datetime, timedelta
class DBManager:
    def __init__(self, db_name='restaurant.db'):
        self.db_name = db_name
        # Open the connection and set row_factory for easy dict‐like access
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.initialize_db()
    def initialize_db(self):
        """Create the tables if they do not exist yet."""
        cursor = self.conn.cursor()
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
                additional_info TEXT,        -- NEW COLUMN
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
        self.conn.commit()
        # Initialize default sections if none exist
        self._initialize_default_sections()
    # -------------------------
    # Waiter management methods
    # -------------------------
    def add_waiter(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO waiters (name) VALUES (?)", (name,))
        self.conn.commit()
    def remove_waiter(self, waiter_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM waiters WHERE id = ?", (waiter_id,))
        self.conn.commit()
    def update_waiter(self, waiter_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE waiters SET name = ? WHERE id = ?", (new_name, waiter_id))
        self.conn.commit()
    def get_waiters(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM waiters")
        return cursor.fetchall()
    def check_in_waiter(self, waiter_id):
        """Record a check‐in entry for a waiter for the current shift."""
        cursor = self.conn.cursor()
        shift_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO shifts (waiter_id, shift_date) VALUES (?, ?)", (waiter_id, shift_date))
        self.conn.commit()
    def get_shifts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM shifts")
        return cursor.fetchall()
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

        cursor = self.conn.cursor()

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
        self.conn.commit()
        return True
    def update_reservation(self, reservation_id, table_number, time_slot, customer_name,
                        phone_number, additional_info, waiter_id, status):
        """
        Update an existing reservation.
        1. If the time_slot changed, enforce no double booking within 1h30 of the new time.
        2. Update phone_number and additional_info as well.
        """
        cursor = self.conn.cursor()

        # 1) Parse the new time_slot if user changed it
        try:
            new_start = datetime.strptime(time_slot, "%Y-%m-%d %H:%M")
            new_end = new_start + timedelta(hours=1, minutes=30)
        except ValueError:
            # If invalid date/time format, handle as needed
            return False

        # 2) Check for overlap with other reservations (if still 'Reserved')
        #    (Skip overlap check if status is 'Cancelled', or if you only want to block when status='Reserved')
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
        self.conn.commit()
        return True
    def delete_reservation(self, reservation_id):
        """
        Instead of deleting, we mark the reservation as Cancelled.
        This helps in preserving the history.
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (reservation_id,))
        self.conn.commit()
    def get_reservations(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reservations")
        return cursor.fetchall()
    # -------------------------
    # Order management
    # -------------------------
    def create_order(self, table_number, order_details, waiter_id):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO orders (table_number, order_details, waiter_id, timestamp) VALUES (?, ?, ?, ?)",
            (table_number, order_details, waiter_id, timestamp)
        )
        self.conn.commit()
    def get_orders(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders")
        return cursor.fetchall()
    # -------------------------
    # Reports & Analytics
    # -------------------------
    def generate_report(self, period='daily'):
        """
        Generate a simple report based on the reservation time slots.
        period: 'daily', 'weekly', or 'monthly'
        """
        cursor = self.conn.cursor()
        if period == 'daily':
            cursor.execute("SELECT * FROM reservations WHERE date(time_slot)=date('now')")
        elif period == 'weekly':
            cursor.execute("SELECT * FROM reservations WHERE strftime('%W', time_slot)=strftime('%W','now')")
        elif period == 'monthly':
            cursor.execute("SELECT * FROM reservations WHERE strftime('%m', time_slot)=strftime('%m','now')")
        else:
            return []
        return cursor.fetchall()
    # -------------------------
    # Backup & Restore
    # -------------------------
    def backup_database(self, backup_file='backup.db'):
        """Back up the database to a file."""
        self.conn.commit()
        with sqlite3.connect(backup_file) as backup_conn:
            self.conn.backup(backup_conn)
        return backup_file
    def restore_database(self, backup_file='backup.db'):
        """Restore the database from a backup file."""
        self.conn.close()
        os.remove(self.db_name)
        os.rename(backup_file, self.db_name)
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
    def close(self):
        self.conn.close()
    
    # -------------------------
    # Section management
    # -------------------------
    def _initialize_default_sections(self):
        """Initialize default sections if none exist."""
        cursor = self.conn.cursor()
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
            self.conn.commit()
    
    def get_sections(self):
        """Get all sections ordered by display_order."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sections ORDER BY display_order")
        return cursor.fetchall()
    
    def get_section_by_id(self, section_id):
        """Get a section by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
        return cursor.fetchone()
    
    def get_section_tables(self, section_id):
        """Get all table numbers assigned to a section."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT table_number FROM section_tables WHERE section_id = ? ORDER BY table_number",
            (section_id,)
        )
        return [row["table_number"] for row in cursor.fetchall()]
    
    def get_all_section_tables(self):
        """Get all sections with their table assignments."""
        cursor = self.conn.cursor()
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
    
    def create_section(self, name, display_order=None):
        """Create a new section."""
        cursor = self.conn.cursor()
        if display_order is None:
            cursor.execute("SELECT COALESCE(MAX(display_order), 0) + 1 FROM sections")
            display_order = cursor.fetchone()[0]
        try:
            cursor.execute(
                "INSERT INTO sections (name, display_order) VALUES (?, ?)",
                (name, display_order)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Duplicate name
    
    def update_section(self, section_id, name):
        """Update a section's name."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE sections SET name = ? WHERE id = ?",
                (name, section_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate name
    
    def delete_section(self, section_id):
        """Delete a section and its table assignments."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM section_tables WHERE section_id = ?", (section_id,))
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        self.conn.commit()
    
    def assign_tables_to_section(self, section_id, table_numbers):
        """
        Assign tables to a section (replaces existing assignments).
        Tables are removed from other sections before assignment.
        """
        cursor = self.conn.cursor()
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
        self.conn.commit()