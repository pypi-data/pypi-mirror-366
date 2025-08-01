"""
Тест подключения к новому адресу лицензионного сервера
"""
import requests
import json
from datetime import datetime

def test_license_connection():
    """Тестирует подключение к новому адресу лицензионного сервера"""
    
    print("=" * 70)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К НОВОМУ ЛИЦЕНЗИОННОМУ СЕРВЕРУ")
    print("=" * 70)
    
    # Новый адрес
    base_url = "http://utils-licensegateproxy-yodjsn-513a08-83-222-22-34.traefik.me:1884/license/a2029"
    license_key = "743017d6-221c-4e0a-93ed-e417ae006db2"
    full_url = f"{base_url}/{license_key}/verify"
    
    print(f"Тестируемый URL: {full_url}")
    print(f"Лицензионный ключ: {license_key}")
    print()
    
    try:
        print("1. Выполнение HTTP GET запроса...")
        response = requests.get(full_url, timeout=10)
        
        print(f"   Статус код: {response.status_code}")
        print(f"   Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Успешное подключение!")
            
            try:
                data = response.json()
                print(f"   Ответ сервера (JSON): {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get('valid'):
                    print("✅ Лицензия действительна!")
                else:
                    print("❌ Лицензия недействительна!")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"   Сырой ответ: {response.text}")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"   Текст ответа: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения (10 сек)")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Ошибка подключения: {e}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    print()
    print("2. Тест с использованием нашего LicenseManager...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from offers_check_marketplaces.license_manager import LicenseManager
        
        # Создаем менеджер лицензий
        license_manager = LicenseManager(license_key)
        
        # Проверяем лицензию без кэша
        is_valid, license_info = license_manager.verify_license(use_cache=False)
        
        if is_valid:
            print("✅ LicenseManager: Лицензия действительна!")
            print(f"   Информация: {json.dumps(license_info, indent=2, ensure_ascii=False, default=str)}")
        else:
            print("❌ LicenseManager: Лицензия недействительна!")
            print(f"   Ошибка: {license_info}")
            
    except Exception as e:
        print(f"❌ Ошибка LicenseManager: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 70)

if __name__ == "__main__":
    test_license_connection()