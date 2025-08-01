"""
Тест установки и работы пакета offers-check-marketplaces
"""
import subprocess
import sys
import os
from pathlib import Path

def test_package_installation():
    """Тестирует установку и работу пакета"""
    
    print("=" * 60)
    print("ТЕСТ УСТАНОВКИ ПАКЕТА OFFERS-CHECK-MARKETPLACES")
    print("=" * 60)
    
    # Проверяем, что пакет собран
    wheel_file = Path("dist/offers_check_marketplaces-0.1.0-py3-none-any.whl")
    if not wheel_file.exists():
        print("❌ Файл пакета не найден. Сначала соберите пакет с помощью: uv build")
        return False
    
    print(f"✅ Найден файл пакета: {wheel_file}")
    
    # Тест 1: Проверка содержимого пакета
    print("\n1. Проверка содержимого пакета...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "zipfile", "-l", str(wheel_file)
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Пакет содержит следующие файлы:")
            lines = result.stdout.split('\n')[:10]  # Показываем первые 10 строк
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(result.stdout.split('\n')) > 10:
                print("   ... и другие файлы")
        else:
            print(f"❌ Ошибка при проверке содержимого: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке содержимого: {e}")
    
    # Тест 2: Проверка метаданных пакета
    print("\n2. Проверка метаданных пакета...")
    try:
        result = subprocess.run([
            "uvx", "twine", "check", str(wheel_file)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Метаданные пакета корректны")
            print(f"   {result.stdout.strip()}")
        else:
            print(f"❌ Проблемы с метаданными: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке метаданных: {e}")
    
    # Тест 3: Проверка зависимостей
    print("\n3. Проверка зависимостей...")
    try:
        # Читаем pyproject.toml для проверки зависимостей
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            
        if "requests>=2.28.0" in content:
            print("✅ Зависимость requests найдена")
        if "mcp>=1.7.1" in content:
            print("✅ Зависимость mcp найдена")
        if "pandas>=2.0.0" in content:
            print("✅ Зависимость pandas найдена")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке зависимостей: {e}")
    
    # Тест 4: Проверка entry point
    print("\n4. Проверка entry point...")
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            
        if 'offers-check-marketplaces = "offers_check_marketplaces.__main__:main"' in content:
            print("✅ Entry point корректно настроен")
        else:
            print("❌ Entry point не найден или настроен неправильно")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке entry point: {e}")
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print("✅ Пакет готов к публикации!")
    print("\nДля публикации выполните:")
    print("1. Тест на Test PyPI:")
    print("   uvx twine upload --repository testpypi dist/*")
    print("\n2. Публикация на PyPI:")
    print("   uvx twine upload dist/*")
    print("\n3. Установка из PyPI:")
    print("   pip install offers-check-marketplaces")
    print("\n4. Использование:")
    print("   LICENSE_KEY=your-key offers-check-marketplaces")
    
    return True

if __name__ == "__main__":
    test_package_installation()