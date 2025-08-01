"""
Tests for the FileSystemManager class.

This module contains unit tests for file system operations,
including atomic operations, permission validation, and error recovery.
"""

import os
import pytest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, mock_open

from a3.managers.filesystem import (
    FileSystemManager, FileSystemError, PermissionError, 
    AtomicOperationError, CorruptionError
)


class TestFileSystemManager:
    """Test cases for FileSystemManager class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def fs_manager(self, temp_project_dir):
        """Create a FileSystemManager instance for testing."""
        manager = FileSystemManager(temp_project_dir)
        manager.initialize()
        return manager
    
    def test_initialization(self, temp_project_dir):
        """Test FileSystemManager initialization."""
        manager = FileSystemManager(temp_project_dir)
        assert not manager._initialized
        
        manager.initialize()
        assert manager._initialized
        assert manager._temp_dir.exists()
        assert manager._backup_dir.exists()
    
    def test_create_directory(self, fs_manager):
        """Test directory creation."""
        test_dir = "test_directory"
        
        # Create directory
        result = fs_manager.create_directory(test_dir)
        assert result is True
        
        # Verify directory exists
        expected_path = fs_manager.project_path / test_dir
        assert expected_path.exists()
        assert expected_path.is_dir()
        
        # Test creating existing directory (should succeed)
        result = fs_manager.create_directory(test_dir)
        assert result is True
    
    def test_create_nested_directory(self, fs_manager):
        """Test creating nested directories."""
        nested_dir = "parent/child/grandchild"
        
        result = fs_manager.create_directory(nested_dir)
        assert result is True
        
        expected_path = fs_manager.project_path / nested_dir
        assert expected_path.exists()
        assert expected_path.is_dir()
    
    def test_write_and_read_file(self, fs_manager):
        """Test writing and reading files."""
        test_file = "test_file.txt"
        test_content = "Hello, World!\nThis is a test file."
        
        # Write file
        result = fs_manager.write_file(test_file, test_content)
        assert result is True
        
        # Verify file exists
        assert fs_manager.file_exists(test_file)
        
        # Read file
        content = fs_manager.read_file(test_file)
        assert content == test_content
    
    def test_read_nonexistent_file(self, fs_manager):
        """Test reading a file that doesn't exist."""
        content = fs_manager.read_file("nonexistent.txt")
        assert content is None
    
    def test_file_exists(self, fs_manager):
        """Test file existence checking."""
        test_file = "existence_test.txt"
        
        # File doesn't exist initially
        assert not fs_manager.file_exists(test_file)
        
        # Create file
        fs_manager.write_file(test_file, "test content")
        
        # File should exist now
        assert fs_manager.file_exists(test_file)
    
    def test_delete_file(self, fs_manager):
        """Test file deletion."""
        test_file = "delete_test.txt"
        test_content = "This file will be deleted"
        
        # Create file
        fs_manager.write_file(test_file, test_content)
        assert fs_manager.file_exists(test_file)
        
        # Delete file
        result = fs_manager.delete_file(test_file)
        assert result is True
        
        # Verify file is deleted
        assert not fs_manager.file_exists(test_file)
        
        # Deleting non-existent file should succeed
        result = fs_manager.delete_file(test_file)
        assert result is True
    
    def test_copy_file(self, fs_manager):
        """Test file copying."""
        source_file = "source.txt"
        dest_file = "destination.txt"
        test_content = "Content to be copied"
        
        # Create source file
        fs_manager.write_file(source_file, test_content)
        
        # Copy file
        result = fs_manager.copy_file(source_file, dest_file)
        assert result is True
        
        # Verify both files exist with same content
        assert fs_manager.file_exists(source_file)
        assert fs_manager.file_exists(dest_file)
        
        source_content = fs_manager.read_file(source_file)
        dest_content = fs_manager.read_file(dest_file)
        assert source_content == dest_content == test_content
    
    def test_copy_nonexistent_file(self, fs_manager):
        """Test copying a file that doesn't exist."""
        with pytest.raises(FileSystemError):
            fs_manager.copy_file("nonexistent.txt", "destination.txt")
    
    def test_get_file_info(self, fs_manager):
        """Test getting file information."""
        test_file = "info_test.txt"
        test_content = "File info test content"
        
        # Non-existent file
        info = fs_manager.get_file_info(test_file)
        assert info is None
        
        # Create file
        fs_manager.write_file(test_file, test_content)
        
        # Get file info
        info = fs_manager.get_file_info(test_file)
        assert info is not None
        assert info["size"] == len(test_content.encode('utf-8'))
        assert info["is_file"] is True
        assert info["is_directory"] is False
        assert "modified" in info
        assert "created" in info
        assert "permissions" in info
    
    def test_atomic_write_operation(self, fs_manager):
        """Test that write operations are atomic."""
        test_file = "atomic_test.txt"
        original_content = "Original content"
        new_content = "New content"
        
        # Create original file
        fs_manager.write_file(test_file, original_content)
        
        # Mock an exception during the move operation
        with patch('shutil.move', side_effect=Exception("Simulated error")):
            with pytest.raises(FileSystemError):
                fs_manager.write_file(test_file, new_content)
        
        # Verify original file is unchanged
        content = fs_manager.read_file(test_file)
        assert content == original_content
        
        # Verify no temporary files are left behind
        temp_files = list(fs_manager._temp_dir.glob("*"))
        assert len(temp_files) == 0
    
    def test_backup_and_recovery(self, fs_manager):
        """Test backup creation and recovery functionality."""
        test_file = "backup_test.txt"
        original_content = "Original content for backup test"
        
        # Create file (no backup created for new file)
        fs_manager.write_file(test_file, original_content)
        
        # Modify file (this should create a backup of the original content)
        modified_content = "Modified content"
        fs_manager.write_file(test_file, modified_content)
        
        # Verify backup was created
        backups = list(fs_manager._backup_dir.glob(f"{test_file}.backup.*"))
        assert len(backups) >= 1
        
        # Modify file again (this should create another backup of the modified content)
        final_content = "Final content"
        time.sleep(0.1)  # Ensure different timestamp
        fs_manager.write_file(test_file, final_content)
        
        # Verify we have at least 2 backups now
        backups = list(fs_manager._backup_dir.glob(f"{test_file}.backup.*"))
        assert len(backups) >= 2
        
        # Simulate corruption by writing invalid content
        file_path = fs_manager.project_path / test_file
        with open(file_path, 'w') as f:
            f.write("CORRUPTED")
        
        # Attempt recovery (should restore from most recent backup)
        recovery_result = fs_manager.recover_from_corruption(test_file)
        assert recovery_result is True
        
        # Verify file was recovered (should be the most recent backup content)
        recovered_content = fs_manager.read_file(test_file)
        # The most recent backup should contain the modified_content (backup created before final_content write)
        assert recovered_content == modified_content
    
    def test_permission_validation(self, fs_manager):
        """Test permission validation."""
        test_file = "permission_test.txt"
        
        # Test with valid path
        result = fs_manager.validate_permissions(test_file)
        assert result is True
        
        # Create file and test permissions
        fs_manager.write_file(test_file, "test content")
        result = fs_manager.validate_permissions(test_file)
        assert result is True
    
    @pytest.mark.skipif(os.name == 'nt', reason="Permission tests don't work reliably on Windows")
    def test_permission_denied_scenarios(self, fs_manager):
        """Test scenarios where permissions are denied."""
        test_file = "readonly_test.txt"
        
        # Create file
        fs_manager.write_file(test_file, "test content")
        
        # Make file read-only
        file_path = fs_manager.project_path / test_file
        os.chmod(file_path, 0o444)  # Read-only
        
        # Try to write to read-only file
        with pytest.raises(PermissionError):
            fs_manager.write_file(test_file, "new content")
        
        # Restore permissions for cleanup
        os.chmod(file_path, 0o644)
    
    def test_content_verification(self, fs_manager):
        """Test content verification during write operations."""
        test_file = "verification_test.txt"
        test_content = "Content for verification test"
        
        # Normal write should succeed
        result = fs_manager.write_file(test_file, test_content)
        assert result is True
        
        # Verify content is correct
        actual_content = fs_manager.read_file(test_file)
        assert actual_content == test_content
    
    def test_cleanup_temp_files(self, fs_manager):
        """Test cleanup of temporary files."""
        # Create some temporary files
        temp_file1 = fs_manager._temp_dir / "temp1.tmp"
        temp_file2 = fs_manager._temp_dir / "temp2.tmp"
        
        temp_file1.write_text("temp content 1")
        temp_file2.write_text("temp content 2")
        
        # Make one file old (simulate old temp file)
        old_time = time.time() - 7200  # 2 hours ago
        os.utime(temp_file1, (old_time, old_time))
        
        # Run cleanup
        fs_manager.cleanup_temp_files()
        
        # Old temp file should be deleted, recent one should remain
        assert not temp_file1.exists()
        assert temp_file2.exists()
        
        # Clean up remaining file
        temp_file2.unlink()
    
    def test_backup_cleanup(self, fs_manager):
        """Test cleanup of old backup files."""
        test_file = "backup_cleanup_test.txt"
        
        # Create multiple backups by writing to file multiple times
        for i in range(7):
            content = f"Content version {i}"
            fs_manager.write_file(test_file, content)
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Verify we have multiple backups
        backups = list(fs_manager._backup_dir.glob(f"{test_file}.backup.*"))
        assert len(backups) >= 6  # Should have at least 6 backups
        
        # Run cleanup
        fs_manager.cleanup_temp_files()
        
        # Should keep only the 5 most recent backups
        remaining_backups = list(fs_manager._backup_dir.glob(f"{test_file}.backup.*"))
        assert len(remaining_backups) <= 5
    
    def test_absolute_path_handling(self, fs_manager):
        """Test handling of absolute paths."""
        # Create a temporary file outside project directory
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write("External file content")
            external_file = temp_file.name
        
        try:
            # Test reading external file with absolute path
            content = fs_manager.read_file(external_file)
            assert content == "External file content"
            
            # Test file existence check with absolute path
            assert fs_manager.file_exists(external_file)
            
        finally:
            # Clean up
            os.unlink(external_file)
    
    def test_error_handling_edge_cases(self, fs_manager):
        """Test various error handling edge cases."""
        # Test writing to a directory path
        test_dir = "test_directory"
        fs_manager.create_directory(test_dir)
        
        with pytest.raises(FileSystemError):
            fs_manager.write_file(test_dir, "content")  # Can't write to directory
        
        # Test reading a directory as file
        with pytest.raises(FileSystemError):
            fs_manager.read_file(test_dir)
        
        # Test deleting a directory as file
        with pytest.raises(FileSystemError):
            fs_manager.delete_file(test_dir)
    
    def test_validate_prerequisites(self, fs_manager):
        """Test prerequisite validation."""
        result = fs_manager.validate_prerequisites()
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_large_file_operations(self, fs_manager):
        """Test operations with larger files."""
        test_file = "large_file_test.txt"
        
        # Create content with multiple lines
        lines = [f"Line {i}: This is a test line with some content." for i in range(1000)]
        large_content = "\n".join(lines)
        
        # Write large file
        result = fs_manager.write_file(test_file, large_content)
        assert result is True
        
        # Read and verify
        read_content = fs_manager.read_file(test_file)
        assert read_content == large_content
        
        # Copy large file
        copy_file = "large_file_copy.txt"
        result = fs_manager.copy_file(test_file, copy_file)
        assert result is True
        
        # Verify copy
        copy_content = fs_manager.read_file(copy_file)
        assert copy_content == large_content
    
    def test_atomic_operation_failure_recovery(self, fs_manager):
        """Test recovery from atomic operation failures."""
        test_file = "atomic_failure_test.txt"
        original_content = "Original content"
        
        # Create original file
        fs_manager.write_file(test_file, original_content)
        
        # Mock shutil.move to fail during atomic write
        with patch('shutil.move', side_effect=Exception("Simulated move failure")):
            with pytest.raises(FileSystemError):
                fs_manager.write_file(test_file, "New content")
        
        # Verify original file is restored from backup
        content = fs_manager.read_file(test_file)
        assert content == original_content
    
    def test_corruption_detection_and_recovery(self, fs_manager):
        """Test corruption detection during write operations."""
        test_file = "corruption_test.txt"
        test_content = "Test content for corruption detection"
        
        # Create file
        fs_manager.write_file(test_file, test_content)
        
        # Mock content verification to fail
        with patch.object(fs_manager, '_verify_file_content', return_value=False):
            with pytest.raises(CorruptionError):
                fs_manager.write_file(test_file, "New content")
        
        # Original file should be preserved
        content = fs_manager.read_file(test_file)
        assert content == test_content
    
    def test_permission_validation_edge_cases(self, fs_manager):
        """Test permission validation in various scenarios."""
        # Test with non-existent parent directory
        deep_path = "non/existent/path/file.txt"
        result = fs_manager.validate_permissions(deep_path)
        assert result is True  # Should be able to create the path
        
        # Test with existing file
        test_file = "permission_edge_test.txt"
        fs_manager.write_file(test_file, "test content")
        result = fs_manager.validate_permissions(test_file)
        assert result is True
    
    def test_file_integrity_verification(self, fs_manager):
        """Test file integrity verification during copy operations."""
        source_file = "integrity_source.txt"
        dest_file = "integrity_dest.txt"
        test_content = "Content for integrity testing"
        
        # Create source file
        fs_manager.write_file(source_file, test_content)
        
        # Normal copy should succeed
        result = fs_manager.copy_file(source_file, dest_file)
        assert result is True
        
        # Verify integrity check works
        source_path = fs_manager.project_path / source_file
        dest_path = fs_manager.project_path / dest_file
        assert fs_manager._verify_file_integrity(source_path, dest_path) is True
    
    def test_backup_uniqueness_and_collision_handling(self, fs_manager):
        """Test that backup filenames are unique and handle collisions."""
        test_file = "backup_uniqueness_test.txt"
        
        # Create multiple backups rapidly
        for i in range(5):
            content = f"Content version {i}"
            fs_manager.write_file(test_file, content)
        
        # Verify all backups have unique names
        backups = list(fs_manager._backup_dir.glob(f"{test_file}.backup.*"))
        backup_names = [b.name for b in backups]
        assert len(backup_names) == len(set(backup_names))  # All names should be unique
    
    def test_recovery_from_multiple_backups(self, fs_manager):
        """Test recovery when multiple backups exist."""
        test_file = "multi_backup_recovery_test.txt"
        
        # Create multiple versions
        versions = ["Version 1", "Version 2", "Version 3"]
        for version in versions:
            fs_manager.write_file(test_file, version)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Corrupt the file
        file_path = fs_manager.project_path / test_file
        with open(file_path, 'w') as f:
            f.write("CORRUPTED DATA")
        
        # Recovery should use the most recent backup
        result = fs_manager.recover_from_corruption(test_file)
        assert result is True
        
        recovered_content = fs_manager.read_file(test_file)
        assert recovered_content == "Version 2"  # Most recent backup before Version 3
    
    def test_error_handling_with_invalid_paths(self, fs_manager):
        """Test error handling with invalid file paths."""
        # Test with invalid characters (if applicable to the OS)
        invalid_paths = ["", "   ", "\0invalid", "con.txt" if os.name == 'nt' else "/dev/null/invalid"]
        
        for invalid_path in invalid_paths:
            if invalid_path:  # Skip empty strings for this test
                try:
                    fs_manager.write_file(invalid_path, "test")
                except (FileSystemError, OSError, ValueError):
                    pass  # Expected to fail
    
    def test_concurrent_operation_safety(self, fs_manager):
        """Test safety of concurrent file operations."""
        test_file = "concurrent_test.txt"
        
        # Create initial file
        fs_manager.write_file(test_file, "Initial content")
        
        # Simulate concurrent writes by creating multiple temp files
        temp_files = []
        for i in range(3):
            temp_file = fs_manager._get_temp_file(fs_manager.project_path / test_file)
            temp_files.append(temp_file)
            with open(temp_file, 'w') as f:
                f.write(f"Concurrent content {i}")
        
        # Verify temp files are unique
        temp_names = [tf.name for tf in temp_files]
        assert len(temp_names) == len(set(temp_names))
        
        # Clean up temp files
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_state_validation_and_recovery(self, fs_manager):
        """Test state validation and recovery mechanisms."""
        # Test with corrupted .A3 directory structure
        if fs_manager._backup_dir.exists():
            # Create an invalid backup file
            invalid_backup = fs_manager._backup_dir / "invalid.backup"
            invalid_backup.write_text("invalid backup content")
            
            # Cleanup should handle invalid backups gracefully
            fs_manager.cleanup_temp_files()
            
            # Invalid backup should still exist (not cleaned up)
            assert invalid_backup.exists()
            
            # Clean up
            invalid_backup.unlink()


if __name__ == "__main__":
    pytest.main([__file__])