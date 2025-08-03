"""
Тест интеграции лицензионного ключа
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.license_manager import LicenseManager, check_license

async def test_license_integration():
    """Тестирует интеграцию лицензионного ключа"""
    
    print("=" * 60)
    print("ТЕСТ ИНТЕГРАЦИИ ЛИЦЕНЗИОННОГО КЛЮЧА")
    print("=" * 60)
    
    # Тест 1: Проверка лицензии по умолчанию
    print("\n1. Проверка лицензии по умолчанию...")
    is_valid, license_info = check_license()
    
    if is_valid:
        print("✅ Лицензия действительна!")
        print(f"   Ключ: {license_info.get('license_key', 'Не указан')}")
        print(f"   Проверено: {license_info.get('checked_at', 'Неизвестно')}")
    else:
        print("❌ Лицензия недействительна!")
        print(f"   Ошибка: {license_info.get('message', 'Неизвестная ошибка')}")
    
    # Тест 2: Создание экземпляра менеджера лицензий
    print("\n2. Создание менеджера лицензий...")
    license_manager = LicenseManager()
    
    # Тест 3: Получение информации о лицензии
    print("\n3. Получение полной информации о лицензии...")
    full_info = license_manager.get_license_info()
    
    print(f"   Статус: {'✅ Действительна' if full_info['is_valid'] else '❌ Недействительна'}")
    print(f"   Ключ: {full_info['license_key']}")
    print(f"   API URL: {full_info['api_url']}")
    print(f"   Файл кэша: {full_info['cache_file']}")
    
    # Тест 4: Проверка без кэша
    print("\n4. Проверка лицензии без использования кэша...")
    is_valid_no_cache, license_info_no_cache = license_manager.verify_license(use_cache=False)
    
    if is_valid_no_cache:
        print("✅ Лицензия действительна (без кэша)!")
        print(f"   Данные: {license_info_no_cache.get('valid', 'Неизвестно')}")
    else:
        print("❌ Лицензия недействительна (без кэша)!")
        print(f"   Ошибка: {license_info_no_cache.get('message', 'Неизвестная ошибка')}")
    
    # Тест 5: Тест установки того же ключа
    print("\n5. Тест установки существующего ключа...")
    current_key = license_manager.license_key
    success = license_manager.set_license_key(current_key, save_to_config=False)
    
    if success:
        print("✅ Ключ успешно переустановлен!")
    else:
        print("❌ Не удалось переустановить ключ!")
    
    # Тест 6: Проверка файлов конфигурации
    print("\n6. Проверка файлов конфигурации...")
    
    config_file = Path("data/.license_config.json")
    cache_file = Path("data/.license_cache.json")
    
    print(f"   Файл конфигурации: {'✅ Существует' if config_file.exists() else '❌ Не найден'}")
    print(f"   Файл кэша: {'✅ Существует' if cache_file.exists() else '❌ Не найден'}")
    
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"   Ключ в конфигурации: {config_data.get('license_key', 'Не найден')}")
        except Exception as e:
            print(f"   Ошибка чтения конфигурации: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_license_integration())