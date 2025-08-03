"""
Тест работы с лицензионным ключом из переменной окружения
"""
import os
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

def test_license_from_environment():
    """Тестирует загрузку лицензионного ключа из переменной окружения"""
    
    print("=" * 70)
    print("ТЕСТ ЛИЦЕНЗИОННОГО КЛЮЧА ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ")
    print("=" * 70)
    
    # Тест 1: Без переменной окружения
    print("\n1. Тест без переменной окружения LICENSE_KEY...")
    
    # Убираем переменную окружения если она есть
    if 'LICENSE_KEY' in os.environ:
        del os.environ['LICENSE_KEY']
    
    try:
        from offers_check_marketplaces.license_manager import LicenseManager
        
        license_manager = LicenseManager()
        
        if license_manager.license_key is None:
            print("✅ Правильно: лицензионный ключ не найден")
        else:
            print(f"❌ Неожиданно: найден ключ {license_manager.license_key}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: С переменной окружения
    print("\n2. Тест с переменной окружения LICENSE_KEY...")
    
    test_key = "743017d6-221c-4e0a-93ed-e417ae006db2"
    os.environ['LICENSE_KEY'] = test_key
    
    try:
        # Перезагружаем модуль чтобы он заново прочитал переменную окружения
        import importlib
        from offers_check_marketplaces import license_manager as lm_module
        importlib.reload(lm_module)
        
        from offers_check_marketplaces.license_manager import LicenseManager
        
        license_manager = LicenseManager()
        
        if license_manager.license_key == test_key:
            print("✅ Правильно: лицензионный ключ загружен из переменной окружения")
            print(f"   Ключ: {license_manager.license_key}")
        else:
            print(f"❌ Неожиданно: ключ не совпадает. Ожидался {test_key}, получен {license_manager.license_key}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 3: Проверка лицензии с ключом из переменной окружения
    print("\n3. Проверка лицензии с ключом из переменной окружения...")
    
    try:
        from offers_check_marketplaces.license_manager import check_license
        
        is_valid, license_info = check_license()
        
        if is_valid:
            print("✅ Лицензия действительна!")
            print(f"   Ключ: {license_info.get('license_key', 'Не указан')}")
            print(f"   Проверено: {license_info.get('checked_at', 'Неизвестно')}")
        else:
            print("❌ Лицензия недействительна!")
            print(f"   Ошибка: {license_info.get('message', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки лицензии: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 4: Проверка что ключ не сохраняется в файл по умолчанию
    print("\n4. Проверка файлов конфигурации...")
    
    config_file = Path("data/.license_config.json")
    cache_file = Path("data/.license_cache.json")
    
    print(f"   Файл конфигурации: {'❌ Существует (не должен)' if config_file.exists() else '✅ Не существует (правильно)'}")
    print(f"   Файл кэша: {'✅ Существует' if cache_file.exists() else '❌ Не существует'}")
    
    print("\n" + "=" * 70)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 70)
    print("\nИнструкции для MCP конфигурации:")
    print("Добавьте в ваш mcp.json:")
    print("""
{
  "mcpServers": {
    "offers_check_marketplaces": {
      "command": "python",
      "args": ["-m", "offers_check_marketplaces"],
      "env": {
        "LICENSE_KEY": "ваш-лицензионный-ключ"
      }
    }
  }
}
""")

if __name__ == "__main__":
    test_license_from_environment()