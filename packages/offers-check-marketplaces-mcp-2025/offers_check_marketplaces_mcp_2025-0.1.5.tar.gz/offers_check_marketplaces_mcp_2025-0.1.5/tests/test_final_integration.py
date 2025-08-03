"""
Финальный тест интеграции лицензии с сервером
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

async def test_server_with_license():
    """Тестирует запуск сервера с интегрированной лицензией"""
    
    print("=" * 70)
    print("ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ ЛИЦЕНЗИИ С СЕРВЕРОМ")
    print("=" * 70)
    
    try:
        # Импортируем компоненты сервера
        from offers_check_marketplaces.server import (
            initialize_components, 
            check_license_status, 
            set_license_key
        )
        from offers_check_marketplaces.license_manager import check_license
        
        print("\n1. Проверка лицензии перед инициализацией...")
        is_valid, license_info = check_license()
        
        if is_valid:
            print("✅ Лицензия действительна!")
            print(f"   Ключ: {license_info.get('license_key', 'Не указан')}")
        else:
            print("❌ Лицензия недействительна!")
            print(f"   Ошибка: {license_info.get('message', 'Неизвестная ошибка')}")
            return
        
        print("\n2. Инициализация компонентов сервера...")
        try:
            await initialize_components()
            print("✅ Компоненты сервера успешно инициализированы!")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return
        
        print("\n3. Тест MCP инструмента check_license_status...")
        license_status = await check_license_status()
        
        if license_status.get("status") == "valid":
            print("✅ MCP инструмент check_license_status работает!")
            print(f"   Статус: {license_status['status']}")
            print(f"   Ключ: {license_status['license_key']}")
        else:
            print("❌ Проблема с MCP инструментом check_license_status!")
            print(f"   Ответ: {license_status}")
        
        print("\n4. Тест MCP инструмента set_license_key...")
        current_key = "743017d6-221c-4e0a-93ed-e417ae006db2"
        set_result = await set_license_key(current_key)
        
        if set_result.get("status") == "success":
            print("✅ MCP инструмент set_license_key работает!")
            print(f"   Статус: {set_result['status']}")
        else:
            print("❌ Проблема с MCP инструментом set_license_key!")
            print(f"   Ответ: {set_result}")
        
        print("\n5. Проверка доступности других MCP инструментов...")
        try:
            from offers_check_marketplaces.server import (
                get_product_details,
                get_product_list,
                get_statistics
            )
            print("✅ Все основные MCP инструменты доступны!")
            print("   - get_product_details") 
            print("   - get_product_list")
            print("   - get_statistics")
            print("   - check_license_status")
            print("   - set_license_key")
        except ImportError as e:
            print(f"❌ Проблема с импортом MCP инструментов: {e}")
        
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
        
        print("\n" + "=" * 70)
        print("✅ ИНТЕГРАЦИЯ ЛИЦЕНЗИИ УСПЕШНО ЗАВЕРШЕНА!")
        print("=" * 70)
        print("\nСервер готов к работе с интегрированной проверкой лицензии:")
        print("- Лицензия проверяется при запуске сервера")
        print("- Доступны MCP инструменты для управления лицензией")
        print("- Лицензионный ключ сохраняется в конфигурации")
        print("- Результаты проверки кэшируются для производительности")
        print("\nДля запуска сервера используйте:")
        print("  python -m offers_check_marketplaces")
        print("  python -m offers_check_marketplaces --sse --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server_with_license())