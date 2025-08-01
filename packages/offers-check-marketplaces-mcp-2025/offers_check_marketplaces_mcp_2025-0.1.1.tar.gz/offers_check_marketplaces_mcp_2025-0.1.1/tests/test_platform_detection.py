#!/usr/bin/env python3
"""
Unit tests for platform detection and path resolution.
Tests PlatformDetector on different operating systems and environment variable scenarios.
Comprehensive test coverage for Requirements 1.1, 2.1, 3.1, 4.1.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add path to module
sys.path.insert(0, str(Path(__file__).parent.parent))

from offers_check_marketplaces.user_data_manager import (
    PlatformDetector,
    Platform,
    PathResolver,
    PlatformConfig,
    ValidationError,
    PermissionError as UserDataPermissionError,
    DirectoryCreationError,
    UserDataManager
)


class TestPlatformDetector:
    """Test cases for PlatformDetector class."""
    
    def test_get_platform_windows(self):
        """Test platform detection for Windows."""
        with patch('sys.platform', 'win32'):
            detector = PlatformDetector()
            platform = detector.get_platform()
            assert platform == Platform.WINDOWS
    
    def test_get_platform_macos(self):
        """Test platform detection for macOS."""
        with patch('sys.platform', 'darwin'):
            detector = PlatformDetector()
            platform = detector.get_platform()
            assert platform == Platform.MACOS
    
    def test_get_platform_linux(self):
        """Test platform detection for Linux."""
        with patch('sys.platform', 'linux'):
            detector = PlatformDetector()
            platform = detector.get_platform()
            assert platform == Platform.LINUX
    
    def test_get_platform_unknown(self):
        """Test platform detection for unknown systems."""
        with patch('sys.platform', 'freebsd'):
            detector = PlatformDetector()
            platform = detector.get_platform()
            assert platform == Platform.UNKNOWN
    
    def test_get_platform_edge_cases(self):
        """Test platform detection for edge cases and variations."""
        # Test Windows variations
        for win_platform in ['win32', 'win64', 'windows']:
            with patch('sys.platform', win_platform):
                detector = PlatformDetector()
                platform = detector.get_platform()
                if win_platform.startswith('win'):
                    assert platform == Platform.WINDOWS
                else:
                    assert platform == Platform.UNKNOWN
        
        # Test Linux variations
        for linux_platform in ['linux', 'linux2', 'linux3']:
            with patch('sys.platform', linux_platform):
                detector = PlatformDetector()
                platform = detector.get_platform()
                assert platform == Platform.LINUX
        
        # Test other Unix-like systems
        for unix_platform in ['freebsd', 'openbsd', 'netbsd', 'sunos5']:
            with patch('sys.platform', unix_platform):
                detector = PlatformDetector()
                platform = detector.get_platform()
                assert platform == Platform.UNKNOWN
    
    def test_get_user_data_dir_windows(self):
        """Test Windows APPDATA directory resolution."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}):
                detector = PlatformDetector()
                data_dir = detector.get_user_data_dir()
                assert data_dir == Path('C:\\Users\\Test\\AppData\\Roaming')
    
    def test_get_user_data_dir_windows_fallback(self):
        """Test Windows fallback when APPDATA is not available."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('pathlib.Path.home', return_value=Path('C:\\Users\\Test')):
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    expected = Path('C:\\Users\\Test\\AppData\\Roaming')
                    assert data_dir == expected
    
    def test_get_user_data_dir_windows_userprofile_fallback(self):
        """Test Windows USERPROFILE fallback when APPDATA is not available."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'USERPROFILE': 'C:\\Users\\TestUser'}, clear=True):
                with patch('pathlib.Path.exists') as mock_exists:
                    # Mock that the AppData/Roaming directory exists
                    mock_exists.return_value = True
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    expected = Path('C:\\Users\\TestUser\\AppData\\Roaming')
                    assert data_dir == expected
    
    def test_get_user_data_dir_windows_homedrive_fallback(self):
        """Test Windows HOMEDRIVE/HOMEPATH fallback."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {
                'HOMEDRIVE': 'D:',
                'HOMEPATH': '\\Users\\TestUser'
            }, clear=True):
                with patch('pathlib.Path.exists') as mock_exists:
                    mock_exists.return_value = True
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    expected = Path('D:\\Users\\TestUser\\AppData\\Roaming')
                    assert data_dir == expected
    
    def test_get_user_data_dir_windows_nonexistent_appdata(self):
        """Test Windows behavior when APPDATA path doesn't exist."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'APPDATA': 'C:\\NonExistent\\AppData\\Roaming'}):
                with patch('pathlib.Path.exists', return_value=False):
                    with patch('pathlib.Path.home', return_value=Path('C:\\Users\\Test')):
                        detector = PlatformDetector()
                        data_dir = detector.get_user_data_dir()
                        # Should fallback to home-based path
                        expected = Path('C:\\Users\\Test\\AppData\\Roaming')
                        assert data_dir == expected
    
    def test_get_user_data_dir_macos(self):
        """Test macOS Application Support directory."""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.home', return_value=Path('/Users/test')):
                detector = PlatformDetector()
                data_dir = detector.get_user_data_dir()
                expected = Path('/Users/test/Library/Application Support')
                assert data_dir == expected
    
    def test_get_user_data_dir_linux_xdg(self):
        """Test Linux XDG_DATA_HOME environment variable."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {'XDG_DATA_HOME': '/home/test/.local/share'}):
                detector = PlatformDetector()
                data_dir = detector.get_user_data_dir()
                assert data_dir == Path('/home/test/.local/share')
    
    def test_get_user_data_dir_linux_fallback(self):
        """Test Linux fallback to ~/.local/share."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('pathlib.Path.home', return_value=Path('/home/test')):
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    expected = Path('/home/test/.local/share')
                    assert data_dir == expected
    
    def test_get_user_data_dir_linux_xdg_variations(self):
        """Test Linux XDG_DATA_HOME with various path formats."""
        test_cases = [
            '/home/user/.local/share',
            '/custom/data/location',
            '/tmp/test-data',
            '~/custom-data',  # Should be expanded
        ]
        
        with patch('sys.platform', 'linux'):
            for xdg_path in test_cases:
                with patch.dict(os.environ, {'XDG_DATA_HOME': xdg_path}):
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    assert data_dir == Path(xdg_path)
    
    def test_get_user_data_dir_linux_empty_xdg(self):
        """Test Linux behavior when XDG_DATA_HOME is empty string."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {'XDG_DATA_HOME': ''}):
                with patch('pathlib.Path.home', return_value=Path('/home/test')):
                    detector = PlatformDetector()
                    data_dir = detector.get_user_data_dir()
                    expected = Path('/home/test/.local/share')
                    assert data_dir == expected
    
    def test_get_user_cache_dir_windows(self):
        """Test Windows cache directory resolution."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'}):
                detector = PlatformDetector()
                cache_dir = detector.get_user_cache_dir()
                assert cache_dir == Path('C:\\Users\\Test\\AppData\\Local')
    
    def test_get_user_cache_dir_macos(self):
        """Test macOS cache directory."""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.home', return_value=Path('/Users/test')):
                detector = PlatformDetector()
                cache_dir = detector.get_user_cache_dir()
                expected = Path('/Users/test/Library/Caches')
                assert cache_dir == expected
    
    def test_get_user_cache_dir_linux_xdg(self):
        """Test Linux XDG_CACHE_HOME environment variable."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {'XDG_CACHE_HOME': '/home/test/.cache'}):
                detector = PlatformDetector()
                cache_dir = detector.get_user_cache_dir()
                assert cache_dir == Path('/home/test/.cache')
    
    def test_get_user_cache_dir_linux_fallback(self):
        """Test Linux cache fallback to ~/.cache."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('pathlib.Path.home', return_value=Path('/home/test')):
                    detector = PlatformDetector()
                    cache_dir = detector.get_user_cache_dir()
                    expected = Path('/home/test/.cache')
                    assert cache_dir == expected
    
    def test_get_user_cache_dir_windows_localappdata_fallback(self):
        """Test Windows LOCALAPPDATA fallback when not available."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('pathlib.Path.home', return_value=Path('C:\\Users\\Test')):
                    detector = PlatformDetector()
                    cache_dir = detector.get_user_cache_dir()
                    # Should fallback to APPDATA equivalent
                    expected = Path('C:\\Users\\Test\\AppData\\Roaming')
                    assert cache_dir == expected
    
    def test_get_user_cache_dir_windows_nonexistent_localappdata(self):
        """Test Windows cache directory when LOCALAPPDATA doesn't exist."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\NonExistent\\Local'}):
                with patch('pathlib.Path.exists', return_value=False):
                    with patch('pathlib.Path.home', return_value=Path('C:\\Users\\Test')):
                        detector = PlatformDetector()
                        cache_dir = detector.get_user_cache_dir()
                        # Should fallback to APPDATA equivalent
                        expected = Path('C:\\Users\\Test\\AppData\\Roaming')
                        assert cache_dir == expected
    
    def test_supports_xdg_base_directory(self):
        """Test XDG Base Directory support detection."""
        with patch('sys.platform', 'linux'):
            detector = PlatformDetector()
            assert detector.supports_xdg_base_directory() is True
        
        with patch('sys.platform', 'win32'):
            detector = PlatformDetector()
            assert detector.supports_xdg_base_directory() is False
