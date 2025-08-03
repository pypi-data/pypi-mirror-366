#!/usr/bin/env python3
"""
Тест для проверки поддержки Windows APPDATA директорий.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.user_data_manager import (
    PlatformDetector, Platform, PlatformConfig, UserDataManager
)


def test_windows_appdata_detection():
    """Тестирует определение APPDATA директории на Windows."""
    print("=== Тест определения APPDATA директории ===")
    
    detector = PlatformDetector()
    
    # Мокаем Windows платформу
    with patch.object(detector, 'get_platform', return_value=Platform.WINDOWS):
        # Тест с установленной APPDATA
        with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}):
            data_dir = detector.get_user_data_dir()
            print(f"APPDATA директория: {data_dir}")
            assert str(data_dir) == 'C:\\Users\\Test\\AppData\\Roaming'
        
        # Тест без APPDATA, но с USERPROFILE
        with patch.dict(os.environ, {'USERPROFILE': 'C:\\Users\\Test'}, clear=True):
            with patch('pathlib.Path.exists', return_value=True):
                data_dir = detector.get_user_data_dir()
                print(f"USERPROFILE/AppData/Roaming директория: {data_dir}")
                expected = Path('C:\\Users\\Test') / 'AppData' / 'Roaming'
                assert data_dir == expected
        
        # Тест с HOMEDRIVE и HOMEPATH
        with patch.dict(os.environ, {
            'HOMEDRIVE': 'C:',
            'HOMEPATH': '\\Users\\Test'
        }, clear=True):
            with patch('pathlib.Path.exists', return_value=True):
                data_dir = detector.get_user_data_dir()
                print(f"HOMEDRIVE/HOMEPATH/AppData/Roaming директория: {data_dir}")
                expected = Path('C:\\Users\\Test') / 'AppData' / 'Roaming'
                assert data_dir == expected
    
    print("✓ Тест определения APPDATA директории прошел успешно")


def test_windows_cache_directory():
    """Тестирует определение директории кеша на Windows."""
    print("\n=== Тест определения директории кеша Windows ===")
    
    detector = PlatformDetector()
    
    with patch.object(detector, 'get_platform', return_value=Platform.WINDOWS):
        # Тест с LOCALAPPDATA
        with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'}):
            with patch('pathlib.Path.exists', return_value=True):
                cache_dir = detector.get_user_cache_dir()
                print(f"LOCALAPPDATA директория: {cache_dir}")
                assert str(cache_dir) == 'C:\\Users\\Test\\AppData\\Local'
        
        # Тест fallback к APPDATA
        with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}, clear=True):
            with patch('pathlib.Path.exists', return_value=True):
                cache_dir = detector.get_user_cache_dir()
                print(f"Fallback к APPDATA: {cache_dir}")
                assert str(cache_dir) == 'C:\\Users\\Test\\AppData\\Roaming'
    
    print("✓ Тест определения директории кеша прошел успешно")


def test_windows_directory_structure():
    """Тестирует создание структуры директорий для Windows."""
    print("\n=== Тест структуры директорий Windows ===")
    
    with patch('sys.platform', 'win32'):
        with patch.dict(os.environ, {
            'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming',
            'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'
        }):
            config = PlatformConfig.for_current_platform()
            
            print(f"Платформа: {config.platform}")
            print(f"Базовая директория: {config.base_directory}")
            print(f"Директория кеша: {config.cache_directory}")
            print(f"Директория логов: {config.logs_directory}")
            
            # Проверяем правильность путей
            assert config.platform == Platform.WINDOWS
            assert 'offers-check-marketplaces' in str(config.base_directory)
            assert 'AppData' in str(config.base_directory)
            assert config.cache_directory is not None
            assert config.logs_directory is not None
    
    print("✓ Тест структуры директорий Windows прошел успешно")


def test_windows_fallback_scenarios():
    """Тестирует fallback сценарии для Windows."""
    print("\n=== Тест fallback сценариев Windows ===")
    
    detector = PlatformDetector()
    
    with patch.object(detector, 'get_platform', return_value=Platform.WINDOWS):
        # Тест когда все переменные окружения недоступны
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path('C:\\Users\\Test')
                data_dir = detector.get_user_data_dir()
                print(f"Fallback к Path.home(): {data_dir}")
                expected = Path('C:\\Users\\Test') / 'AppData' / 'Roaming'
                assert data_dir == expected
        
        # Тест когда директории не существуют
        with patch.dict(os.environ, {'APPDATA': 'C:\\NonExistent\\Path'}):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.home') as mock_home:
                    mock_home.return_value = Path('C:\\Users\\Test')
                    data_dir = detector.get_user_data_dir()
                    print(f"Fallback при несуществующих директориях: {data_dir}")
                    expected = Path('C:\\Users\\Test') / 'AppData' / 'Roaming'
                    assert data_dir == expected
    
    print("✓ Тест fallback сценариев прошел успешно")


if __name__ == "__main__":
    try:
        test_windows_appdata_detection()
        test_windows_cache_directory()
        test_windows_directory_structure()
        test_windows_fallback_scenarios()
        print("\n🎉 Все тесты Windows APPDATA поддержки прошли успешно!")
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)