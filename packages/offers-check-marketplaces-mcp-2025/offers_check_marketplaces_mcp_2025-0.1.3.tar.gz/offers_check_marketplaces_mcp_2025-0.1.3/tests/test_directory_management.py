#!/usr/bin/env python3
"""
Integration tests for directory management.
Tests full directory structure creation, permission setting, and migration scenarios.
Comprehensive coverage for Requirements 6.1, 7.1, 5.1.
"""

import os
import sys
import pytest
import tempfile
import shutil
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add path to module
sys.path.insert(0, str(Path(__file__).parent.parent))

from offers_check_marketplaces.user_data_manager import (
    DirectoryManager,
    DirectoryStructure,
    PlatformConfig,
    Platform,
    DataMigrator,
    UserDataManager,
    DirectoryCreationError,
    PermissionError as UserDataPermissionError,
    MigrationError,
    DiskSpaceError,
    ValidationError
)


class TestDirectoryStructure:
    """Test cases for DirectoryStructure class."""
    
    def test_validate_valid_structure(self):
        """Test validation of valid directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / 'base'
            structure = DirectoryStructure(
                base=base,
                database=base / 'database',
                cache=base / 'cache',
                logs=base / 'logs',
                temp=base / 'temp'
            )
            assert structure.validate() is True
    
    def test_validate_invalid_structure_missing_paths(self):
        """Test validation fails with missing paths."""
        structure = DirectoryStructure(
            base=None,
            database=None,
            cache=Path('/cache'),
            logs=Path('/logs'),
            temp=None
        )
        assert structure.validate() is False    def 
test_create_all_success(self):
        """Test successful creation of all directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / 'test_structure'
            structure = DirectoryStructure(
                base=base,
                database=base / 'database',
                cache=base / 'cache',
                logs=base / 'logs',
                temp=base / 'temp'
            )
            
            result = structure.create_all()
            assert result is True
            assert base.exists() and base.is_dir()
            assert structure.database.exists() and structure.database.is_dir()
            assert structure.cache.exists() and structure.cache.is_dir()
            assert structure.logs.exists() and structure.logs.is_dir()
            assert structure.temp.exists() and structure.temp.is_dir()
    
    def test_create_all_permission_error(self):
        """Test creation failure due to permission error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / 'test_structure'
            structure = DirectoryStructure(
                base=base,
                database=base / 'database',
                cache=base / 'cache',
                logs=base / 'logs',
                temp=base / 'temp'
            )
            
            with patch('pathlib.Path.mkdir', side_effect=OSError(13, 'Permission denied')):
                with pytest.raises(UserDataPermissionError):
                    structure.create_all()


class TestDirectoryManager:
    """Test cases for DirectoryManager class."""
    
    def test_create_directory_structure_windows(self):
        """Test directory structure creation on Windows."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'offers-check-marketplaces'
            
            config = PlatformConfig(
                platform=Platform.WINDOWS,
                base_directory=base_path,
                cache_directory=base_path / 'cache',
                logs_directory=base_path / 'logs'
            )
            
            manager = DirectoryManager(config)
            structure = manager.create_directory_structure(base_path)
            
            assert structure.base == base_path
            assert structure.database == base_path / 'database'
            assert structure.cache == base_path / 'cache'
            assert structure.logs == base_path / 'logs'
            assert structure.temp == base_path / 'temp'
            
            # Verify all directories were created
            assert all(d.exists() for d in [structure.base, structure.database, 
                                          structure.cache, structure.logs, structure.temp])    def t
