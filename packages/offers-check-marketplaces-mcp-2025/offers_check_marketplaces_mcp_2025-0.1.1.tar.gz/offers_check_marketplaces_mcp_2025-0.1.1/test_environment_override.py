#!/usr/bin/env python3
"""
Тест для проверки поддержки переменной окружения OFFERS_CHECK_DATA_DIR.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    UserDataManager, PathResolver, PlatformDetector,
    DirectoryCreationError, PermissionError
)


def test_environment_variable_override():
    """Тестирует переопределение директории через переменную окружения."""
    print("=== Тест переопределения через OFFERS_CHECK_DATA_DIR ===")
    
    # Создаем временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_data_dir = Path(temp_dir) / "custom_offers_data"
        
        # Устанавливаем переменную окружения
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_data_dir)
        
        try:
            # Создаем менеджер данных
            manager = UserDataManager()
            
            # Инициализируем директории
            success = manager.initialize_directories()
            assert success, "Инициализация директорий должна быть успешной"
            
            # Проверяем что используется кастомная директория
            data_dir = manager.get_data_directory()
            assert data_dir == custom_data_dir, f"Ожидалась {custom_data_dir}, получена {data_dir}"
            
            # Проверяем что структура создана
            assert custom_data_dir.exists(), "Кастомная директория должна быть создана"
            assert (custom_data_dir / "database").exists(), "Поддиректория database должна существовать"
            assert (custom_data_dir / "cache").exists(), "Поддиректория cache должна существовать"
            assert (custom_data_dir / "logs").exists(), "Поддиректория logs должна существовать"
            assert (custom_data_dir / "temp").exists(), "Поддиректория temp должна существовать"
            
            # Проверяем пути к файлам
            db_path = manager.get_database_path()
            expected_db_path = custom_data_dir / "database" / "products.db"
            assert db_path == expected_db_path, f"Ожидался путь к БД {expected_db_path}, получен {db_path}"
            
            print(f"✓ Кастомная директория создана: {custom_data_dir}")
            print(f"✓ Путь к БД: {db_path}")
            print(f"✓ Структура директорий создана корректно")
            
        finally:
            # Очищаем переменную окружения
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']


def test_path_resolver_validation():
    """Тестирует валидацию путей в PathResolver."""
    print("\n=== Тест валидации путей ===")
    
    resolver = PathResolver(PlatformDetector())
    
    # Тест с корректным путем
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_path = Path(temp_dir) / "valid_path"
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_path)
        
        try:
            resolved_path = resolver.resolve_data_directory()
            assert resolved_path == custom_path, "Путь должен быть разрешен корректно"
            assert custom_path.exists(), "Директория должна быть создана"
            print(f"✓ Корректный путь разрешен: {resolved_path}")
            
        finally:
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']
    
    # Тест с некорректным путем (файл вместо директории)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            os.environ['OFFERS_CHECK_DATA_DIR'] = temp_file.name
            
            try:
                resolver.resolve_data_directory()
                assert False, "Должна быть выброшена ошибка для файла вместо директории"
            except DirectoryCreationError as e:
                print(f"✓ Корректно обработан файл вместо директории: {e}")
            
        finally:
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']
            os.unlink(temp_file.name)


def test_permission_handling():
    """Тестирует обработку ошибок прав доступа."""
    print("\n=== Тест обработки прав доступа ===")
    
    # Этот тест работает только на Unix-системах
    if os.name != 'posix':
        print("⚠ Тест прав доступа пропущен (не Unix система)")
        return
    
    resolver = PathResolver(PlatformDetector())
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем директорию без прав на запись
        restricted_dir = Path(temp_dir) / "restricted"
        restricted_dir.mkdir()
        restricted_dir.chmod(0o444)  # Только чтение
        
        custom_path = restricted_dir / "data"
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_path)
        
        try:
            resolver.resolve_data_directory()
            assert False, "Должна быть выброшена ошибка прав доступа"
        except (DirectoryCreationError, PermissionError) as e:
            print(f"✓ Корректно обработана ошибка прав доступа: {e}")
        finally:
            if 'OFFERS_CHECK_DATA_DIR' in os.environ:
                del os.environ['OFFERS_CHECK_DATA_DIR']
            # Восстанавливаем права для удаления
            restricted_dir.chmod(0o755)


def test_standard_directory_fallback():
    """Тестирует использование стандартной директории при отсутствии переменной."""
    print("\n=== Тест стандартной директории ===")
    
    # Убеждаемся что переменная не установлена
    if 'OFFERS_CHECK_DATA_DIR' in os.environ:
        del os.environ['OFFERS_CHECK_DATA_DIR']
    
    resolver = PathResolver(PlatformDetector())
    resolved_path = resolver.resolve_data_directory()
    
    # Проверяем что используется стандартный путь
    detector = PlatformDetector()
    expected_base = detector.get_user_data_dir() / "offers-check-marketplaces"
    
    assert resolved_path == expected_base, f"Ожидался стандартный путь {expected_base}, получен {resolved_path}"
    print(f"✓ Используется стандартная директория: {resolved_path}")


def main():
    """Запускает все тесты."""
    print("Запуск тестов поддержки переменной окружения OFFERS_CHECK_DATA_DIR\n")
    
    try:
        test_environment_variable_override()
        test_path_resolver_validation()
        test_permission_handling()
        test_standard_directory_fallback()
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"\n❌ Тест завершился с ошибкой: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()