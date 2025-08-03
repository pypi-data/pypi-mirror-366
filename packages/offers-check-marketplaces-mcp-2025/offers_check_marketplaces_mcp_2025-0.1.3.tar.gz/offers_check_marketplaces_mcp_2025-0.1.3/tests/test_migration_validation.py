#!/usr/bin/env python3
"""
Простой тест для проверки валидации и отката миграции.
"""

import sys
import tempfile
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

try:
    from offers_check_marketplaces.user_data_manager import (
        DataMigrator, DirectoryStructure
    )
    print("✓ Импорт DataMigrator успешен")
    
    # Создаем тестовую структуру
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        target_base = temp_path / "target"
        target_structure = DirectoryStructure(
            base=target_base,
            database=target_base / "database",
            cache=target_base / "cache",
            logs=target_base / "logs",
            temp=target_base / "temp"
        )
        
        # Создаем DataMigrator
        migrator = DataMigrator(target_structure)
        print("✓ DataMigrator создан успешно")
        
        # Тестируем создание точки отката
        rollback_info = migrator._create_rollback_point()
        print("✓ Точка отката создана успешно")
        print(f"  Rollback info keys: {list(rollback_info.keys())}")
        
        # Тестируем проверку целостности (должна пройти для пустой директории)
        integrity_result = migrator._verify_migration_integrity(temp_path / "nonexistent")
        print(f"✓ Проверка целостности: {integrity_result}")
        
        print("\n✓ Все базовые тесты пройдены!")
        
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка теста: {e}")
    sys.exit(1)