"""
Тест обработки ошибок лицензии и завершения программы
"""
import os
import sys
import subprocess
from pathlib import Path

def test_invalid_license_exit():
    """Тестирует завершение программы при недействительном лицензионном ключе"""
    
    print("=" * 70)
    print("ТЕСТ ЗАВЕРШЕНИЯ ПРОГРАММЫ ПРИ НЕПРАВИЛЬНОЙ ЛИЦЕНЗИИ")
    print("=" * 70)
    
    # Тест 1: Запуск с недействительным ключом
    print("\n1. Тест с недействительным лицензионным ключом...")
    
    invalid_key = "invalid-license-key-12345"
    
    try:
        # Запускаем сервер с недействительным ключом
        env = os.environ.copy()
        env['LICENSE_KEY'] = invalid_key
        
        result = subprocess.run([
            sys.executable, "-m", "offers_check_marketplaces"
        ], 
        env=env,
        capture_output=True,
        text=True,
        timeout=30  # Таймаут 30 секунд
        )
        
        print(f"   Код завершения: {result.returncode}")
        print(f"   STDOUT: {result.stdout}")
        print(f"   STDERR: {result.stderr}")
        
        if result.returncode == 1:
            print("✅ Программа корректно завершилась с кодом 1")
            if "Недействительная лицензия" in result.stdout or "ОШИБКА" in result.stdout:
                print("✅ Выведено корректное сообщение об ошибке")
            else:
                print("❌ Не найдено сообщение об ошибке лицензии")
        else:
            print(f"❌ Неожиданный код завершения: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Программа не завершилась в течение 30 секунд")
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")
    
    # Тест 2: Запуск без лицензионного ключа
    print("\n2. Тест без лицензионного ключа...")
    
    try:
        # Запускаем сервер без ключа
        env = os.environ.copy()
        if 'LICENSE_KEY' in env:
            del env['LICENSE_KEY']
        
        result = subprocess.run([
            sys.executable, "-m", "offers_check_marketplaces"
        ], 
        env=env,
        capture_output=True,
        text=True,
        timeout=30
        )
        
        print(f"   Код завершения: {result.returncode}")
        print(f"   STDOUT: {result.stdout}")
        print(f"   STDERR: {result.stderr}")
        
        if result.returncode == 1:
            print("✅ Программа корректно завершилась с кодом 1")
            if "лицензи" in result.stdout.lower() or "ОШИБКА" in result.stdout:
                print("✅ Выведено сообщение о проблеме с лицензией")
            else:
                print("❌ Не найдено сообщение о проблеме с лицензией")
        else:
            print(f"❌ Неожиданный код завершения: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Программа не завершилась в течение 30 секунд")
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")
    
    # Тест 3: Запуск с действительным ключом (должен запуститься)
    print("\n3. Тест с действительным лицензионным ключом...")
    
    valid_key = "743017d6-221c-4e0a-93ed-e417ae006db2"
    
    try:
        # Запускаем сервер с действительным ключом
        env = os.environ.copy()
        env['LICENSE_KEY'] = valid_key
        
        # Используем таймаут 10 секунд, так как сервер должен запуститься
        process = subprocess.Popen([
            sys.executable, "-m", "offers_check_marketplaces"
        ], 
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        
        # Ждем несколько секунд для инициализации
        import time
        time.sleep(5)
        
        # Проверяем, что процесс еще работает
        if process.poll() is None:
            print("✅ Сервер успешно запустился с действительной лицензией")
            
            # Завершаем процесс
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
        else:
            # Процесс завершился
            stdout, stderr = process.communicate()
            print(f"❌ Сервер неожиданно завершился")
            print(f"   Код завершения: {process.returncode}")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")
        if 'process' in locals():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
    
    print("\n" + "=" * 70)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 70)
    print("\nРезультаты:")
    print("- Программа должна завершаться с кодом 1 при недействительной лицензии")
    print("- Должно выводиться понятное сообщение об ошибке")
    print("- С действительной лицензией сервер должен запускаться нормально")

if __name__ == "__main__":
    test_invalid_license_exit()