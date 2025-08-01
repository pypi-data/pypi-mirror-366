#!/usr/bin/env python3
"""
Тестирование системы управления пользовательскими данными.
"""

import os
import sys
import tempfile
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    UserDataManager, 
    PlatformDetector, 
    Platform,
    PlatformConfig,
    DirectoryManager
)


def test_platform_detection():
    """Тестирует определение платформы."""
    print("=== ТЕСТ ОПРЕДЕЛЕНИЯ ПЛАТФОРМЫ ===")
    
    detector = PlatformDetector()
    platform = detector.get_platform()
    
    print(f"Обнаружена платформа: {platform.value}")
    
    data_dir = detector.get_user_data_dir()
    cache_dir = detector.get_user_cache_dir()
    
    print(f"Стандартная директория данных: {data_dir}")
    print(f"Стандартная директория кеша: {cache_dir}")
    print(f"Поддержка XDG: {detector.supports_xdg_base_directory()}")
    
    return True


def test_platform_config():
    """Тестирует конфигурацию платформы."""
    print("\n=== ТЕСТ КОНФИГУРАЦИИ ПЛАТФОРМЫ ===")
    
    config = PlatformConfig.for_current_platform()
    
    print(f"Платформа: {config.platform.value}")
    print(f"Базовая директория: {config.base_directory}")
    print(f"Директория кеша: {config.cache_directory}")
    print(f"Директория логов: {config.logs_directory}")
    print(f"Права доступа: {config.permissions}")
    
    return True


def test_directory_structure():
    """Тестирует создание структуры директорий."""
    print("\n=== ТЕСТ СТРУКТУРЫ ДИРЕКТОРИЙ ===")
    
    # Используем временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir) / "test_offers_check"
        
        config = PlatformConfig.for_current_platform()
        # Переопределяем пути для тестирования
        config.base_directory = base_path
        config.cache_directory = base_path / "cache"
        config.logs_directory = base_path / "logs"
        
        manager = DirectoryManager(config)
        
        try:
            structure = manager.create_directory_structure(base_path)
            
            print(f"Создана структура в: {base_path}")
            print(f"База данных: {structure.database}")
            print(f"Кеш: {structure.cache}")
            print(f"Логи: {structure.logs}")
            print(f"Временные: {structure.temp}")
            
            # Проверяем что все директории созданы
            assert structure.base.exists(), "Базовая директория не создана"
            assert structure.database.exists(), "Директория БД не создана"
            assert structure.cache.exists(), "Директория кеша не создана"
            assert structure.logs.exists(), "Директория логов не создана"
            assert structure.temp.exists(), "Временная директория не создана"
            
            # Проверяем доступность
            assert manager.validate_directory_access(structure.base), "Нет доступа к базовой директории"
            
            print("✅ Все директории созданы и доступны")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания структуры: {e}")
            return False


def test_environment_override():
    """Тестирует переопределение через переменную окружения."""
    print("\n=== ТЕСТ ПЕРЕОПРЕДЕЛЕНИЯ ЧЕРЕЗ ПЕРЕМЕННУЮ ОКРУЖЕНИЯ ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_path = Path(temp_dir) / "custom_data"
        
        # Устанавливаем переменную окружения
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_path)
        
        try:
            manager = UserDataManager()
            data_dir = manager.get_data_directory()
            
            print(f"Кастомная директория: {data_dir}")
            
            # Проверяем что используется кастомный путь
            assert str(data_dir) == str(custom_path), f"Ожидался {custom_path}, получен {data_dir}"
            
            # Проверяем что директория создана
            assert data_dir.exists(), "Кастомная директория не создана"
            
            print("✅ Переопределение через переменную окружения работает")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка переопределения: {e}")
            return False
        finally:
            # Очищаем переменную окружения
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']


def test_user_data_manager():
    """Тестирует полную функциональность UserDataManager."""
    print("\n=== ТЕСТ USER DATA MANAGER ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_path = Path(temp_dir) / "test_data"
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_path)
        
        try:
            manager = UserDataManager()
            
            # Тестируем получение путей
            data_dir = manager.get_data_directory()
            db_path = manager.get_database_path()
            cache_dir = manager.get_cache_directory()
            logs_dir = manager.get_logs_directory()
            temp_dir = manager.get_temp_directory()
            
            print(f"Данные: {data_dir}")
            print(f"База данных: {db_path}")
            print(f"Кеш: {cache_dir}")
            print(f"Логи: {logs_dir}")
            print(f"Временные: {temp_dir}")
            
            # Проверяем что все пути существуют
            assert data_dir.exists(), "Директория данных не создана"
            assert db_path.parent.exists(), "Директория БД не создана"
            assert cache_dir.exists(), "Директория кеша не создана"
            assert logs_dir.exists(), "Директория логов не создана"
            assert temp_dir.exists(), "Временная директория не создана"
            
            # Тестируем получение информации
            info = manager.get_directory_info()
            print(f"\nИнформация о директориях:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            print("✅ UserDataManager работает корректно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка UserDataManager: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']


def main():
    """Запускает все тесты."""
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЬСКИМИ ДАННЫМИ")
    print("=" * 60)
    
    tests = [
        test_platform_detection,
        test_platform_config,
        test_directory_structure,
        test_environment_override,
        test_user_data_manager
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📊 Всего: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print(f"\n💥 {failed} ТЕСТОВ ПРОВАЛЕНО")
        return 1


if __name__ == "__main__":
    sys.exit(main())