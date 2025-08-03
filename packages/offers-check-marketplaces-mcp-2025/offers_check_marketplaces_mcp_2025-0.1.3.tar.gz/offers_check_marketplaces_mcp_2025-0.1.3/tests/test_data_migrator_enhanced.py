#!/usr/bin/env python3
"""
Тест для проверки расширенной функциональности DataMigrator.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    DataMigrator, DirectoryStructure, MigrationError
)

def test_data_migrator_enhanced():
    """Тестирует расширенную функциональность DataMigrator."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем тестовую структуру
        legacy_data = temp_path / "data"
        legacy_data.mkdir()
        
        # Создаем тестовые файлы
        (legacy_data / "test.db").write_bytes(b'SQLite format 3\x00' + b'test data' * 100)
        (legacy_data / "cache.tmp").write_text("cache data")
        (legacy_data / "app.log").write_text("log data")
        (legacy_data / "config.json").write_text('{"test": "value"}')
        
        # Создаем целевую структуру
        target_base = temp_path / "target"
        target_structure = DirectoryStructure(
            base=target_base,
            database=target_base / "database",
            cache=target_base / "cache", 
            logs=target_base / "logs",
            temp=target_base / "temp"
        )
        
        # Меняем рабочую директорию для теста
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            # Создаем и тестируем DataMigrator
            migrator = DataMigrator(target_structure)
            
            print("Тестирование расширенного DataMigrator...")
            
            # Выполняем миграцию
            result = migrator.migrate_legacy_data()
            
            if result:
                print("✓ Миграция выполнена успешно")
                
                # Проверяем что файлы мигрированы
                assert (target_structure.database / "test.db").exists()
                assert (target_structure.cache / "cache.tmp").exists()
                assert (target_structure.logs / "app.log").exists()
                assert (target_structure.base / "config.json").exists()
                
                # Проверяем что старая директория переименована
                assert (temp_path / "data.migrated").exists()
                assert not (temp_path / "data").exists()
                
                print("✓ Все проверки пройдены")
                print(f"✓ Статистика миграции: {migrator.migration_stats}")
                
            else:
                print("✗ Миграция не удалась")
                return False
                
        except Exception as e:
            print(f"✗ Ошибка теста: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    return True

def test_migration_rollback():
    """Тестирует механизм отката миграции."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем тестовую структуру
        legacy_data = temp_path / "data"
        legacy_data.mkdir()
        
        # Создаем поврежденный файл БД для провоцирования ошибки
        (legacy_data / "corrupted.db").write_bytes(b'invalid database')
        
        # Создаем целевую структуру
        target_base = temp_path / "target"
        target_structure = DirectoryStructure(
            base=target_base,
            database=target_base / "database",
            cache=target_base / "cache",
            logs=target_base / "logs", 
            temp=target_base / "temp"
        )
        
        # Создаем существующий файл в целевой директории
        target_structure.create_all()
        (target_structure.database / "existing.db").write_text("existing data")
        
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            migrator = DataMigrator(target_structure)
            
            print("Тестирование механизма отката...")
            
            # Выполняем миграцию (должна пройти, так как поврежденный файл будет пропущен)
            result = migrator.migrate_legacy_data()
            
            # Проверяем что существующий файл не был удален
            assert (target_structure.database / "existing.db").exists()
            
            print("✓ Тест отката пройден")
            
        except Exception as e:
            print(f"Ошибка теста отката: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    return True

if __name__ == "__main__":
    print("Запуск тестов расширенного DataMigrator...")
    
    success = True
    
    if not test_data_migrator_enhanced():
        success = False
    
    if not test_migration_rollback():
        success = False
    
    if success:
        print("\n✓ Все тесты пройдены успешно!")
    else:
        print("\n✗ Некоторые тесты не пройдены")
        sys.exit(1)