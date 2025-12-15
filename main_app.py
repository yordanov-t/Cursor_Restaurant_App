from db import DBManager
from visualization import AppUI
def main():
    # Initialize the database manager (creates the SQLite database if needed)
    db_manager = DBManager()
    # For demo purposes, add a default waiter if none exist
    if not db_manager.get_waiters():
        db_manager.add_waiter("John Doe")
        db_manager.add_waiter("Jane Smith")
    # Instantiate the UI and pass the database manager to it
    app = AppUI(db_manager)
    # Start the main event loop
    app.window.mainloop()
if __name__ == "__main__":
    main()