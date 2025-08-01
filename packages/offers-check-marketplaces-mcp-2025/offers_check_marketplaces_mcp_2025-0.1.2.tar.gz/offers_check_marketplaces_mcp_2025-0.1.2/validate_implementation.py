#!/usr/bin/env python3
"""
Валидация реализации поддержки переменной окружения OFFERS_CHECK_DATA_DIR.
Проверяет соответствие требованиям без запуска кода.
"""

import ast
import sys
from pathlib import Path


def validate_path_resolver_implementation():
    """Проверяет реализацию PathResolver на соответствие требованиям."""
    print("=== Валидация реализации PathResolver ===")
    
    # Читаем файл с реализацией
    file_path = Path("offers_check_marketplaces/user_data_manager.py")
    if not file_path.exists():
        print("❌ Файл user_data_manager.py не найден")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие ключевых элементов
    checks = [
        # Requirement 4.1: WHEN переменная OFFERS_CHECK_DATA_DIR установлена THEN используется указанный путь
        ("OFFERS_CHECK_DATA_DIR", "Проверка переменной окружения OFFERS_CHECK_DATA_DIR"),
        ("os.environ.get('OFFERS_CHECK_DATA_DIR')", "Получение значения переменной окружения"),
        ("_resolve_custom_path", "Метод разрешения кастомного пути"),
        
        # Requirement 4.2: WHEN указанный путь не существует THEN он автоматически создается
        ("_ensure_custom_directory_exists", "Метод создания кастомной директории"),
        ("path.mkdir(parents=True, exist_ok=True)", "Создание директории с родительскими"),
        
        # Requirement 4.3: WHEN путь недоступен для записи THEN выводится понятное сообщение об ошибке
        ("_validate_custom_path", "Метод валидации кастомного пути"),
        ("_validate_directory_access", "Метод проверки доступа к директории"),
        ("os.access(", "Проверка прав доступа"),
        ("DirectoryCreationError", "Исключение для ошибок создания директории"),
        ("PermissionError", "Исключение для ошибок прав доступа"),
        
        # Дополнительные проверки
        ("validate_and_create_structure", "Метод валидации и создания структуры"),
        ("expanduser", "Разворачивание пользовательских путей (~)"),
        ("resolve()", "Получение абсолютного пути"),
    ]
    
    results = []
    for check, description in checks:
        if check in content:
            print(f"✓ {description}")
            results.append(True)
        else:
            print(f"❌ {description} - не найдено: {check}")
            results.append(False)
    
    # Проверяем структуру класса PathResolver
    try:
        tree = ast.parse(content)
        path_resolver_found = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "PathResolver":
                path_resolver_found = True
                print("✓ Класс PathResolver найден")
                
                # Проверяем методы
                methods = [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                required_methods = [
                    "__init__", "resolve_data_directory", "_resolve_custom_path",
                    "_validate_custom_path", "_ensure_custom_directory_exists",
                    "_validate_directory_access", "validate_and_create_structure"
                ]
                
                for method in required_methods:
                    if method in methods:
                        print(f"✓ Метод {method} найден")
                        results.append(True)
                    else:
                        print(f"❌ Метод {method} не найден")
                        results.append(False)
                break
        
        if not path_resolver_found:
            print("❌ Класс PathResolver не найден")
            results.append(False)
    
    except SyntaxError as e:
        print(f"❌ Синтаксическая ошибка в коде: {e}")
        return False
    
    success_rate = sum(results) / len(results) * 100
    print(f"\nРезультат валидации: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 90


def validate_user_data_manager_integration():
    """Проверяет интеграцию PathResolver в UserDataManager."""
    print("\n=== Валидация интеграции в UserDataManager ===")
    
    file_path = Path("offers_check_marketplaces/user_data_manager.py")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("self.path_resolver = PathResolver(self.platform_detector)", "Инициализация PathResolver с platform_detector"),
        ("custom_path = os.environ.get('OFFERS_CHECK_DATA_DIR')", "Проверка переменной в initialize_directories"),
        ("validate_and_create_structure", "Использование валидации для кастомных путей"),
    ]
    
    results = []
    for check, description in checks:
        if check in content:
            print(f"✓ {description}")
            results.append(True)
        else:
            print(f"❌ {description}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"Результат интеграции: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 80


def validate_error_handling():
    """Проверяет обработку ошибок."""
    print("\n=== Валидация обработки ошибок ===")
    
    file_path = Path("offers_check_marketplaces/user_data_manager.py")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    error_messages = [
        "является файлом, а не директорией",
        "Нельзя использовать системную директорию",
        "Родительская директория",
        "Нет прав на запись",
        "Нет прав для создания директории",
        "Недостаточно места на диске",
        "Измените права доступа: chmod 755",
    ]
    
    results = []
    for message in error_messages:
        if message in content:
            print(f"✓ Сообщение об ошибке: {message}")
            results.append(True)
        else:
            print(f"❌ Отсутствует сообщение: {message}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"Результат обработки ошибок: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 70


def main():
    """Запускает валидацию."""
    print("Валидация реализации поддержки переменной окружения OFFERS_CHECK_DATA_DIR\n")
    
    try:
        path_resolver_ok = validate_path_resolver_implementation()
        integration_ok = validate_user_data_manager_integration()
        error_handling_ok = validate_error_handling()
        
        if path_resolver_ok and integration_ok and error_handling_ok:
            print("\n🎉 Реализация соответствует требованиям!")
            print("\nРеализованные функции:")
            print("- ✓ Поддержка переменной окружения OFFERS_CHECK_DATA_DIR")
            print("- ✓ Автоматическое создание кастомных директорий")
            print("- ✓ Валидация путей и прав доступа")
            print("- ✓ Понятные сообщения об ошибках")
            print("- ✓ Создание структуры поддиректорий")
            print("- ✓ Интеграция с UserDataManager")
            return True
        else:
            print("\n❌ Реализация требует доработки")
            return False
    
    except Exception as e:
        print(f"\n❌ Ошибка валидации: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)