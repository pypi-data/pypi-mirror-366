#!/usr/bin/env python3
"""
Тест для проверки улучшенной обработки ошибок и логирования в UserDataManager.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    UserDataManager, DirectoryCreationError, PermissionError, 
    DiskSpaceError, ValidationError, MigrationError
)

def setup_logging():
    """Настраивает логирование для тестов."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_user_friendly_error_messages():
    """Тестирует пользовательские сообщения об ошибках."""
    print("=" * 60)
    print("ТЕСТ: Пользовательские сообщения об ошибках")
    print("=" * 60)
    
    # Тест DirectoryCreationError
    try:
        from offers_check_marketplaces.user_data_manager import Platform
        error = DirectoryCreationError(
            "Permission denied: /root/test",
            directory_path=Path("/root/test"),
            platform=Platform.LINUX
        )
        print("DirectoryCreationError сообщение:")
        print(error.get_user_friendly_message())
        print()
    except Exception as e:
        print(f"Ошибка создания DirectoryCreationError: {e}")
    
    # Тест PermissionError
    try:
        from offers_check_marketplaces.user_data_manager import Platform
        error = PermissionError(
            "Access denied to directory",
            directory_path=Path("/test/dir"),
            access_type="write",
            platform=Platform.WINDOWS
        )
        print("PermissionError сообщение:")
        print(error.get_user_friendly_message())
        print()
    except Exception as e:
        print(f"Ошибка создания PermissionError: {e}")
    
    # Тест DiskSpaceError
    try:
        error = DiskSpaceError(
            "Not enough space",
            required_space_mb=500.0,
            available_space_mb=100.0,
            directory_path=Path("/tmp")
        )
        print("DiskSpaceError сообщение:")
        print(error.get_user_friendly_message())
        print()
    except Exception as e:
        print(f"Ошибка создания DiskSpaceError: {e}")

def test_detailed_logging():
    """Тестирует подробное логирование."""
    print("=" * 60)
    print("ТЕСТ: Подробное логирование")
    print("=" * 60)
    
    try:
        # Создаем временную директорию для тестов
        with tempfile.TemporaryDirectory() as temp_dir:
            # Устанавливаем переменную окружения для использования временной директории
            os.environ['OFFERS_CHECK_DATA_DIR'] = temp_dir
            
            try:
                # Создаем UserDataManager - это должно вызвать подробное логирование
                manager = UserDataManager()
                
                print("\nИнициализация UserDataManager...")
                result = manager.initialize_directories()
                
                if result:
                    print("✅ Инициализация прошла успешно")
                    
                    # Получаем информацию о директориях
                    info = manager.get_directory_info()
                    print("\nИнформация о директориях:")
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                else:
                    print("❌ Инициализация не удалась")
                    
            finally:
                # Очищаем переменную окружения
                if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                    del os.environ['OFFERS_CHECK_DATA_DIR']
                    
    except Exception as e:
        print(f"Ошибка в тесте логирования: {e}")
        import traceback
        traceback.print_exc()

def test_error_recovery():
    """Тестирует стратегии восстановления после ошибок."""
    print("=" * 60)
    print("ТЕСТ: Стратегии восстановления после ошибок")
    print("=" * 60)
    
    try:
        # Тестируем с недоступной директорией
        invalid_path = "/root/invalid_directory_for_test"
        os.environ['OFFERS_CHECK_DATA_DIR'] = invalid_path
        
        try:
            manager = UserDataManager()
            manager.initialize_directories()
            print("❌ Ожидалась ошибка, но инициализация прошла успешно")
        except Exception as e:
            print(f"✅ Получена ожидаемая ошибка: {type(e).__name__}")
            
            # Проверяем наличие пользовательского сообщения
            if hasattr(e, 'get_user_friendly_message'):
                print("Пользовательское сообщение об ошибке:")
                print(e.get_user_friendly_message())
            else:
                print(f"Стандартное сообщение: {e}")
                
    except Exception as e:
        print(f"Неожиданная ошибка в тесте восстановления: {e}")
    finally:
        # Очищаем переменную окружения
        if 'OFFERS_CHECK_DATA_DIR' in os.environ:
            del os.environ['OFFERS_CHECK_DATA_DIR']

def main():
    """Основная функция тестирования."""
    print("ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ОБРАБОТКИ ОШИБОК И ЛОГИРОВАНИЯ")
    print("=" * 70)
    
    # Настраиваем логирование
    setup_logging()
    
    # Запускаем тесты
    test_user_friendly_error_messages()
    test_detailed_logging()
    test_error_recovery()
    
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)

if __name__ == "__main__":
    main()