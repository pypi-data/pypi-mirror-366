# Design Document

## Overview

Система управления пользовательскими данными для MCP сервера offers-check-marketplaces, которая автоматически определяет и создает подходящие директории для каждой операционной системы в соответствии с их стандартами.

## Architecture

### Core Components

1. **UserDataManager** - основной класс для управления пользовательскими данными
2. **PlatformDetector** - определение операционной системы и стандартных путей
3. **DirectoryManager** - создание и управление структурой директорий
4. **DataMigrator** - миграция существующих данных из старых расположений
5. **PathResolver** - разрешение путей с учетом переменных окружения

### Platform-Specific Paths

#### Windows

- Base: `%APPDATA%/offers-check-marketplaces/`
- Database: `%APPDATA%/offers-check-marketplaces/database/`
- Cache: `%APPDATA%/offers-check-marketplaces/cache/`
- Logs: `%APPDATA%/offers-check-marketplaces/logs/`

#### macOS

- Base: `~/Library/Application Support/offers-check-marketplaces/`
- Database: `~/Library/Application Support/offers-check-marketplaces/database/`
- Cache: `~/Library/Caches/offers-check-marketplaces/`
- Logs: `~/Library/Logs/offers-check-marketplaces/`

#### Linux

- Base: `~/.local/share/offers-check-marketplaces/` (или `$XDG_DATA_HOME/offers-check-marketplaces/`)
- Database: `~/.local/share/offers-check-marketplaces/database/`
- Cache: `~/.cache/offers-check-marketplaces/` (или `$XDG_CACHE_HOME/offers-check-marketplaces/`)
- Logs: `~/.local/share/offers-check-marketplaces/logs/`

## Components and Interfaces

### UserDataManager Class

```python
class UserDataManager:
    def __init__(self):
        self.platform_detector = PlatformDetector()
        self.directory_manager = DirectoryManager()
        self.data_migrator = DataMigrator()
        self.path_resolver = PathResolver()

    def get_data_directory(self) -> Path
    def get_database_path(self) -> Path
    def get_cache_directory(self) -> Path
    def get_logs_directory(self) -> Path
    def initialize_directories(self) -> bool
    def migrate_legacy_data(self) -> bool
```

### PlatformDetector Class

```python
class PlatformDetector:
    def get_platform(self) -> str  # 'windows', 'macos', 'linux'
    def get_user_data_dir(self) -> Path
    def get_user_cache_dir(self) -> Path
    def get_user_logs_dir(self) -> Path
    def supports_xdg_base_directory(self) -> bool
```

### DirectoryManager Class

```python
class DirectoryManager:
    def create_directory_structure(self, base_path: Path) -> bool
    def ensure_directory_exists(self, path: Path) -> bool
    def set_directory_permissions(self, path: Path, platform: str) -> bool
    def validate_directory_access(self, path: Path) -> bool
```

## Data Models

### DirectoryStructure

```python
@dataclass
class DirectoryStructure:
    base: Path
    database: Path
    cache: Path
    logs: Path
    temp: Path

    def validate(self) -> bool
    def create_all(self) -> bool
```

### PlatformConfig

```python
@dataclass
class PlatformConfig:
    platform: str
    base_directory: Path
    cache_directory: Path
    logs_directory: Path
    permissions: Dict[str, int]

    @classmethod
    def for_current_platform(cls) -> 'PlatformConfig'
```

## Error Handling

### Exception Hierarchy

```python
class UserDataError(Exception):
    """Base exception for user data operations"""
    pass

class DirectoryCreationError(UserDataError):
    """Raised when directory creation fails"""
    pass

class PermissionError(UserDataError):
    """Raised when insufficient permissions"""
    pass

class MigrationError(UserDataError):
    """Raised when data migration fails"""
    pass
```

### Error Recovery Strategies

1. **Directory Creation Failure**

   - Try alternative locations
   - Fallback to temporary directory
   - Provide clear user instructions

2. **Permission Issues**

   - Suggest permission fixes
   - Try with reduced permissions
   - Fallback to read-only mode

3. **Migration Failures**
   - Preserve original data
   - Partial migration support
   - Detailed error reporting

## Testing Strategy

### Unit Tests

- Platform detection accuracy
- Directory creation logic
- Permission handling
- Path resolution with environment variables

### Integration Tests

- Full initialization flow
- Cross-platform compatibility
- Migration scenarios
- Error handling paths

### Platform-Specific Tests

- Windows: APPDATA handling
- macOS: Application Support structure
- Linux: XDG Base Directory compliance

## Security Considerations

1. **File Permissions**

   - Restrict access to user only (700/755)
   - Validate directory ownership
   - Prevent symlink attacks

2. **Path Validation**

   - Sanitize user-provided paths
   - Prevent directory traversal
   - Validate environment variables

3. **Data Protection**
   - Secure database file permissions
   - Encrypted sensitive data storage
   - Safe temporary file handling
