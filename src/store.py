"""
File watching and data storage for PET Resource Allocation Dashboard
Handles monitoring the data folder and managing the latest file
"""

import os
import re
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from datetime import datetime
import logging

from .schema import WATCH_PATTERN, WATCH_INTERVAL_SECONDS, MAX_BACKUP_FILES
from .etl import process_pet_csv

logger = logging.getLogger(__name__)

class PETDataStore:
    """Manages file watching and data storage for PET dashboard"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.last_check_time = 0
        self.current_file: Optional[Path] = None
        self.current_data = None
        self.last_modified: Optional[datetime] = None

    def find_latest_file(self) -> Optional[Tuple[Path, datetime]]:
        """
        Find the most recently modified PET CSV file in the data directory

        Returns:
            Tuple of (file_path, modification_time) or None if no files found
        """
        if not self.data_dir.exists():
            return None

        matching_files = []
        for file_path in self.data_dir.glob("*.csv"):
            if re.search(WATCH_PATTERN, file_path.name, re.IGNORECASE):
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    matching_files.append((file_path, mtime))
                except OSError as e:
                    logger.warning(f"Could not access file {file_path}: {e}")

        if not matching_files:
            return None

        # Return the most recently modified file
        return max(matching_files, key=lambda x: x[1])

    def should_refresh(self) -> bool:
        """
        Check if data should be refreshed based on file changes or time interval

        Returns:
            True if refresh is needed
        """
        current_time = time.time()

        # Check if enough time has passed since last check
        if current_time - self.last_check_time < WATCH_INTERVAL_SECONDS:
            return False

        self.last_check_time = current_time

        # Check for new or modified files
        latest_file_info = self.find_latest_file()

        if latest_file_info is None:
            # No files found
            if self.current_file is not None:
                logger.info("No PET CSV files found, clearing data")
                self.current_file = None
                self.current_data = None
                self.last_modified = None
                return True
            return False

        file_path, file_mtime = latest_file_info

        # Check if file has changed
        if (self.current_file != file_path or
            self.last_modified is None or
            file_mtime > self.last_modified):

            logger.info(f"New or updated file detected: {file_path}")
            self.current_file = file_path
            self.last_modified = file_mtime
            return True

        return False

    def load_data(self, force_refresh: bool = False) -> Optional[Tuple]:
        """
        Load and process the latest PET CSV file

        Args:
            force_refresh: Force reload even if file hasn't changed

        Returns:
            Tuple of (people_df, assignments_df, capabilities_df, stats) or None
        """
        if not force_refresh and not self.should_refresh():
            return self.current_data

        if self.current_file is None:
            latest_file_info = self.find_latest_file()
            if latest_file_info is None:
                return None
            self.current_file, self.last_modified = latest_file_info

        try:
            logger.info(f"Processing file: {self.current_file}")
            people_df, assignments_df, capabilities_df, stats = process_pet_csv(self.current_file)

            self.current_data = (people_df, assignments_df, capabilities_df, stats)

            # Clean up old backup files
            self._cleanup_old_files()

            return self.current_data

        except Exception as e:
            logger.error(f"Error processing file {self.current_file}: {e}")
            return None

    def save_uploaded_file(self, uploaded_file, filename: str) -> bool:
        """
        Save an uploaded file to the data directory

        Args:
            uploaded_file: Streamlit uploaded file object
            filename: Desired filename

        Returns:
            True if successful
        """
        try:
            file_path = self.data_dir / filename

            # Clean up old uploaded files before saving new one
            self._cleanup_uploaded_files()

            # Read uploaded file content
            content = uploaded_file.read()

            # Write to data directory
            with open(file_path, 'wb') as f:
                f.write(content)

            logger.info(f"Saved uploaded file: {file_path}")

            # Force refresh on next load
            self.last_modified = None

            return True

        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            return False

    def _cleanup_uploaded_files(self) -> None:
        """Clean up old uploaded files to prevent resource issues"""
        try:
            uploaded_files = []
            for file_path in self.data_dir.glob("*.csv"):
                if "uploaded" in file_path.name and "PET Resource Allocation" in file_path.name:
                    uploaded_files.append(file_path)

            # Keep only the most recent 2 uploaded files
            if len(uploaded_files) > 2:
                uploaded_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                files_to_remove = uploaded_files[2:]  # Keep only the 2 most recent

                for file_path in files_to_remove:
                    try:
                        file_path.unlink()
                        logger.info(f"Cleaned up old uploaded file: {file_path}")
                    except OSError as e:
                        logger.warning(f"Could not remove old file {file_path}: {e}")

        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def _cleanup_old_files(self) -> None:
        """Clean up old backup files, keeping only the most recent ones"""
        if not self.data_dir.exists():
            return

        try:
            matching_files = []
            for file_path in self.data_dir.glob("*.csv"):
                if re.search(WATCH_PATTERN, file_path.name, re.IGNORECASE):
                    mtime = file_path.stat().st_mtime
                    matching_files.append((file_path, mtime))

            if len(matching_files) > MAX_BACKUP_FILES:
                # Sort by modification time, keep newest
                matching_files.sort(key=lambda x: x[1], reverse=True)
                files_to_remove = matching_files[MAX_BACKUP_FILES:]

                for file_path, _ in files_to_remove:
                    try:
                        file_path.unlink()
                        logger.info(f"Removed old backup file: {file_path}")
                    except OSError as e:
                        logger.warning(f"Could not remove old file {file_path}: {e}")

        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def get_file_info(self) -> Optional[Dict[str, str]]:
        """
        Get information about the current file

        Returns:
            Dictionary with file information or None
        """
        if self.current_file is None or self.last_modified is None:
            return None

        return {
            'filename': self.current_file.name,
            'path': str(self.current_file),
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S'),
            'size': f"{self.current_file.stat().st_size / 1024:.1f} KB"
        }

    def get_available_files(self) -> List[Dict[str, str]]:
        """
        Get list of available PET CSV files for manual selection

        Returns:
            List of file info dictionaries
        """
        if not self.data_dir.exists():
            return []

        files_info = []
        for file_path in self.data_dir.glob("*.csv"):
            if re.search(WATCH_PATTERN, file_path.name, re.IGNORECASE):
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    files_info.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'last_modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                        'size': f"{file_path.stat().st_size / 1024:.1f} KB"
                    })
                except OSError:
                    continue

        # Sort by modification time, newest first
        files_info.sort(key=lambda x: x['last_modified'], reverse=True)
        return files_info

# Global data store instance
_data_store = None

def get_data_store() -> PETDataStore:
    """Get or create global data store instance"""
    global _data_store
    if _data_store is None:
        _data_store = PETDataStore()
    return _data_store

def load_latest_data(force_refresh: bool = False):
    """
    Load the latest PET data

    Args:
        force_refresh: Force reload data

    Returns:
        Tuple of (people_df, assignments_df, capabilities_df, stats) or None
    """
    store = get_data_store()
    return store.load_data(force_refresh=force_refresh)
