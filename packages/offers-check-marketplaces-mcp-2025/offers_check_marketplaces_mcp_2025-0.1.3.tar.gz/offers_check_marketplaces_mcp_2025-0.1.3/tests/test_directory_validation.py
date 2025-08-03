#!/usr/bin/env python3
"""
Тест валидации доступа к директориям.
"""

import os
import sys
import tempfile
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    DirectoryManager, 
    PlatformConfig
)


def test_directory_validation():
    """Тестирует валидацию доступа к директориям."""
    print("=== ТЕСТ ВАЛИДАЦИИ ДОСТУПА К ДИРЕКТОРИЯМ ===")
    
    config = PlatformConfig.for_current_platform()
    manager = DirectoryManager(config)
    
    # Тест 1: Валидная директория
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir)
        result = manager.validate_directory_access(test_path)
        print(f"Валидная директория {test_path}: {result}")
        assert result == True, "Валидная директория должна пройти проверку"
    
    # Тест 2: Несуществующая директория
    nonexistent_path = Path("/nonexistent/directory/path")
    result = manager.validate_directory_access(nonexistent_path)
    print(f"Несуществующая директория {nonexistent_path}: {result}")
    assert result == False, "Несуществующая директория не должна пройти проверку"
    
    # Тест 3: Файл вместо директории
    with tempfile.NamedTemporaryFile() as temp_file:
        file_path = Path(temp_file.name)
        result = manager.validate_directory_access(file_path)
        print(f"Файл вместо директории {file_path}: {result}")
        assert result == False, "Файл не должен пройти проверку как директория"
    
    print("✅ Все тесты валидации пройдены")
    return True


if __name__ == "__main__":
    test_directory_validation()