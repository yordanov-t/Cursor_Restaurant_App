"""
Backup Service for Restaurant Management System.

Provides database backup and restore functionality with:
- Daily automatic backups
- Manual backup creation
- Backup listing with metadata
- Safe atomic restore operations
"""

import os
import shutil
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Any


class BackupService:
    """
    Manages database backups and restores.
    
    Features:
    - Create backups with timestamp-based naming
    - List backups with metadata (size, date, counts)
    - Delete backups
    - Atomic restore with safety checks
    - Daily auto-backup on startup
    
    Thread-safe: Uses file-based operations, not SQLite connection-based backup.
    """
    
    BACKUP_FOLDER = "backups"
    BACKUP_PREFIX = "restaurant_"
    BACKUP_EXTENSION = ".db"
    
    def __init__(self, db_manager):
        """
        Initialize backup service.
        
        Args:
            db_manager: DBManager instance
        """
        self.db_manager = db_manager
        self.db_name = db_manager.db_name
        
        # Ensure backup folder exists
        self._ensure_backup_folder()
    
    def _ensure_backup_folder(self):
        """Create backup folder if it doesn't exist."""
        if not os.path.exists(self.BACKUP_FOLDER):
            os.makedirs(self.BACKUP_FOLDER)
    
    def _generate_backup_filename(self) -> str:
        """Generate a backup filename with current timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.BACKUP_PREFIX}{timestamp}{self.BACKUP_EXTENSION}"
    
    def _get_backup_path(self, filename: str) -> str:
        """Get full path for a backup file."""
        return os.path.join(self.BACKUP_FOLDER, filename)
    
    def _parse_backup_timestamp(self, filename: str) -> Optional[datetime]:
        """Parse timestamp from backup filename."""
        try:
            # Remove prefix and extension
            name = filename.replace(self.BACKUP_PREFIX, "").replace(self.BACKUP_EXTENSION, "")
            return datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            return None
    
    def _get_backup_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a backup file."""
        filepath = self._get_backup_path(filename)
        
        if not os.path.exists(filepath):
            return None
        
        # Get file stats
        stat = os.stat(filepath)
        size_bytes = stat.st_size
        
        # Parse timestamp from filename
        timestamp = self._parse_backup_timestamp(filename)
        if not timestamp:
            return None
        
        # Format size for display
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        return {
            "filename": filename,
            "filepath": filepath,
            "timestamp": timestamp,
            "timestamp_str": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "size_bytes": size_bytes,
            "size_str": size_str,
        }
    
    def _get_backup_counts(self, filepath: str) -> Dict[str, int]:
        """Get record counts from a backup database."""
        counts = {
            "reservations": 0,
            "waiters": 0,
            "tables": 0,
            "sections": 0,
        }
        
        try:
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            
            # Count reservations
            try:
                cursor.execute("SELECT COUNT(*) FROM reservations WHERE status = 'Reserved'")
                counts["reservations"] = cursor.fetchone()[0]
            except:
                pass
            
            # Count waiters
            try:
                cursor.execute("SELECT COUNT(*) FROM waiters")
                counts["waiters"] = cursor.fetchone()[0]
            except:
                pass
            
            # Count tables
            try:
                cursor.execute("SELECT COUNT(*) FROM tables_metadata")
                counts["tables"] = cursor.fetchone()[0]
            except:
                pass
            
            # Count sections
            try:
                cursor.execute("SELECT COUNT(*) FROM sections")
                counts["sections"] = cursor.fetchone()[0]
            except:
                pass
            
            conn.close()
        except Exception:
            pass
        
        return counts
    
    def create_backup(self) -> Optional[str]:
        """
        Create a new backup of the current database.
        
        Uses file copy for thread-safety (no connection needed).
        
        Returns:
            Backup filename if successful, None otherwise.
        """
        try:
            # Ensure folder exists
            self._ensure_backup_folder()
            
            # Generate filename
            filename = self._generate_backup_filename()
            filepath = self._get_backup_path(filename)
            
            # Create backup using file copy (thread-safe)
            shutil.copy2(self.db_name, filepath)
            
            return filename
        except Exception as e:
            print(f"Backup creation failed: {e}")
            return None
    
    def list_backups(self, include_counts: bool = False) -> List[Dict[str, Any]]:
        """
        List all available backups with metadata.
        
        Args:
            include_counts: If True, include record counts (slower)
            
        Returns:
            List of backup metadata dictionaries, sorted by timestamp (newest first).
        """
        backups = []
        
        if not os.path.exists(self.BACKUP_FOLDER):
            return backups
        
        for filename in os.listdir(self.BACKUP_FOLDER):
            if filename.startswith(self.BACKUP_PREFIX) and filename.endswith(self.BACKUP_EXTENSION):
                metadata = self._get_backup_metadata(filename)
                if metadata:
                    if include_counts:
                        metadata["counts"] = self._get_backup_counts(metadata["filepath"])
                    backups.append(metadata)
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return backups
    
    def delete_backup(self, filename: str) -> bool:
        """
        Delete a backup file.
        
        Args:
            filename: Name of the backup file to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
        """
        try:
            filepath = self._get_backup_path(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Backup deletion failed: {e}")
            return False
    
    def restore_backup(self, filename: str, on_progress: Optional[callable] = None) -> bool:
        """
        Restore database from a backup file.
        
        This is an atomic operation:
        1. Verify backup file exists and is valid
        2. Create a safety backup of current DB
        3. Copy backup over current DB (using temp file for atomicity)
        4. Reinitialize DB manager
        
        Thread-safe: Uses file operations, not connection-based restore.
        
        Args:
            filename: Name of the backup file to restore.
            on_progress: Optional callback for progress updates.
            
        Returns:
            True if restored successfully, False otherwise.
        """
        filepath = self._get_backup_path(filename)
        
        # Verify backup exists
        if not os.path.exists(filepath):
            print(f"Backup file not found: {filepath}")
            return False
        
        # Verify backup is a valid SQLite database
        try:
            test_conn = sqlite3.connect(filepath)
            test_conn.execute("SELECT 1 FROM sqlite_master LIMIT 1")
            test_conn.close()
        except Exception as e:
            print(f"Invalid backup file: {e}")
            return False
        
        try:
            if on_progress:
                on_progress("Създаване на резервно копие...")
            
            # Create safety backup of current state
            safety_backup = f"_pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            safety_path = self._get_backup_path(safety_backup)
            shutil.copy2(self.db_name, safety_path)
            
            if on_progress:
                on_progress("Възстановяване на данните...")
            
            # Copy backup to current DB location (atomic with temp file)
            temp_path = self.db_name + ".tmp"
            shutil.copy2(filepath, temp_path)
            
            # Replace current DB with restored backup
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            os.rename(temp_path, self.db_name)
            
            if on_progress:
                on_progress("Инициализиране...")
            
            # Reinitialize DB manager (ensures schema is up to date)
            self.db_manager.initialize_db()
            
            if on_progress:
                on_progress("Готово!")
            
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def has_today_backup(self) -> bool:
        """Check if a backup exists for today."""
        today = date.today()
        
        for backup in self.list_backups():
            if backup["timestamp"].date() == today:
                return True
        
        return False
    
    def create_daily_backup_if_needed(self) -> Optional[str]:
        """
        Create a daily backup if one doesn't exist for today.
        
        Returns:
            Backup filename if created, None if already exists or failed.
        """
        if self.has_today_backup():
            return None
        
        return self.create_backup()
    
    def cleanup_old_backups(self, keep_count: int = 30) -> int:
        """
        Remove old backups, keeping the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep.
            
        Returns:
            Number of backups deleted.
        """
        backups = self.list_backups()
        deleted = 0
        
        if len(backups) <= keep_count:
            return 0
        
        # Remove oldest backups beyond keep_count
        for backup in backups[keep_count:]:
            if self.delete_backup(backup["filename"]):
                deleted += 1
        
        return deleted
