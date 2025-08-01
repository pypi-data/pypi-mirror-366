"""
Тест MCP инструментов для работы с лицензией
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.server import check_license_status, set_license_key, initialize_components

async def test_mcp_license_tools():
    """Тестирует MCP инструменты для работы с лицензией"""
    
    print("=" * 60)
    print("ТЕСТ MCP ИНСТРУМЕНТОВ ЛИЦЕНЗИИ")
    print("=" * 60)
    
    try:
        # Инициализируем компоненты (но без проверки лицензии, чтобы протестировать инструменты)
        print("\n1. Инициализация компонентов...")
        # Временно отключаем проверку лицензии в initialize_components
        # await initialize_components()
        print("✅ Компоненты инициализированы (пропущено для теста)")
        
        # Тест 1: Проверка статуса лицензии через MCP инструмент
        print("\n2. Тест check_license_status...")
        license_status = await check_license_status()
        
        if license_status.get("status") == "valid":
            print("✅ MCP инструмент check_license_status работает!")
            print(f"   Статус: {license_status['status']}")
            print(f"   Сообщение: {license_status['message']}")
            print(f"   Ключ: {license_status['license_key']}")
        else:
            print("❌ MCP инструмент check_license_status вернул ошибку!")
            print(f"   Статус: {license_status.get('status', 'unknown')}")
            print(f"   Сообщение: {license_status.get('message', 'Нет сообщения')}")
        
        # Тест 2: Установка того же лицензионного ключа
        print("\n3. Тест set_license_key с существующим ключом...")
        current_key = "743017d6-221c-4e0a-93ed-e417ae006db2"
        set_result = await set_license_key(current_key)
        
        if set_result.get("status") == "success":
            print("✅ MCP инструмент set_license_key работает!")
            print(f"   Статус: {set_result['status']}")
            print(f"   Сообщение: {set_result['message']}")
            print(f"   Сохранен в конфиг: {set_result.get('saved_to_config', False)}")
        else:
            print("❌ MCP инструмент set_license_key вернул ошибку!")
            print(f"   Статус: {set_result.get('status', 'unknown')}")
            print(f"   Сообщение: {set_result.get('message', 'Нет сообщения')}")
        
        # Тест 3: Попытка установки недействительного ключа
        print("\n4. Тест set_license_key с недействительным ключом...")
        invalid_key = "invalid-key-12345"
        invalid_result = await set_license_key(invalid_key)
        
        if invalid_result.get("status") == "error":
            print("✅ MCP инструмент правильно обработал недействительный ключ!")
            print(f"   Статус: {invalid_result['status']}")
            print(f"   Сообщение: {invalid_result['message']}")
        else:
            print("❌ MCP инструмент не обработал недействительный ключ!")
            print(f"   Статус: {invalid_result.get('status', 'unknown')}")
        
        # Тест 4: Повторная проверка статуса после тестов
        print("\n5. Повторная проверка статуса лицензии...")
        final_status = await check_license_status()
        
        if final_status.get("status") == "valid":
            print("✅ Лицензия остается действительной после тестов!")
            print(f"   Ключ: {final_status['license_key']}")
        else:
            print("❌ Проблема с лицензией после тестов!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("ТЕСТ MCP ИНСТРУМЕНТОВ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_license_tools())