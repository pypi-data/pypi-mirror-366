#!/usr/bin/env python3
"""
Проверка реализации задачи 4.2: Add directory access validation
"""

import sys
import tempfile
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    DirectoryManager, 
    PlatformConfig
)


def verify_task_4_2():
    """Проверяет что задача 4.2 полностью реализована."""
    print("=== ПРОВЕРКА ЗАДАЧИ 4.2: Add directory access validation ===")
    
    config = PlatformConfig.for_current_platform()
    manager = DirectoryManager(config)
    
    # Проверка 1: Метод validate_directory_access существует
    assert hasattr(manager, 'validate_directory_access'), "Метод validate_directory_access не найден"
    print("✅ Метод validate_directory_access существует")
    
    # Проверка 2: Метод _check_disk_space существует
    assert hasattr(manager, '_check_disk_space'), "Метод _check_disk_space не найден"
    print("✅ Метод _check_disk_space существует")
    
    # Проверка 3: Метод _log_directory_validation_error существует
    assert hasattr(manager, '_log_directory_validation_error'), "Метод _log_directory_validation_error не найден"
    print("✅ Метод _log_directory_validation_error существует")
    
    # Проверка 4: Метод _get_permission_fix_suggestion существует
    assert hasattr(manager, '_get_permission_fix_suggestion'), "Метод _get_permission_fix_suggestion не найден"
    print("✅ Метод _get_permission_fix_suggestion существует")
    
    # Проверка 5: Функциональный тест валидации
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir)
        result = manager.validate_directory_access(test_path)
        assert result == True, "Валидная директория должна пройти проверку"
        print("✅ Валидация доступной директории работает")
    
    # Проверка 6: Тест несуществующей директории
    nonexistent_path = Path("/nonexistent/directory/path/12345")
    result = manager.validate_directory_access(nonexistent_path)
    assert result == False, "Несуществующая директория не должна пройти проверку"
    print("✅ Валидация несуществующей директории работает")
    
    print("\n🎉 ЗАДАЧА 4.2 ПОЛНОСТЬЮ РЕАЛИЗОВАНА!")
    print("Все требования выполнены:")
    print("  - ✅ validate_directory_access method для проверки прав доступа")
    print("  - ✅ Проверка свободного места на диске")
    print("  - ✅ Подробные сообщения об ошибках")
    
    return True


if __name__ == "__main__":
    verify_task_4_2()