class TestPathResolver:
    """Test cases for PathResolver class."""
    
    def test_resolve_data_directory_default(self):
        """Test default data directory resolution."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/test')):
                with patch.dict(os.environ, {}, clear=True):
                    resolver = PathResolver()
                    data_dir = resolver.resolve_data_directory()
                    expected = Path('/home/test/.local/share/offers-check-marketplaces')
                    assert data_dir == expected
    
    def test_resolve_data_directory_custom_env(self):
        """Test custom data directory from OFFERS_CHECK_DATA_DIR."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'custom_data'
            custom_path.mkdir(parents=True, exist_ok=True)
            
            with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                resolver = PathResolver()
                data_dir = resolver.resolve_data_directory()
                assert data_dir == custom_path
    
    def test_resolve_data_directory_custom_env_all_platforms(self):
        """Test OFFERS_CHECK_DATA_DIR override on all platforms - Requirement 4.1."""
        platforms = [
            ('win32', Platform.WINDOWS),
            ('darwin', Platform.MACOS),
            ('linux', Platform.LINUX),
            ('freebsd', Platform.UNKNOWN)
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'custom_offers_data'
            custom_path.mkdir(parents=True, exist_ok=True)
            
            for sys_platform, expected_platform in platforms:
                with patch('sys.platform', sys_platform):
                    with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                        resolver = PathResolver()
                        data_dir = resolver.resolve_data_directory()
                        assert data_dir == custom_path, f"Failed for platform {sys_platform}"
    
    def test_resolve_data_directory_custom_env_relative_path(self):
        """Test OFFERS_CHECK_DATA_DIR with relative path - Requirement 4.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to test relative paths
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                relative_path = Path('relative_data')
                relative_path.mkdir(exist_ok=True)
                
                with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(relative_path)}):
                    resolver = PathResolver()
                    data_dir = resolver.resolve_data_directory()
                    # Should resolve to absolute path
                    assert data_dir.is_absolute()
                    assert data_dir.name == 'relative_data'
            finally:
                os.chdir(original_cwd)
    
    def test_resolve_data_directory_custom_env_nonexistent_creates_directory(self):
        """Test that OFFERS_CHECK_DATA_DIR creates directory if it doesn't exist - Requirement 4.2."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'nonexistent' / 'nested' / 'path'
            
            with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                resolver = PathResolver()
                data_dir = resolver.resolve_data_directory()
                assert data_dir == custom_path
                assert custom_path.exists()
                assert custom_path.is_dir()
    
    def test_resolve_data_directory_custom_env_empty_string(self):
        """Test OFFERS_CHECK_DATA_DIR with empty string falls back to default - Requirement 4.1."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/test')):
                with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': ''}):
                    resolver = PathResolver()
                    data_dir = resolver.resolve_data_directory()
                    expected = Path('/home/test/.local/share/offers-check-marketplaces')
                    assert data_dir == expected
    
    def test_resolve_data_directory_custom_env_whitespace_only(self):
        """Test OFFERS_CHECK_DATA_DIR with whitespace-only string falls back to default."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/test')):
                with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': '   \t\n  '}):
                    resolver = PathResolver()
                    data_dir = resolver.resolve_data_directory()
                    expected = Path('/home/test/.local/share/offers-check-marketplaces')
                    assert data_dir == expected
    
    def test_resolve_custom_path_expanduser(self):
        """Test custom path expansion with ~ character."""
        with patch('pathlib.Path.home', return_value=Path('/home/test')):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a test directory structure
                test_home = Path(temp_dir) / 'home' / 'test'
                test_home.mkdir(parents=True, exist_ok=True)
                custom_dir = test_home / 'custom_data'
                
                with patch('pathlib.Path.expanduser') as mock_expand:
                    mock_expand.return_value = custom_dir
                    with patch('pathlib.Path.resolve') as mock_resolve:
                        mock_resolve.return_value = custom_dir
                        with patch('pathlib.Path.exists') as mock_exists:
                            mock_exists.return_value = False
                            with patch('pathlib.Path.mkdir') as mock_mkdir:
                                with patch('os.access', return_value=True):
                                    resolver = PathResolver()
                                    result = resolver._resolve_custom_path('~/custom_data')
                                    mock_expand.assert_called_once()
                                    assert result == custom_dir
    
    def test_validate_custom_path_file_error(self):
        """Test validation error when custom path is a file."""
        with tempfile.NamedTemporaryFile() as temp_file:
            resolver = PathResolver()
            with pytest.raises(ValidationError) as exc_info:
                resolver._validate_custom_path(Path(temp_file.name))
            assert "является файлом" in str(exc_info.value)
    
    def test_validate_custom_path_system_directory(self):
        """Test validation error for system directories."""
        resolver = PathResolver()
        with pytest.raises(ValidationError) as exc_info:
            resolver._validate_custom_path(Path('/'))
        assert "системную директорию" in str(exc_info.value)
    
    def test_validate_custom_path_nonexistent_parent(self):
        """Test validation error when parent directory doesn't exist."""
        resolver = PathResolver()
        nonexistent_path = Path('/nonexistent/parent/child')
        with pytest.raises(ValidationError) as exc_info:
            resolver._validate_custom_path(nonexistent_path)
        assert "не существует" in str(exc_info.value)
    
    def test_validate_custom_path_no_write_permission(self):
        """Test validation error when no write permission to parent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            parent_dir = Path(temp_dir)
            child_path = parent_dir / 'child'
            
            with patch('os.access', return_value=False):
                resolver = PathResolver()
                with pytest.raises(UserDataPermissionError) as exc_info:
                    resolver._validate_custom_path(child_path)
                assert "Нет прав на запись" in str(exc_info.value)


class TestPlatformConfig:
    """Test cases for PlatformConfig class."""
    
    def test_for_current_platform_windows(self):
        """Test PlatformConfig creation for Windows."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}):
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.WINDOWS
                expected_base = Path('C:\\Users\\Test\\AppData\\Roaming\\offers-check-marketplaces')
                assert config.base_directory == expected_base
                assert config.permissions == {}  # Windows uses default permissions    def t
est_for_current_platform_macos(self):
        """Test PlatformConfig creation for macOS."""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.home', return_value=Path('/Users/test')):
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.MACOS
                expected_base = Path('/Users/test/Library/Application Support/offers-check-marketplaces')
                assert config.base_directory == expected_base
                expected_cache = Path('/Users/test/Library/Caches/offers-check-marketplaces')
                assert config.cache_directory == expected_cache
                expected_logs = Path('/Users/test/Library/Logs/offers-check-marketplaces')
                assert config.logs_directory == expected_logs
                assert config.permissions == {"directory": 0o755, "file": 0o644}
    
    def test_for_current_platform_linux(self):
        """Test PlatformConfig creation for Linux."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/test')):
                with patch.dict(os.environ, {}, clear=True):
                    config = PlatformConfig.for_current_platform()
                    assert config.platform == Platform.LINUX
                    expected_base = Path('/home/test/.local/share/offers-check-marketplaces')
                    assert config.base_directory == expected_base
                    expected_cache = Path('/home/test/.cache/offers-check-marketplaces')
                    assert config.cache_directory == expected_cache
                    assert config.permissions == {"directory": 0o755, "file": 0o644}
    
    def test_for_current_platform_unknown(self):
        """Test PlatformConfig creation for unknown platform."""
        with patch('sys.platform', 'unknown'):
            with patch('pathlib.Path.home', return_value=Path('/home/test')):
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.UNKNOWN
                expected_base = Path('/home/test/.offers-check-marketplaces')
                assert config.base_directory == expected_base
    
    def test_for_current_platform_linux_with_xdg_vars(self):
        """Test Linux PlatformConfig with XDG environment variables - Requirement 3.2."""
        with patch('sys.platform', 'linux'):
            with patch.dict(os.environ, {
                'XDG_DATA_HOME': '/custom/data',
                'XDG_CACHE_HOME': '/custom/cache'
            }):
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.LINUX
                expected_base = Path('/custom/data/offers-check-marketplaces')
                assert config.base_directory == expected_base
                expected_cache = Path('/custom/cache/offers-check-marketplaces')
                assert config.cache_directory == expected_cache
                assert config.permissions == {"directory": 0o755, "file": 0o644}
    
    def test_for_current_platform_windows_missing_appdata(self):
        """Test Windows PlatformConfig when APPDATA is missing - Requirement 1.2."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('pathlib.Path.home', return_value=Path('C:\\Users\\TestUser')):
                    config = PlatformConfig.for_current_platform()
                    assert config.platform == Platform.WINDOWS
                    expected_base = Path('C:\\Users\\TestUser\\AppData\\Roaming\\offers-check-marketplaces')
                    assert config.base_directory == expected_base
                    assert config.permissions == {}  # Windows uses default permissions


class TestCrossPlatformIntegration:
    """Integration tests for cross-platform compatibility - Requirements 1.1, 2.1, 3.1, 4.1."""
    
    def test_full_platform_detection_and_path_resolution_windows(self):
        """Test complete Windows platform detection and path resolution - Requirement 1.1."""
        with patch('sys.platform', 'win32'):
            with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\TestUser\\AppData\\Roaming'}):
                # Test platform detection
                detector = PlatformDetector()
                assert detector.get_platform() == Platform.WINDOWS
                
                # Test path resolution
                resolver = PathResolver()
                data_dir = resolver.resolve_data_directory()
                expected = Path('C:\\Users\\TestUser\\AppData\\Roaming\\offers-check-marketplaces')
                assert data_dir == expected
                
                # Test platform config
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.WINDOWS
                assert config.base_directory == expected
    
    def test_full_platform_detection_and_path_resolution_macos(self):
        """Test complete macOS platform detection and path resolution - Requirement 2.1."""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.home', return_value=Path('/Users/testuser')):
                # Test platform detection
                detector = PlatformDetector()
                assert detector.get_platform() == Platform.MACOS
                
                # Test path resolution
                resolver = PathResolver()
                data_dir = resolver.resolve_data_directory()
                expected = Path('/Users/testuser/Library/Application Support/offers-check-marketplaces')
                assert data_dir == expected
                
                # Test platform config
                config = PlatformConfig.for_current_platform()
                assert config.platform == Platform.MACOS
                assert config.base_directory == expected
                assert config.cache_directory == Path('/Users/testuser/Library/Caches/offers-check-marketplaces')
                assert config.logs_directory == Path('/Users/testuser/Library/Logs/offers-check-marketplaces')
    
    def test_full_platform_detection_and_path_resolution_linux(self):
        """Test complete Linux platform detection and path resolution - Requirement 3.1."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/testuser')):
                with patch.dict(os.environ, {}, clear=True):
                    # Test platform detection
                    detector = PlatformDetector()
                    assert detector.get_platform() == Platform.LINUX
                    
                    # Test path resolution
                    resolver = PathResolver()
                    data_dir = resolver.resolve_data_directory()
                    expected = Path('/home/testuser/.local/share/offers-check-marketplaces')
                    assert data_dir == expected
                    
                    # Test platform config
                    config = PlatformConfig.for_current_platform()
                    assert config.platform == Platform.LINUX
                    assert config.base_directory == expected
                    assert config.cache_directory == Path('/home/testuser/.cache/offers-check-marketplaces')
    
    def test_environment_variable_override_all_platforms(self):
        """Test OFFERS_CHECK_DATA_DIR override works on all platforms - Requirement 4.1."""
        platforms = ['win32', 'darwin', 'linux', 'freebsd']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / 'custom_data_dir'
            custom_path.mkdir(exist_ok=True)
            
            for platform in platforms:
                with patch('sys.platform', platform):
                    with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': str(custom_path)}):
                        # Test that PathResolver respects the environment variable
                        resolver = PathResolver()
                        data_dir = resolver.resolve_data_directory()
                        assert data_dir == custom_path, f"Failed for platform {platform}"
                        
                        # Test that UserDataManager also respects it
                        manager = UserDataManager()
                        manager_data_dir = manager.get_data_directory()
                        assert manager_data_dir == custom_path, f"UserDataManager failed for platform {platform}"
    
    def test_xdg_base_directory_compliance(self):
        """Test XDG Base Directory specification compliance - Requirement 3.2, 3.3."""
        xdg_scenarios = [
            # Standard XDG variables
            {'XDG_DATA_HOME': '/home/user/.local/share', 'XDG_CACHE_HOME': '/home/user/.cache'},
            # Custom XDG variables
            {'XDG_DATA_HOME': '/custom/data', 'XDG_CACHE_HOME': '/custom/cache'},
            # Only data home set
            {'XDG_DATA_HOME': '/custom/data'},
            # Only cache home set
            {'XDG_CACHE_HOME': '/custom/cache'},
        ]
        
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home', return_value=Path('/home/user')):
                for scenario in xdg_scenarios:
                    with patch.dict(os.environ, scenario, clear=True):
                        detector = PlatformDetector()
                        
                        # Test data directory
                        data_dir = detector.get_user_data_dir()
                        if 'XDG_DATA_HOME' in scenario:
                            assert data_dir == Path(scenario['XDG_DATA_HOME'])
                        else:
                            assert data_dir == Path('/home/user/.local/share')
                        
                        # Test cache directory
                        cache_dir = detector.get_user_cache_dir()
                        if 'XDG_CACHE_HOME' in scenario:
                            assert cache_dir == Path(scenario['XDG_CACHE_HOME'])
                        else:
                            assert cache_dir == Path('/home/user/.cache')
    
    def test_error_handling_invalid_custom_paths(self):
        """Test error handling for invalid OFFERS_CHECK_DATA_DIR values - Requirement 4.3."""
        invalid_paths = [
            '/root',  # System directory
            '/dev/null',  # Special file
            '/nonexistent/deeply/nested/path/that/cannot/be/created',  # Uncreateable path
        ]
        
        for invalid_path in invalid_paths:
            with patch.dict(os.environ, {'OFFERS_CHECK_DATA_DIR': invalid_path}):
                resolver = PathResolver()
                # Should either raise an appropriate exception or fallback gracefully
                try:
                    data_dir = resolver.resolve_data_directory()
                    # If it doesn't raise an exception, it should fallback to a valid path
                    assert data_dir != Path(invalid_path)
                except (ValidationError, UserDataPermissionError, DirectoryCreationError):
                    # These are expected exceptions for invalid paths
                    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])