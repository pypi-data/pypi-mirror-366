"""
Модуль для управления лицензионными ключами
"""
import os
import requests
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class LicenseManager:
    """Менеджер для проверки и управления лицензионными ключами"""
    
    def __init__(self, license_key: Optional[str] = None):
        """
        Инициализация менеджера лицензий
        
        Args:
            license_key: Лицензионный ключ (если не указан, будет загружен из переменных окружения или файла)
        """
        self.license_key = license_key or self._load_license_key()
        self.api_base_url = "http://utils-licensegateproxy-yodjsn-513a08-83-222-22-34.traefik.me:1884/license/a2029"
        self.cache_file = Path("data/.license_cache.json")
        self.cache_duration = timedelta(hours=1)  # Кэшируем результат на 1 час
        
    def _load_license_key(self) -> Optional[str]:
        """
        Загружает лицензионный ключ из различных источников
        
        Returns:
            Лицензионный ключ или None если не найден
        """
        # Сначала проверяем переменные окружения
        license_key = os.getenv('LICENSE_KEY')
        if license_key:
            logger.info("Лицензионный ключ загружен из переменных окружения")
            return license_key
            
        # Проверяем файл конфигурации
        config_file = Path("data/.license_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    license_key = config.get('license_key')
                    if license_key:
                        logger.info("Лицензионный ключ загружен из файла конфигурации")
                        return license_key
            except Exception as e:
                logger.warning(f"Ошибка при чтении файла конфигурации лицензии: {e}")
        
        # Лицензионный ключ не найден
        logger.warning("Лицензионный ключ не найден ни в переменных окружения, ни в файле конфигурации")
        return None
    
    def _load_cache(self) -> Optional[Dict]:
        """
        Загружает кэшированный результат проверки лицензии
        
        Returns:
            Кэшированные данные или None если кэш недействителен
        """
        if not self.cache_file.exists():
            return None
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Проверяем, что кэш для того же ключа
            cached_license_key = cache_data.get('license_data', {}).get('license_key')
            if cached_license_key != self.license_key:
                logger.debug("Кэш для другого лицензионного ключа, игнорируем")
                return None
                
            # Проверяем, не истек ли кэш
            cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
            if datetime.now() - cached_time < self.cache_duration:
                logger.debug("Используется кэшированный результат проверки лицензии")
                return cache_data
                
        except Exception as e:
            logger.warning(f"Ошибка при чтении кэша лицензии: {e}")
            
        return None
    
    def _save_cache(self, license_data: Dict) -> None:
        """
        Сохраняет результат проверки лицензии в кэш
        
        Args:
            license_data: Данные лицензии для кэширования
        """
        try:
            # Создаем директорию если не существует
            self.cache_file.parent.mkdir(exist_ok=True)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'license_data': license_data
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.debug("Результат проверки лицензии сохранен в кэш")
            
        except Exception as e:
            logger.warning(f"Ошибка при сохранении кэша лицензии: {e}")
    
    def verify_license(self, use_cache: bool = True) -> Tuple[bool, Dict]:
        """
        Проверяет действительность лицензионного ключа
        
        Args:
            use_cache: Использовать ли кэшированный результат
            
        Returns:
            Tuple[bool, Dict]: (is_valid, license_info)
        """
        if not self.license_key:
            logger.error("Лицензионный ключ не найден")
            return False, {
                "error": "LICENSE_KEY_NOT_FOUND",
                "message": "Лицензионный ключ не найден",
                "user_message": "Необходимо указать лицензионный ключ для использования системы"
            }
        
        # Проверяем кэш если разрешено
        if use_cache:
            cached_result = self._load_cache()
            if cached_result:
                license_data = cached_result['license_data']
                return license_data.get('valid', False), license_data
        
        # Выполняем запрос к API
        try:
            url = f"{self.api_base_url}/{self.license_key}/verify"
            logger.info(f"Проверка лицензии через API: {url}")
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            license_data = response.json()
            
            # Добавляем дополнительную информацию
            license_data['checked_at'] = datetime.now().isoformat()
            license_data['license_key'] = self.license_key
            
            # Сохраняем в кэш
            self._save_cache(license_data)
            
            is_valid = license_data.get('valid', False)
            
            if is_valid:
                logger.info("Лицензия действительна")
            else:
                logger.warning("Лицензия недействительна")
                
            return is_valid, license_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при проверке лицензии: {e}")
            return False, {
                "error": "LICENSE_CHECK_FAILED",
                "message": f"Ошибка при проверке лицензии: {str(e)}",
                "user_message": "Не удалось проверить лицензию. Проверьте подключение к интернету",
                "exception": str(e)
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке лицензии: {e}")
            return False, {
                "error": "UNEXPECTED_ERROR",
                "message": f"Неожиданная ошибка: {str(e)}",
                "user_message": "Произошла неожиданная ошибка при проверке лицензии",
                "exception": str(e)
            }
    
    def get_license_info(self) -> Dict:
        """
        Получает информацию о текущей лицензии
        
        Returns:
            Словарь с информацией о лицензии
        """
        is_valid, license_data = self.verify_license()
        
        return {
            "license_key": self.license_key,
            "is_valid": is_valid,
            "license_data": license_data,
            "cache_file": str(self.cache_file),
            "api_url": f"{self.api_base_url}/{self.license_key}/verify"
        }
    
    def set_license_key(self, license_key: str, save_to_config: bool = True) -> bool:
        """
        Устанавливает новый лицензионный ключ
        
        Args:
            license_key: Новый лицензионный ключ
            save_to_config: Сохранить ли ключ в файл конфигурации
            
        Returns:
            True если ключ успешно установлен и проверен
        """
        old_key = self.license_key
        self.license_key = license_key
        
        # Проверяем новый ключ
        is_valid, license_data = self.verify_license(use_cache=False)
        
        if is_valid:
            if save_to_config:
                self._save_license_to_config(license_key)
            logger.info("Новый лицензионный ключ успешно установлен")
            return True
        else:
            # Возвращаем старый ключ если новый недействителен
            self.license_key = old_key
            logger.error("Новый лицензионный ключ недействителен")
            # НЕ сохраняем недействительный ключ в конфигурацию
            return False
    
    def _save_license_to_config(self, license_key: str) -> None:
        """
        Сохраняет лицензионный ключ в файл конфигурации
        
        Args:
            license_key: Лицензионный ключ для сохранения
        """
        try:
            config_file = Path("data/.license_config.json")
            config_file.parent.mkdir(exist_ok=True)
            
            config = {
                "license_key": license_key,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info("Лицензионный ключ сохранен в файл конфигурации")
            
        except Exception as e:
            logger.warning(f"Ошибка при сохранении лицензионного ключа: {e}")

# Глобальный экземпляр менеджера лицензий
license_manager = LicenseManager()

def check_license() -> Tuple[bool, Dict]:
    """
    Удобная функция для проверки лицензии
    
    Returns:
        Tuple[bool, Dict]: (is_valid, license_info)
    """
    return license_manager.verify_license()

def require_valid_license():
    """
    Декоратор для функций, требующих действительную лицензию
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            is_valid, license_info = check_license()
            if not is_valid:
                raise Exception(f"Недействительная лицензия: {license_info.get('message', 'Неизвестная ошибка')}")
            return func(*args, **kwargs)
        return wrapper
    return decorator