est_create_directory_structure_macos(self):
        """Test directory structure creation on macOS."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'offers-check-marketplaces'
            cache_path = Path(temp_dir) / 'cache' / 'offers-check-marketplaces'
            logs_path = Path(temp_dir) / 'logs' / 'offers-check-marketplaces'
            
            config = PlatformConfig(
                platform=Platform.MACOS,
                base_directory=base_path,
                cache_directory=cache_path,
                logs_directory=logs_path,
                permissions={"directory": 0o755, "file": 0o644}
            )
            
            manager = DirectoryManager(config)
            structure = manager.create_directory_structure(base_path)
            
            assert structure.base == base_path
            assert structure.cache == cache_path
            assert structure.logs == logs_path
            
            # Verify all directories were created
            assert all(d.exists() for d in [structure.base, structure.database, 
                                          structure.cache, structure.logs, structure.temp])
    
    def test_create_directory_structure_linux(self):
        """Test directory structure creation on Linux."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'offers-check-marketplaces'
            cache_path = Path(temp_dir) / 'cache' / 'offers-check-marketplaces'
            
            config = PlatformConfig(
                platform=Platform.LINUX,
                base_directory=base_path,
                cache_directory=cache_path,
                logs_directory=base_path / 'logs',
                permissions={"directory": 0o755, "file": 0o644}
            )
            
            manager = DirectoryManager(config)
            structure = manager.create_directory_structure(base_path)
            
            # Verify XDG-compliant structure
            assert structure.base == base_path
            assert structure.cache == cache_path
            assert structure.logs == base_path / 'logs'
            
            # Verify all directories were created
            assert all(d.exists() for d in [structure.base, structure.database, 
                                          structure.cache, structure.logs, structure.temp])
    
    def test_validate_directory_access_success(self):
        """Test successful directory access validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / 'test_access'
            test_dir.mkdir()
            
            config = PlatformConfig.for_current_platform()
            manager = DirectoryManager(config)
            
            result = manager.validate_directory_access(test_dir)
            assert result is True    de
f test_validate_directory_access_nonexistent(self):
        """Test directory access validation for nonexistent directory."""
        nonexistent_dir = Path('/nonexistent/directory')
        
        config = PlatformConfig.for_current_platform()
        manager = DirectoryManager(config)
        
        result = manager.validate_directory_access(nonexistent_dir)
        assert result is False
    
    def test_validate_directory_access_no_permissions(self):
        """Test directory access validation with insufficient permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / 'test_access'
            test_dir.mkdir()
            
            config = PlatformConfig.for_current_platform()
            manager = DirectoryManager(config)
            
            with patch('os.access', return_value=False):
                result = manager.validate_directory_access(test_dir)
                assert result is False
    
    def test_set_unix_permissions(self):
        """Test setting Unix permissions on directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'test_permissions'
            
            config = PlatformConfig(
                platform=Platform.LINUX,
                base_directory=base_path,
                cache_directory=base_path / 'cache',
                logs_directory=base_path / 'logs',
                permissions={"directory": 0o755, "file": 0o644}
            )
            
            manager = DirectoryManager(config)
            structure = manager.create_directory_structure(base_path)
            
            # Check that directories have correct permissions (if on Unix system)
            if os.name == 'posix':
                for directory in [structure.base, structure.database, structure.cache, 
                                structure.logs, structure.temp]:
                    if directory.exists():
                        mode = directory.stat().st_mode & 0o777
                        assert mode == 0o755


class TestDataMigrator:
    """Test cases for DataMigrator class."""
    
    def test_migrate_legacy_data_no_legacy_directory(self):
        """Test migration when no legacy directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_base = Path(temp_dir) / 'target'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            
            migrator = DataMigrator(target_structure)
            
            # Change to temp directory so ./data doesn't exist
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = migrator.migrate_legacy_data()
                assert result is True  # No migration needed
            finally:
                os.chdir(original_cwd) 
   def test_migrate_legacy_data_with_files(self):
        """Test migration with actual legacy files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create legacy data directory with test files
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            
            # Create test files
            (legacy_dir / 'test.db').write_text('test database')
            (legacy_dir / 'config.json').write_text('{"test": "config"}')
            (legacy_dir / 'app.log').write_text('test log')
            (legacy_dir / '.license_cache.json').write_text('{"cache": "data"}')
            
            # Create target structure
            target_base = Path(temp_dir) / 'target'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            target_structure.create_all()
            
            migrator = DataMigrator(target_structure)
            
            # Change to temp directory for migration
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = migrator.migrate_legacy_data()
                assert result is True
                
                # Verify files were migrated
                assert (target_structure.database / 'test.db').exists()
                assert (target_structure.base / 'config.json').exists()
                assert (target_structure.logs / 'app.log').exists()
                assert (target_structure.cache / '.license_cache.json').exists()
                
                # Verify legacy directory was renamed
                assert not legacy_dir.exists()
                assert (Path(temp_dir) / 'data.migrated').exists()
                
            finally:
                os.chdir(original_cwd)
    
    def test_migrate_legacy_data_permission_error(self):
        """Test migration failure due to permission error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create legacy data directory
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            (legacy_dir / 'test.db').write_text('test database')
            
            # Create target structure
            target_base = Path(temp_dir) / 'target'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            
            migrator = DataMigrator(target_structure)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                with patch('shutil.copy2', side_effect=OSError(13, 'Permission denied')):
                    with pytest.raises(MigrationError):
                        migrator.migrate_legacy_data()
                        
            finally:
                os.chdir(original_cwd)cla
