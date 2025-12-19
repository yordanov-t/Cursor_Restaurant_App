"""
Restaurant Management System - Main Entry Point

Supports both modern Flet UI (default) and legacy Tkinter UI (--legacy flag).
"""

import sys


def main():
    """Main entry point with UI selection."""
    # Check for legacy flag
    use_legacy = "--legacy" in sys.argv or "-l" in sys.argv
    
    if use_legacy:
        # Run legacy Tkinter UI
        print("Starting legacy Tkinter UI...")
        from db import DBManager
        from legacy_tk_ui import AppUI
        
        db_manager = DBManager()
        if not db_manager.get_waiters():
            db_manager.add_waiter("John Doe")
            db_manager.add_waiter("Jane Smith")
        
        app = AppUI(db_manager)
        app.window.mainloop()
    else:
        # Run modern Flet UI
        print("Starting Flet UI...")
        import flet as ft
        from flet_app import main as flet_main
        
        ft.app(target=flet_main)


if __name__ == "__main__":
    main()
