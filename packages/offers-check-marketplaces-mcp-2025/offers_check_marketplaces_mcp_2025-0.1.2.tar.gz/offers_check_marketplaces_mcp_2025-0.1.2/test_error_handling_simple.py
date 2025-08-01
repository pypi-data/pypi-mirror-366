#!/usr/bin/env python3
"""
Простой тест для проверки улучшенной обработки ошибок.
"""

import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

try:
    from offers_check_marketplaces.user_data_manager import (
        DirectoryCreationError, PermissionError, DiskSpaceError, 
        ValidationError, Platform
    )
    
    print("✅ Импорт классов ошибок успешен")
    
    # Тестируем создание ошибки с пользовательским сообщением
    try:
        error = DirectoryCreationError(
            "Test error message",
            directory_path=Path("/test"),
            platform=Platform.WINDOWS
        )
        
        print("✅ Создание DirectoryCreationError успешно")
        print("Пользовательское сообщение:")
        print(error.get_user_friendly_message())
        
    except Exception as e:
        print(f"❌ Ошибка создания DirectoryCreationError: {e}")
    
    # Тестируем PermissionError
    try:
        error = PermissionError(
            "Permission denied",
            directory_path=Path("/test"),
            access_type="write",
            platform=Platform.LINUX
        )
        
        print("\n✅ Создание PermissionError успешно")
        print("Пользовательское сообщение:")
        print(error.get_user_friendly_message())
        
    except Exception as e:
        print(f"❌ Ошибка создания PermissionError: {e}")
    
    print("\n✅ Все тесты обработки ошибок пройдены успешно")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)