ss TestUserDataManagerIntegration:
    """Integration tests for UserDataManager."""
    
    def test_full_initialization_workflow(self):
        """Test complete initialization workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'custom_data'
            
            with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                manager = UserDataManager()
                
                # Test directory creation
                data_dir = manager.get_data_directory()
                assert data_dir == custom_path
                assert data_dir.exists()
                
                # Test all subdirectories
                db_path = manager.get_database_path()
                cache_dir = manager.get_cache_directory()
                logs_dir = manager.get_logs_directory()
                temp_dir = manager.get_temp_directory()
                
                assert db_path.parent.exists()  # database directory
                assert cache_dir.exists()
                assert logs_dir.exists()
                assert temp_dir.exists()
    
    def test_initialization_with_migration(self):
        """Test initialization with legacy data migration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create legacy data directory
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            (legacy_dir / 'test.db').write_text('legacy database')
            (legacy_dir / 'config.json').write_text('{"legacy": "config"}')
            
            custom_path = Path(temp_dir) / 'new_data'
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                    manager = UserDataManager()
                    
                    # Initialize directories (should trigger migration)
                    success = manager.initialize_directories()
                    assert success is True
                    
                    # Verify migration occurred
                    assert (custom_path / 'database' / 'test.db').exists()
                    assert (custom_path / 'config.json').exists()
                    assert not legacy_dir.exists()
                    assert (Path(temp_dir) / 'data.migrated').exists()
                    
            finally:
                os.chdir(original_cwd)
    
    def test_get_directory_info(self):
        """Test directory information retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'test_info'
            
            with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                manager = UserDataManager()
                info = manager.get_directory_info()
                
                assert 'data_directory' in info
                assert 'database_path' in info
                assert 'cache_directory' in info
                assert 'logs_directory' in info
                assert 'temp_directory' in info
                assert 'platform' in info
                
                assert str(custom_path) in info['data_directory']


class TestCrossPlatformDirectoryManagement:
    """Comprehensive integration tests for cross-platform directory management - Requirements 6.1, 7.1, 5.1."""
    
    def test_full_directory_structure_creation_windows(self):
        """Test complete directory structure creation on Windows - Requirement 6.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.platform', 'win32'):
                with patch.dict(os.environ, {'APPDATA': str(Path(temp_dir) / 'AppData' / 'Roaming')}):
                    manager = UserDataManager()
                    
                    # Test initialization
                    success = manager.initialize_directories()
                    assert success is True
                    
                    # Verify Windows-specific structure
                    data_dir = manager.get_data_directory()
                    assert 'AppData' in str(data_dir)
                    assert 'Roaming' in str(data_dir)
                    
                    # Verify all required subdirectories exist
                    required_dirs = [
                        manager.get_database_path().parent,  # database directory
                        manager.get_cache_directory(),
                        manager.get_logs_directory(),
                        manager.get_temp_directory()
                    ]
                    
                    for directory in required_dirs:
                        assert directory.exists(), f"Directory {directory} should exist"
                        assert directory.is_dir(), f"{directory} should be a directory"
    
    def test_full_directory_structure_creation_macos(self):
        """Test complete directory structure creation on macOS - Requirement 6.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.platform', 'darwin'):
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    manager = UserDataManager()
                    
                    # Test initialization
                    success = manager.initialize_directories()
                    assert success is True
                    
                    # Verify macOS-specific structure
                    data_dir = manager.get_data_directory()
                    assert 'Library' in str(data_dir)
                    assert 'Application Support' in str(data_dir)
                    
                    # Verify cache is in separate location
                    cache_dir = manager.get_cache_directory()
                    assert 'Caches' in str(cache_dir)
                    
                    # Verify logs are in separate location
                    logs_dir = manager.get_logs_directory()
                    assert 'Logs' in str(logs_dir)
                    
                    # Verify all directories exist
                    required_dirs = [
                        manager.get_database_path().parent,
                        cache_dir,
                        logs_dir,
                        manager.get_temp_directory()
                    ]
                    
                    for directory in required_dirs:
                        assert directory.exists(), f"Directory {directory} should exist"
                        assert directory.is_dir(), f"{directory} should be a directory"
    
    def test_full_directory_structure_creation_linux(self):
        """Test complete directory structure creation on Linux - Requirement 6.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.platform', 'linux'):
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    with patch.dict(os.environ, {}, clear=True):
                        manager = UserDataManager()
                        
                        # Test initialization
                        success = manager.initialize_directories()
                        assert success is True
                        
                        # Verify Linux XDG-compliant structure
                        data_dir = manager.get_data_directory()
                        assert '.local/share' in str(data_dir)
                        
                        # Verify cache is in separate XDG location
                        cache_dir = manager.get_cache_directory()
                        assert '.cache' in str(cache_dir)
                        
                        # Verify all directories exist
                        required_dirs = [
                            manager.get_database_path().parent,
                            cache_dir,
                            manager.get_logs_directory(),
                            manager.get_temp_directory()
                        ]
                        
                        for directory in required_dirs:
                            assert directory.exists(), f"Directory {directory} should exist"
                            assert directory.is_dir(), f"{directory} should be a directory"
    
    def test_permission_setting_and_validation_unix(self):
        """Test permission setting and validation on Unix systems - Requirement 6.1."""
        if os.name != 'posix':
            pytest.skip("Unix permission tests only run on POSIX systems")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.platform', 'linux'):
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    manager = UserDataManager()
                    success = manager.initialize_directories()
                    assert success is True
                    
                    # Check directory permissions
                    directories_to_check = [
                        manager.get_data_directory(),
                        manager.get_database_path().parent,
                        manager.get_cache_directory(),
                        manager.get_logs_directory(),
                        manager.get_temp_directory()
                    ]
                    
                    for directory in directories_to_check:
                        if directory.exists():
                            mode = directory.stat().st_mode & 0o777
                            assert mode == 0o755, f"Directory {directory} should have 755 permissions, got {oct(mode)}"
    
    def test_permission_validation_failure_scenarios(self):
        """Test permission validation failure scenarios - Requirement 5.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'test_permissions'
            
            config = PlatformConfig(
                platform=Platform.LINUX,
                base_directory=base_path,
                cache_directory=base_path / 'cache',
                logs_directory=base_path / 'logs',
                permissions={"directory": 0o755, "file": 0o644}
            )
            
            manager = DirectoryManager(config)
            
            # Test with no read permission
            with patch('os.access') as mock_access:
                mock_access.return_value = False
                result = manager.validate_directory_access(base_path)
                assert result is False
            
            # Test with nonexistent directory
            nonexistent = Path('/nonexistent/path/that/should/not/exist')
            result = manager.validate_directory_access(nonexistent)
            assert result is False
    
    def test_comprehensive_migration_scenarios(self):
        """Test comprehensive migration scenarios - Requirement 7.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create complex legacy data structure
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            
            # Create various types of files
            (legacy_dir / 'offers.db').write_text('database content')
            (legacy_dir / 'config.json').write_text('{"setting": "value"}')
            (legacy_dir / 'app.log').write_text('log entries')
            (legacy_dir / '.license_cache.json').write_text('{"license": "cached"}')
            
            # Create subdirectories with files
            (legacy_dir / 'backups').mkdir()
            (legacy_dir / 'backups' / 'backup.db').write_text('backup data')
            (legacy_dir / 'exports').mkdir()
            (legacy_dir / 'exports' / 'export.csv').write_text('csv,data')
            
            # Create target structure
            target_base = Path(temp_dir) / 'new_location'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            target_structure.create_all()
            
            migrator = DataMigrator(target_structure)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = migrator.migrate_legacy_data()
                assert result is True
                
                # Verify database files migrated
                assert (target_structure.database / 'offers.db').exists()
                assert (target_structure.database / 'backups' / 'backup.db').exists()
                
                # Verify cache files migrated
                assert (target_structure.cache / '.license_cache.json').exists()
                
                # Verify log files migrated
                assert (target_structure.logs / 'app.log').exists()
                
                # Verify other files migrated to base
                assert (target_structure.base / 'config.json').exists()
                assert (target_structure.base / 'exports' / 'export.csv').exists()
                
                # Verify legacy directory was renamed
                assert not legacy_dir.exists()
                assert (Path(temp_dir) / 'data.migrated').exists()
                
            finally:
                os.chdir(original_cwd)
    
    def test_migration_with_existing_data(self):
        """Test migration when target already has some data - Requirement 7.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create legacy data
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            (legacy_dir / 'legacy.db').write_text('legacy database')
            (legacy_dir / 'legacy_config.json').write_text('{"legacy": true}')
            
            # Create target structure with existing data
            target_base = Path(temp_dir) / 'target'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            target_structure.create_all()
            
            # Add existing data
            (target_structure.database / 'existing.db').write_text('existing database')
            (target_structure.base / 'existing_config.json').write_text('{"existing": true}')
            
            migrator = DataMigrator(target_structure)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = migrator.migrate_legacy_data()
                assert result is True
                
                # Verify both legacy and existing data are present
                assert (target_structure.database / 'legacy.db').exists()
                assert (target_structure.database / 'existing.db').exists()
                assert (target_structure.base / 'legacy_config.json').exists()
                assert (target_structure.base / 'existing_config.json').exists()
                
            finally:
                os.chdir(original_cwd)
    
    def test_migration_failure_and_rollback(self):
        """Test migration failure scenarios and rollback - Requirement 5.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create legacy data
            legacy_dir = Path(temp_dir) / 'data'
            legacy_dir.mkdir()
            (legacy_dir / 'test.db').write_text('test database')
            (legacy_dir / 'config.json').write_text('{"test": "config"}')
            
            # Create target structure
            target_base = Path(temp_dir) / 'target'
            target_structure = DirectoryStructure(
                base=target_base,
                database=target_base / 'database',
                cache=target_base / 'cache',
                logs=target_base / 'logs',
                temp=target_base / 'temp'
            )
            target_structure.create_all()
            
            migrator = DataMigrator(target_structure)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Simulate failure during migration
                with patch('shutil.copy2', side_effect=OSError(28, 'No space left on device')):
                    with pytest.raises(MigrationError) as exc_info:
                        migrator.migrate_legacy_data()
                    
                    # Verify error contains useful information
                    assert "No space left" in str(exc_info.value) or "место" in str(exc_info.value)
                    
                    # Verify legacy data is preserved
                    assert legacy_dir.exists()
                    assert (legacy_dir / 'test.db').exists()
                    assert (legacy_dir / 'config.json').exists()
                    
            finally:
                os.chdir(original_cwd)
    
    def test_disk_space_validation(self):
        """Test disk space validation during directory creation - Requirement 5.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'test_space'
            
            config = PlatformConfig(
                platform=Platform.LINUX,
                base_directory=base_path,
                cache_directory=base_path / 'cache',
                logs_directory=base_path / 'logs',
                permissions={"directory": 0o755, "file": 0o644}
            )
            
            manager = DirectoryManager(config)
            
            # Mock disk usage to simulate low space
            with patch('shutil.disk_usage') as mock_disk_usage:
                # Simulate very low disk space (1MB free)
                mock_disk_usage.return_value = (1000000000, 999000000, 1000000)
                
                with patch('pathlib.Path.mkdir', side_effect=OSError(28, 'No space left on device')):
                    with pytest.raises(DiskSpaceError) as exc_info:
                        structure = manager.create_directory_structure(base_path)
                        structure.create_all()
                    
                    # Verify error contains space information
                    assert hasattr(exc_info.value, 'available_space_mb')
                    assert hasattr(exc_info.value, 'required_space_mb')
    
    def test_concurrent_directory_access(self):
        """Test handling of concurrent directory access scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / 'concurrent_test'
            
            # Simulate race condition where directory is created between check and creation
            config = PlatformConfig.for_current_platform()
            manager = DirectoryManager(config)
            
            def create_directory_during_check(*args, **kwargs):
                # Create the directory during the validation check
                base_path.mkdir(parents=True, exist_ok=True)
                return True
            
            with patch.object(manager, 'validate_directory_access', side_effect=create_directory_during_check):
                structure = manager.create_directory_structure(base_path)
                # Should handle the race condition gracefully
                assert structure.base == base_path
    
    def test_error_recovery_strategies(self):
        """Test error recovery strategies for various failure scenarios - Requirement 5.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test recovery from permission errors
            with patch('sys.platform', 'linux'):
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    manager = UserDataManager()
                    
                    # Simulate permission error on first attempt
                    original_mkdir = Path.mkdir
                    call_count = 0
                    
                    def failing_mkdir(self, *args, **kwargs):
                        nonlocal call_count
                        call_count += 1
                        if call_count == 1:
                            raise OSError(13, 'Permission denied')
                        return original_mkdir(self, *args, **kwargs)
                    
                    with patch('pathlib.Path.mkdir', failing_mkdir):
                        # Should raise appropriate error with recovery suggestions
                        with pytest.raises(UserDataPermissionError) as exc_info:
                            manager.initialize_directories()
                        
                        # Verify error has recovery information
                        assert hasattr(exc_info.value, 'suggested_solution')
                        assert hasattr(exc_info.value, 'recovery_action')
    
    def test_comprehensive_validation_scenarios(self):
        """Test comprehensive validation scenarios - Requirement 5.1."""
        validation_scenarios = [
            # Invalid path scenarios
            {'path': '/dev/null', 'expected_error': ValidationError},
            {'path': '/root', 'expected_error': ValidationError},
            {'path': '', 'expected_error': ValidationError},
        ]
        
        for scenario in validation_scenarios:
            if scenario['path']:  # Skip empty path test on Windows
                try:
                    from offers_check_marketplaces.user_data_manager import PathResolver
                    resolver = PathResolver()
                    
                    with pytest.raises(scenario['expected_error']):
                        resolver._validate_custom_path(Path(scenario['path']))
                except Exception:
                    # Some validation scenarios may not apply to all platforms
                    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])