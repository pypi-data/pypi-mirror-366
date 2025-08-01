"""
File system operations manager for AI Project Builder.

This module provides the FileSystemManager class that handles all file system
operations with atomic operations, permission validation, and error recovery.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import stat
import time
import hashlib

from ..core.interfaces import FileSystemManagerInterface
from ..core.models import ValidationResult
from .base import BaseFileSystemManager


class FileSystemError(Exception):
    """Base exception for file system errors."""
    pass


class PermissionError(FileSystemError):
    """Exception raised when permission validation fails."""
    pass


class AtomicOperationError(FileSystemError):
    """Exception raised during atomic operations."""
    pass


class CorruptionError(FileSystemError):
    """Exception raised when file corruption is detected."""
    pass


class FileSystemManager(BaseFileSystemManager):
    """
    Manages file system operations with atomic operations and error handling.
    
    Provides reliable file operations with permission validation, atomic writes,
    and corruption detection/recovery mechanisms.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the file system manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        self._temp_dir = None
        self._backup_dir = None
    
    def initialize(self) -> None:
        """Initialize the file system manager and create necessary directories."""
        super().initialize()
        
        # Create temporary directory for atomic operations
        self._temp_dir = self.project_path / ".A3" / "temp"
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup directory for recovery
        self._backup_dir = self.project_path / ".A3" / "backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_directory(self, path: str) -> bool:
        """
        Create a directory with proper error handling.
        
        Args:
            path: Path to the directory to create
            
        Returns:
            True if directory was created successfully, False otherwise
            
        Raises:
            FileSystemError: If directory creation fails
        """
        self._ensure_initialized()
        
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            # Validate permissions on parent directory
            if not self._validate_parent_permissions(target_path):
                raise PermissionError(f"Insufficient permissions to create directory: {target_path}")
            
            # Create directory with parents
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Verify creation
            if not target_path.exists() or not target_path.is_dir():
                raise FileSystemError(f"Failed to create directory: {target_path}")
            
            return True
            
        except PermissionError:
            raise
        except Exception as e:
            raise FileSystemError(f"Failed to create directory {path}: {e}") from e
    
    def write_file(self, path: str, content: str) -> bool:
        """
        Write content to a file with atomic operations.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
            
        Returns:
            True if file was written successfully, False otherwise
            
        Raises:
            FileSystemError: If file writing fails
        """
        self._ensure_initialized()
        
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            # Validate permissions
            if not self.validate_permissions(str(target_path)):
                raise PermissionError(f"Insufficient permissions to write file: {target_path}")
            
            # Create parent directory if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            backup_path = None
            if target_path.exists():
                backup_path = self._create_backup(target_path)
            
            try:
                # Write to temporary file first (atomic operation)
                temp_file = self._get_temp_file(target_path)
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Verify content was written correctly
                if not self._verify_file_content(temp_file, content):
                    raise CorruptionError(f"Content verification failed for: {target_path}")
                
                # Move temporary file to final location (atomic on most filesystems)
                shutil.move(str(temp_file), str(target_path))
                
                # Verify final file
                if not self._verify_file_content(target_path, content):
                    raise CorruptionError(f"Final content verification failed for: {target_path}")
                
                # Keep backup for recovery purposes (don't delete it)
                
                return True
                
            except Exception as write_error:
                # Clean up temporary file
                if 'temp_file' in locals() and Path(temp_file).exists():
                    Path(temp_file).unlink()
                
                # Restore from backup if available
                if backup_path and backup_path.exists():
                    try:
                        shutil.move(str(backup_path), str(target_path))
                    except Exception:
                        pass  # Best effort recovery
                
                raise write_error
            
        except (PermissionError, CorruptionError):
            raise
        except Exception as e:
            raise FileSystemError(f"Failed to write file {path}: {e}") from e
    
    def read_file(self, path: str) -> Optional[str]:
        """
        Read content from a file with error handling.
        
        Args:
            path: Path to the file to read
            
        Returns:
            File content as string, or None if file doesn't exist
            
        Raises:
            FileSystemError: If file reading fails
        """
        self._ensure_initialized()
        
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            if not target_path.exists():
                return None
            
            if not target_path.is_file():
                raise FileSystemError(f"Path is not a file: {target_path}")
            
            # Check read permissions
            if not os.access(target_path, os.R_OK):
                raise PermissionError(f"No read permission for file: {target_path}")
            
            # Read file content
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except PermissionError:
            raise
        except Exception as e:
            raise FileSystemError(f"Failed to read file {path}: {e}") from e
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            return target_path.exists() and target_path.is_file()
            
        except Exception:
            return False
    
    def validate_permissions(self, path: str) -> bool:
        """
        Validate that we have necessary permissions for operations.
        
        Args:
            path: Path to validate permissions for
            
        Returns:
            True if permissions are sufficient, False otherwise
        """
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            if target_path.exists():
                # Check if we can read and write existing file
                return os.access(target_path, os.R_OK | os.W_OK)
            else:
                # Check if we can create file in parent directory
                return self._validate_parent_permissions(target_path)
            
        except Exception:
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file with proper error handling.
        
        Args:
            path: Path to the file to delete
            
        Returns:
            True if file was deleted successfully, False otherwise
            
        Raises:
            FileSystemError: If file deletion fails
        """
        self._ensure_initialized()
        
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            if not target_path.exists():
                return True  # Already deleted
            
            if not target_path.is_file():
                raise FileSystemError(f"Path is not a file: {target_path}")
            
            # Check permissions
            if not os.access(target_path, os.W_OK):
                raise PermissionError(f"No write permission for file: {target_path}")
            
            # Create backup before deletion
            backup_path = self._create_backup(target_path)
            
            try:
                # Delete the file
                target_path.unlink()
                
                # Verify deletion
                if target_path.exists():
                    raise FileSystemError(f"File still exists after deletion: {target_path}")
                
                return True
                
            except Exception as delete_error:
                # Restore from backup if deletion failed
                if backup_path and backup_path.exists():
                    try:
                        shutil.move(str(backup_path), str(target_path))
                    except Exception:
                        pass  # Best effort recovery
                
                raise delete_error
            
        except PermissionError:
            raise
        except Exception as e:
            raise FileSystemError(f"Failed to delete file {path}: {e}") from e
    
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Copy a file with atomic operations.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if file was copied successfully, False otherwise
            
        Raises:
            FileSystemError: If file copying fails
        """
        self._ensure_initialized()
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            # Make paths absolute if they're relative to project
            if not source_path.is_absolute():
                source_path = self.project_path / source_path
            if not dest_path.is_absolute():
                dest_path = self.project_path / dest_path
            
            # Validate source file
            if not source_path.exists():
                raise FileSystemError(f"Source file does not exist: {source_path}")
            
            if not source_path.is_file():
                raise FileSystemError(f"Source is not a file: {source_path}")
            
            # Check permissions
            if not os.access(source_path, os.R_OK):
                raise PermissionError(f"No read permission for source file: {source_path}")
            
            if not self.validate_permissions(str(dest_path)):
                raise PermissionError(f"Insufficient permissions for destination: {dest_path}")
            
            # Create destination parent directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if destination exists
            backup_path = None
            if dest_path.exists():
                backup_path = self._create_backup(dest_path)
            
            try:
                # Copy to temporary file first
                temp_file = self._get_temp_file(dest_path)
                shutil.copy2(str(source_path), str(temp_file))
                
                # Verify copy
                if not self._verify_file_integrity(source_path, Path(temp_file)):
                    raise CorruptionError(f"File integrity check failed during copy")
                
                # Move to final destination
                shutil.move(str(temp_file), str(dest_path))
                
                # Final verification
                if not self._verify_file_integrity(source_path, dest_path):
                    raise CorruptionError(f"Final integrity check failed for copied file")
                
                # Keep backup for recovery purposes (don't delete it)
                
                return True
                
            except Exception as copy_error:
                # Clean up temporary file
                if 'temp_file' in locals() and Path(temp_file).exists():
                    Path(temp_file).unlink()
                
                # Restore from backup if available
                if backup_path and backup_path.exists():
                    try:
                        shutil.move(str(backup_path), str(dest_path))
                    except Exception:
                        pass  # Best effort recovery
                
                raise copy_error
            
        except (PermissionError, CorruptionError):
            raise
        except Exception as e:
            raise FileSystemError(f"Failed to copy file from {source} to {destination}: {e}") from e
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information including size, modification time, and permissions.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary with file information, or None if file doesn't exist
        """
        try:
            target_path = Path(path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            if not target_path.exists():
                return None
            
            stat_info = target_path.stat()
            
            return {
                "path": str(target_path),
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
                "created": stat_info.st_ctime,
                "permissions": oct(stat_info.st_mode)[-3:],
                "is_file": target_path.is_file(),
                "is_directory": target_path.is_dir()
            }
            
        except Exception:
            return None
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files and backups."""
        if not self._initialized:
            return
        
        # Clean up temporary files
        if self._temp_dir and self._temp_dir.exists():
            for temp_file in self._temp_dir.glob("*"):
                try:
                    if temp_file.is_file():
                        # Only delete files older than 1 hour
                        if time.time() - temp_file.stat().st_mtime > 3600:
                            temp_file.unlink()
                except Exception:
                    continue  # Best effort cleanup
        
        # Clean up old backups (keep last 5 for each file)
        if self._backup_dir and self._backup_dir.exists():
            backup_groups = {}
            
            # Group backups by original file
            for backup_file in self._backup_dir.glob("*.backup.*"):
                try:
                    # Extract original filename from backup name
                    parts = backup_file.name.split('.backup.')
                    if len(parts) >= 2:
                        original_name = parts[0]
                        if original_name not in backup_groups:
                            backup_groups[original_name] = []
                        backup_groups[original_name].append(backup_file)
                except Exception:
                    continue
            
            # Keep only the 5 most recent backups for each file
            for original_name, backups in backup_groups.items():
                backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for old_backup in backups[5:]:
                    try:
                        old_backup.unlink()
                    except Exception:
                        continue  # Best effort cleanup    

    # Private helper methods
    
    def _validate_parent_permissions(self, target_path: Path) -> bool:
        """Validate permissions on parent directory for file operations."""
        try:
            parent = target_path.parent
            
            # Check if parent exists and we can write to it
            if parent.exists():
                return os.access(parent, os.W_OK | os.X_OK)
            else:
                # Recursively check parent directories
                return self._validate_parent_permissions(parent)
            
        except Exception:
            return False
    
    def _get_temp_file(self, target_path: Path) -> Path:
        """Get a temporary file path for atomic operations."""
        if not self._temp_dir:
            raise FileSystemError("Temporary directory not initialized")
        
        # Create unique temporary filename with milliseconds and counter
        timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
        pid = os.getpid()
        temp_name = f"{target_path.name}.{timestamp}.{pid}.tmp"
        temp_path = self._temp_dir / temp_name
        
        # Ensure temp filename is unique
        counter = 0
        while temp_path.exists():
            counter += 1
            temp_name = f"{target_path.name}.{timestamp}.{pid}.{counter}.tmp"
            temp_path = self._temp_dir / temp_name
        
        return temp_path
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of an existing file."""
        if not self._backup_dir:
            raise FileSystemError("Backup directory not initialized")
        
        if not file_path.exists():
            raise FileSystemError(f"Cannot backup non-existent file: {file_path}")
        
        # Create backup filename with timestamp and process ID for uniqueness
        timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
        pid = os.getpid()
        backup_name = f"{file_path.name}.backup.{timestamp}.{pid}"
        backup_path = self._backup_dir / backup_name
        
        # Ensure backup filename is unique
        counter = 0
        while backup_path.exists():
            counter += 1
            backup_name = f"{file_path.name}.backup.{timestamp}.{pid}.{counter}"
            backup_path = self._backup_dir / backup_name
        
        # Copy file to backup location
        shutil.copy2(str(file_path), str(backup_path))
        
        return backup_path
    
    def _verify_file_content(self, file_path: Path, expected_content: str) -> bool:
        """Verify that file contains expected content."""
        try:
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
            
            return actual_content == expected_content
            
        except Exception:
            return False
    
    def _verify_file_integrity(self, source_path: Path, dest_path: Path) -> bool:
        """Verify file integrity using checksums."""
        try:
            if not source_path.exists() or not dest_path.exists():
                return False
            
            # Compare file sizes first (quick check)
            if source_path.stat().st_size != dest_path.stat().st_size:
                return False
            
            # Compare checksums for integrity
            source_checksum = self._calculate_checksum(source_path)
            dest_checksum = self._calculate_checksum(dest_path)
            
            return source_checksum == dest_checksum
            
        except Exception:
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def recover_from_corruption(self, file_path: str) -> bool:
        """
        Attempt to recover a corrupted file from backups.
        
        Args:
            file_path: Path to the corrupted file
            
        Returns:
            True if recovery was successful, False otherwise
        """
        self._ensure_initialized()
        
        try:
            target_path = Path(file_path)
            
            # Make path absolute if it's relative to project
            if not target_path.is_absolute():
                target_path = self.project_path / target_path
            
            if not self._backup_dir or not self._backup_dir.exists():
                return False
            
            # Find backups for this file
            backup_pattern = f"{target_path.name}.backup.*"
            backups = list(self._backup_dir.glob(backup_pattern))
            
            if not backups:
                return False
            
            # Sort backups by timestamp (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Try to restore from the most recent backup
            for backup_path in backups:
                try:
                    # Verify backup integrity
                    if self._is_file_readable(backup_path):
                        # Copy backup to original location
                        shutil.copy2(str(backup_path), str(target_path))
                        
                        # Verify restoration
                        if self._is_file_readable(target_path):
                            return True
                        
                except Exception:
                    continue  # Try next backup
            
            return False
            
        except Exception:
            return False
    
    def _is_file_readable(self, file_path: Path) -> bool:
        """Check if a file is readable and not corrupted."""
        try:
            if not file_path.exists() or not file_path.is_file():
                return False
            
            # Try to read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            
            return True
            
        except Exception:
            return False
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate file system manager prerequisites."""
        result = super().validate_prerequisites()
        
        if self._initialized:
            # Check if temp and backup directories exist
            if not self._temp_dir or not self._temp_dir.exists():
                result.issues.append("Temporary directory not available")
            
            if not self._backup_dir or not self._backup_dir.exists():
                result.issues.append("Backup directory not available")
            
            # Check write permissions on project directory
            if not os.access(self.project_path, os.W_OK):
                result.issues.append(f"No write permission on project directory: {self.project_path}")
        
        return result