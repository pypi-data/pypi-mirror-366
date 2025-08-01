#!/usr/bin/env python3
"""
Простой тест для проверки переменной окружения OFFERS_CHECK_DATA_DIR.
"""

import os
import sys
import tempfile
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

try:
    from offers_check_marketplaces.user_data_manager import PathResolver, PlatformDetector
    print("✓ Модули импортированы успешно")
    
    # Тест без переменной окружения
    if 'OFFERS_CHECK_DATA_DIR' in os.environ:
        del os.environ['OFFERS_CHECK_DATA_DIR']
    
    resolver = PathResolver(PlatformDetector())
    standard_path = resolver.resolve_data_directory()
    print(f"✓ Стандартный путь: {standard_path}")
    
    # Тест с переменной окружения
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_path = Path(temp_dir) / "custom_data"
        os.environ['OFFERS_CHECK_DATA_DIR'] = str(custom_path)
        
        custom_resolved = resolver.resolve_data_directory()
        print(f"✓ Кастомный путь: {custom_resolved}")
        
        # Проверяем что директория создана
        if custom_path.exists():
            print("✓ Кастомная директория создана")
        else:
            print("❌ Кастомная директория не создана")
        
        # Очищаем переменную
        del os.environ['OFFERS_CHECK_DATA_DIR']
    
    print("\n🎉 Базовый тест прошел успешно!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)