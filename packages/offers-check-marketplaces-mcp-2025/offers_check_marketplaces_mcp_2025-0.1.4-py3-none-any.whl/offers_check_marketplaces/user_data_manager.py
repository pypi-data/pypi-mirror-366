"""
Модуль для управления пользовательскими данными MCP сервера.
Автоматически определяет подходящие директории для каждой ОС.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Поддерживаемые платформы."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class UserDataError(Exception):
    """Базовое исключение для операций с пользовательскими данными."""
    
    def __init__(self, message: str, suggested_solution: Optional[str] = None, 
                 recovery_action: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.suggested_solution = suggested_solution
        self.recovery_action = recovery_action
    
    def get_user_friendly_message(self) -> str:
        """Возвращает пользовательское сообщение об ошибке с предложениями по решению."""
        msg = f"Ошибка управления данными: {self.message}"
        
        if self.suggested_solution:
            msg += f"\n\nРекомендуемое решение: {self.suggested_solution}"
        
        if self.recovery_action:
            msg += f"\n\nДействие для восстановления: {self.recovery_action}"
        
        return msg


class DirectoryCreationError(UserDataError):
    """Исключение при ошибке создания директории."""
    
    def __init__(self, message: str, directory_path: Optional[Path] = None, 
                 platform: Optional[Platform] = None):
        self.directory_path = directory_path
        self.platform = platform
        
        # Определяем решение на основе платформы и типа ошибки
        suggested_solution = self._get_platform_specific_solution(message, platform)
        recovery_action = self._get_recovery_action(message, directory_path)
        
        super().__init__(message, suggested_solution, recovery_action)
    
    def _get_platform_specific_solution(self, message: str, platform: Optional[Platform]) -> str:
        """Возвращает решение, специфичное для платформы."""
        if "Permission denied" in message or "Нет прав" in message:
            if platform == Platform.WINDOWS:
                return ("Запустите программу от имени администратора или выберите другую директорию. "
                       "Проверьте права доступа к папке в свойствах.")
            elif platform in [Platform.LINUX, Platform.MACOS]:
                return ("Выполните команду: sudo chmod 755 <путь_к_директории> "
                       "или выберите директорию в домашней папке пользователя.")
            else:
                return "Проверьте права доступа к директории или выберите другое расположение."
        
        elif "No space left" in message or "Недостаточно места" in message:
            return ("Освободите место на диске или выберите другой диск для хранения данных. "
                   "Рекомендуется минимум 100 MB свободного места.")
        
        elif "File name too long" in message or "Слишком длинное имя" in message:
            return ("Выберите директорию с более коротким путем или переместите проект "
                   "ближе к корню диска.")
        
        elif "Read-only file system" in message or "только для чтения" in message:
            return ("Файловая система доступна только для чтения. Выберите другой диск "
                   "или проверьте настройки монтирования.")
        
        else:
            return "Проверьте доступность директории и права доступа."
    
    def _get_recovery_action(self, message: str, directory_path: Optional[Path]) -> str:
        """Возвращает действие для восстановления."""
        if directory_path:
            return (f"Попробуйте установить переменную окружения OFFERS_CHECK_DATA_DIR "
                   f"с альтернативным путем, например: "
                   f"OFFERS_CHECK_DATA_DIR={Path.home() / 'offers-check-data'}")
        else:
            return ("Перезапустите программу или обратитесь к системному администратору "
                   "если проблема повторяется.")


class PermissionError(UserDataError):
    """Исключение при недостаточных правах доступа."""
    
    def __init__(self, message: str, directory_path: Optional[Path] = None, 
                 access_type: str = "read/write", platform: Optional[Platform] = None):
        self.directory_path = directory_path
        self.access_type = access_type
        self.platform = platform
        
        suggested_solution = self._get_permission_solution(access_type, platform, directory_path)
        recovery_action = self._get_permission_recovery(directory_path)
        
        super().__init__(message, suggested_solution, recovery_action)
    
    def _get_permission_solution(self, access_type: str, platform: Optional[Platform], 
                               directory_path: Optional[Path]) -> str:
        """Возвращает решение для проблем с правами доступа."""
        if platform == Platform.WINDOWS:
            return (f"Для Windows:\n"
                   f"1. Щелкните правой кнопкой на папке {directory_path or '<директория>'}\n"
                   f"2. Выберите 'Свойства' -> 'Безопасность'\n"
                   f"3. Убедитесь что у вашего пользователя есть права на {access_type}\n"
                   f"4. Или запустите программу от имени администратора")
        
        elif platform in [Platform.LINUX, Platform.MACOS]:
            if directory_path:
                return (f"Для {platform.value}:\n"
                       f"1. Выполните: chmod 755 '{directory_path}'\n"
                       f"2. Или: sudo chown $USER '{directory_path}'\n"
                       f"3. Проверьте владельца: ls -la '{directory_path.parent}'")
            else:
                return (f"Для {platform.value}:\n"
                       f"1. Выполните: chmod 755 <путь_к_директории>\n"
                       f"2. Или: sudo chown $USER <путь_к_директории>")
        
        else:
            return ("Проверьте права доступа к директории. Убедитесь что у вашего "
                   "пользователя есть права на чтение и запись.")
    
    def _get_permission_recovery(self, directory_path: Optional[Path]) -> str:
        """Возвращает действие для восстановления прав доступа."""
        return (f"Альтернативное решение: установите переменную окружения "
               f"OFFERS_CHECK_DATA_DIR с путем к директории, к которой у вас есть доступ, "
               f"например: OFFERS_CHECK_DATA_DIR={Path.home() / 'my-offers-data'}")


class MigrationError(UserDataError):
    """Исключение при ошибке миграции данных."""
    
    def __init__(self, message: str, source_path: Optional[Path] = None, 
                 target_path: Optional[Path] = None, files_affected: Optional[list] = None):
        self.source_path = source_path
        self.target_path = target_path
        self.files_affected = files_affected or []
        
        suggested_solution = self._get_migration_solution(message)
        recovery_action = self._get_migration_recovery(source_path, target_path)
        
        super().__init__(message, suggested_solution, recovery_action)
    
    def _get_migration_solution(self, message: str) -> str:
        """Возвращает решение для проблем миграции."""
        if "Недостаточно места" in message or "No space left" in message:
            return ("Освободите место на диске или выберите другое расположение для данных. "
                   "Миграция требует дополнительное место для безопасного копирования файлов.")
        
        elif "Permission denied" in message or "Нет прав" in message:
            return ("Убедитесь что у вас есть права на чтение исходной директории ./data "
                   "и запись в целевую директорию. Возможно потребуются права администратора.")
        
        elif "целостности" in message or "integrity" in message:
            return ("Проверьте целостность исходных файлов. Возможно некоторые файлы "
                   "повреждены или заблокированы другими процессами.")
        
        else:
            return ("Проверьте доступность исходной и целевой директорий. "
                   "Убедитесь что файлы не используются другими программами.")
    
    def _get_migration_recovery(self, source_path: Optional[Path], 
                              target_path: Optional[Path]) -> str:
        """Возвращает действие для восстановления после ошибки миграции."""
        recovery = "Варианты восстановления:\n"
        
        if source_path and source_path.exists():
            recovery += f"1. Исходные данные сохранены в {source_path}\n"
        
        if target_path:
            recovery += f"2. Проверьте содержимое {target_path} и удалите поврежденные файлы\n"
        
        recovery += ("3. Попробуйте миграцию снова после устранения проблем\n"
                    "4. Или скопируйте файлы вручную из ./data в новое расположение")
        
        return recovery


class DiskSpaceError(UserDataError):
    """Исключение при недостатке места на диске."""
    
    def __init__(self, message: str, required_space_mb: float, available_space_mb: float, 
                 directory_path: Optional[Path] = None):
        self.required_space_mb = required_space_mb
        self.available_space_mb = available_space_mb
        self.directory_path = directory_path
        
        suggested_solution = self._get_space_solution()
        recovery_action = self._get_space_recovery()
        
        super().__init__(message, suggested_solution, recovery_action)
    
    def _get_space_solution(self) -> str:
        """Возвращает решение для проблем с местом на диске."""
        return (f"Требуется {self.required_space_mb:.1f} MB, доступно {self.available_space_mb:.1f} MB.\n"
               f"Решения:\n"
               f"1. Освободите место на диске (удалите ненужные файлы)\n"
               f"2. Очистите корзину и временные файлы\n"
               f"3. Выберите другой диск с большим количеством свободного места")
    
    def _get_space_recovery(self) -> str:
        """Возвращает действие для восстановления места на диске."""
        return (f"Установите переменную OFFERS_CHECK_DATA_DIR с путем к диску "
               f"с достаточным количеством свободного места, например:\n"
               f"OFFERS_CHECK_DATA_DIR=D:\\offers-check-data (Windows)\n"
               f"OFFERS_CHECK_DATA_DIR=/mnt/storage/offers-check-data (Linux)")


class ValidationError(UserDataError):
    """Исключение при ошибке валидации данных или путей."""
    
    def __init__(self, message: str, validation_type: str = "general", 
                 invalid_value: Optional[str] = None):
        self.validation_type = validation_type
        self.invalid_value = invalid_value
        
        suggested_solution = self._get_validation_solution(validation_type, invalid_value)
        recovery_action = self._get_validation_recovery(validation_type)
        
        super().__init__(message, suggested_solution, recovery_action)
    
    def _get_validation_solution(self, validation_type: str, invalid_value: Optional[str]) -> str:
        """Возвращает решение для проблем валидации."""
        if validation_type == "path":
            return (f"Некорректный путь: {invalid_value or '<не указан>'}.\n"
                   f"Убедитесь что:\n"
                   f"1. Путь существует и доступен\n"
                   f"2. Путь не содержит недопустимых символов\n"
                   f"3. Путь не указывает на системную директорию")
        
        elif validation_type == "environment":
            return (f"Некорректная переменная окружения: {invalid_value or '<не указана>'}.\n"
                   f"Проверьте правильность установки переменной OFFERS_CHECK_DATA_DIR")
        
        elif validation_type == "structure":
            return ("Некорректная структура директорий.\n"
                   "Проверьте что все необходимые поддиректории могут быть созданы.")
        
        else:
            return "Проверьте корректность входных данных и повторите операцию."
    
    def _get_validation_recovery(self, validation_type: str) -> str:
        """Возвращает действие для восстановления после ошибки валидации."""
        if validation_type == "path":
            return ("Используйте абсолютный путь к существующей директории или "
                   "позвольте программе использовать стандартное расположение.")
        
        elif validation_type == "environment":
            return ("Удалите переменную OFFERS_CHECK_DATA_DIR чтобы использовать "
                   "стандартное расположение: unset OFFERS_CHECK_DATA_DIR")
        
        else:
            return "Перезапустите программу с корректными параметрами."


@dataclass
class DirectoryStructure:
    """Структура директорий для пользовательских данных."""
    base: Path
    database: Path
    cache: Path
    logs: Path
    temp: Path
    
    def validate(self) -> bool:
        """Проверяет корректность структуры директорий."""
        try:
            # Проверяем что все обязательные пути определены
            if not all([self.base, self.database, self.logs, self.temp]):
                logger.error("Не все обязательные пути определены в структуре директорий")
                return False
            
            # Проверяем что пути являются объектами Path
            for name, path in [("base", self.base), ("database", self.database), 
                             ("cache", self.cache), ("logs", self.logs), ("temp", self.temp)]:
                if not isinstance(path, Path):
                    logger.error(f"Путь {name} должен быть объектом Path, получен {type(path)}")
                    return False
            
            # Проверяем что database, logs и temp являются подпутями базовой директории
            # cache может быть в отдельном расположении (например, на macOS)
            for name, path in [("database", self.database), ("logs", self.logs), ("temp", self.temp)]:
                try:
                    # Используем resolve() для корректного сравнения путей
                    base_resolved = self.base.resolve()
                    path_resolved = path.resolve()
                    
                    # Проверяем что путь начинается с базовой директории
                    if not str(path_resolved).startswith(str(base_resolved)):
                        logger.warning(f"Путь {name} ({path}) не является подпутем базовой директории {self.base}")
                        # Для некоторых платформ это может быть нормально (например, cache на macOS)
                        if name != "cache":
                            return False
                except (OSError, ValueError) as e:
                    logger.warning(f"Не удалось разрешить путь {name}: {e}")
                    # Продолжаем валидацию, так как пути могут не существовать
            
            return True
        except Exception as e:
            logger.error(f"Ошибка валидации структуры директорий: {e}")
            return False
    
    def create_all(self) -> bool:
        """Создает все директории в структуре с улучшенной обработкой ошибок."""
        created_dirs = []
        
        try:
            # Создаем директории в правильном порядке
            directories = [
                ("base", self.base),
                ("database", self.database),
                ("cache", self.cache),
                ("logs", self.logs),
                ("temp", self.temp)
            ]
            
            for name, path in directories:
                if path is None:
                    logger.warning(f"Пропускаем создание директории {name}: путь не определен")
                    continue
                
                try:
                    # Создаем директорию с родительскими директориями
                    path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(path)
                    logger.debug(f"Создана директория {name}: {path}")
                    
                    # Проверяем что директория действительно создалась
                    if not path.exists() or not path.is_dir():
                        raise DirectoryCreationError(f"Директория {name} не была создана: {path}")
                        
                except OSError as e:
                    if e.errno == 13:  # Permission denied
                        raise PermissionError(
                            f"Нет прав для создания директории {name} ({path}): {e}",
                            directory_path=path,
                            access_type="write",
                            platform=self.config.platform if hasattr(self, 'config') else None
                        )
                    elif e.errno == 28:  # No space left on device
                        # Получаем информацию о месте на диске для более точной ошибки
                        try:
                            stat = shutil.disk_usage(path.parent)
                            available_mb = stat.free / (1024 * 1024)
                            raise DiskSpaceError(
                                f"Недостаточно места для создания директории {name} ({path})",
                                required_space_mb=100.0,  # Минимальное требование
                                available_space_mb=available_mb,
                                directory_path=path
                            )
                        except:
                            raise DirectoryCreationError(
                                f"Недостаточно места для создания директории {name} ({path}): {e}",
                                directory_path=path,
                                platform=self.config.platform if hasattr(self, 'config') else None
                            )
                    elif e.errno == 36:  # File name too long
                        raise ValidationError(
                            f"Слишком длинное имя для директории {name} ({path}): {e}",
                            validation_type="path",
                            invalid_value=str(path)
                        )
                    else:
                        raise DirectoryCreationError(
                            f"Ошибка создания директории {name} ({path}): {e}",
                            directory_path=path,
                            platform=self.config.platform if hasattr(self, 'config') else None
                        )
            
            logger.info(f"Успешно создана структура из {len(created_dirs)} директорий")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания структуры директорий: {e}")
            
            # Пытаемся откатить созданные директории при ошибке
            self._rollback_created_directories(created_dirs)
            return False
    
    def _rollback_created_directories(self, created_dirs: list):
        """Откатывает созданные директории при ошибке."""
        if not created_dirs:
            return
            
        logger.warning("Попытка отката созданных директорий после ошибки")
        
        # Удаляем в обратном порядке
        for path in reversed(created_dirs):
            try:
                if path.exists() and path.is_dir():
                    # Удаляем только если директория пустая
                    if not any(path.iterdir()):
                        path.rmdir()
                        logger.debug(f"Удалена пустая директория при откате: {path}")
                    else:
                        logger.debug(f"Директория не пустая, пропускаем удаление: {path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить директорию при откате {path}: {e}")


@dataclass
class PlatformConfig:
    """Конфигурация для конкретной платформы."""
    platform: Platform
    base_directory: Path
    cache_directory: Optional[Path] = None
    logs_directory: Optional[Path] = None
    permissions: Dict[str, int] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = {}
    
    @classmethod
    def for_current_platform(cls) -> 'PlatformConfig':
        """Создает конфигурацию для текущей платформы."""
        detector = PlatformDetector()
        platform = detector.get_platform()
        
        if platform == Platform.WINDOWS:
            base = detector.get_user_data_dir() / "offers-check-marketplaces"
            cache_base = detector.get_user_cache_dir() / "offers-check-marketplaces"
            return cls(
                platform=platform,
                base_directory=base,
                cache_directory=cache_base / "cache",
                logs_directory=base / "logs",
                permissions={}  # Windows использует стандартные права
            )
        elif platform == Platform.MACOS:
            base = detector.get_user_data_dir() / "offers-check-marketplaces"
            cache = detector.get_user_cache_dir() / "offers-check-marketplaces"
            logs = Path.home() / "Library" / "Logs" / "offers-check-marketplaces"
            return cls(
                platform=platform,
                base_directory=base,
                cache_directory=cache,
                logs_directory=logs,
                permissions={"directory": 0o755, "file": 0o644}
            )
        elif platform == Platform.LINUX:
            base = detector.get_user_data_dir() / "offers-check-marketplaces"
            cache = detector.get_user_cache_dir() / "offers-check-marketplaces"
            return cls(
                platform=platform,
                base_directory=base,
                cache_directory=cache,
                logs_directory=base / "logs",
                permissions={"directory": 0o755, "file": 0o644}
            )
        else:
            # Fallback для неизвестных платформ
            base = Path.home() / ".offers-check-marketplaces"
            return cls(
                platform=platform,
                base_directory=base,
                cache_directory=base / "cache",
                logs_directory=base / "logs",
                permissions={"directory": 0o755, "file": 0o644}
            )


class PlatformDetector:
    """Определяет текущую платформу и стандартные пути."""
    
    def get_platform(self) -> Platform:
        """Определяет текущую операционную систему."""
        system = sys.platform.lower()
        
        if system.startswith('win'):
            return Platform.WINDOWS
        elif system == 'darwin':
            return Platform.MACOS
        elif system.startswith('linux'):
            return Platform.LINUX
        else:
            logger.warning(f"Неизвестная платформа: {system}")
            return Platform.UNKNOWN
    
    def get_user_data_dir(self) -> Path:
        """Получает стандартную директорию данных пользователя."""
        platform = self.get_platform()
        
        if platform == Platform.WINDOWS:
            return self._get_windows_appdata_dir()
        
        elif platform == Platform.MACOS:
            # macOS использует Application Support
            return Path.home() / "Library" / "Application Support"
        
        elif platform == Platform.LINUX:
            # Linux использует XDG Base Directory
            xdg_data_home = os.environ.get('XDG_DATA_HOME')
            if xdg_data_home:
                return Path(xdg_data_home)
            else:
                return Path.home() / ".local" / "share"
        
        else:
            # Fallback для неизвестных платформ
            return Path.home() / ".local" / "share"
    
    def _get_windows_appdata_dir(self) -> Path:
        """Получает директорию APPDATA для Windows с обработкой ошибок."""
        # Пробуем получить APPDATA из переменных окружения
        appdata = os.environ.get('APPDATA')
        if appdata and Path(appdata).exists():
            logger.debug(f"Используется APPDATA: {appdata}")
            return Path(appdata)
        
        # Пробуем USERPROFILE + AppData\Roaming
        userprofile = os.environ.get('USERPROFILE')
        if userprofile:
            appdata_path = Path(userprofile) / "AppData" / "Roaming"
            if appdata_path.exists():
                logger.debug(f"Используется USERPROFILE/AppData/Roaming: {appdata_path}")
                return appdata_path
        
        # Пробуем HOMEDRIVE + HOMEPATH + AppData\Roaming
        homedrive = os.environ.get('HOMEDRIVE', 'C:')
        homepath = os.environ.get('HOMEPATH', '')
        if homepath:
            appdata_path = Path(homedrive + homepath) / "AppData" / "Roaming"
            if appdata_path.exists():
                logger.debug(f"Используется HOMEDRIVE/HOMEPATH/AppData/Roaming: {appdata_path}")
                return appdata_path
        
        # Последний fallback - используем Path.home()
        fallback_path = Path.home() / "AppData" / "Roaming"
        logger.warning(f"APPDATA недоступна, используется fallback: {fallback_path}")
        return fallback_path
    
    def get_user_cache_dir(self) -> Path:
        """Получает стандартную директорию кеша пользователя."""
        platform = self.get_platform()
        
        if platform == Platform.WINDOWS:
            return self._get_windows_cache_dir()
        
        elif platform == Platform.MACOS:
            # macOS имеет отдельную директорию для кеша
            return Path.home() / "Library" / "Caches"
        
        elif platform == Platform.LINUX:
            # Linux использует XDG_CACHE_HOME
            xdg_cache_home = os.environ.get('XDG_CACHE_HOME')
            if xdg_cache_home:
                return Path(xdg_cache_home)
            else:
                return Path.home() / ".cache"
        
        else:
            # Fallback
            return Path.home() / ".cache"
    
    def _get_windows_cache_dir(self) -> Path:
        """Получает директорию кеша для Windows."""
        # В Windows кеш обычно хранится в той же APPDATA директории
        # Но можно использовать LOCALAPPDATA для временных данных
        localappdata = os.environ.get('LOCALAPPDATA')
        if localappdata and Path(localappdata).exists():
            logger.debug(f"Используется LOCALAPPDATA для кеша: {localappdata}")
            return Path(localappdata)
        
        # Fallback к обычной APPDATA
        return self._get_windows_appdata_dir()
    
    def get_user_logs_dir(self) -> Path:
        """Получает стандартную директорию логов пользователя."""
        platform = self.get_platform()
        
        if platform == Platform.WINDOWS:
            # Windows использует ту же APPDATA директорию для логов
            return self._get_windows_appdata_dir()
        
        elif platform == Platform.MACOS:
            # macOS имеет отдельную директорию для логов
            return Path.home() / "Library" / "Logs"
        
        elif platform == Platform.LINUX:
            # Linux обычно использует ту же директорию что и данные
            return self.get_user_data_dir()
        
        else:
            # Fallback
            return self.get_user_data_dir()
    
    def supports_xdg_base_directory(self) -> bool:
        """Проверяет поддержку XDG Base Directory."""
        return self.get_platform() == Platform.LINUX


class DirectoryManager:
    """Управляет созданием и валидацией директорий."""
    
    def __init__(self, platform_config: PlatformConfig):
        self.config = platform_config
    
    def create_directory_structure(self, base_path: Path) -> DirectoryStructure:
        """Создает полную структуру директорий с улучшенной обработкой ошибок."""
        try:
            logger.info("=" * 50)
            logger.info("СОЗДАНИЕ СТРУКТУРЫ ДИРЕКТОРИЙ")
            logger.info("=" * 50)
            logger.info(f"Целевая директория: {base_path}")
            logger.info(f"Платформа: {self.config.platform.value}")
            
            # Валидируем базовый путь перед созданием структуры
            logger.debug("Валидация базового пути...")
            self._validate_base_path(base_path)
            logger.debug("✅ Базовый путь валиден")
            
            # Определяем пути для всех директорий согласно конфигурации платформы
            logger.debug("Определение путей для поддиректорий...")
            cache_path = self._resolve_cache_path(base_path)
            logs_path = self._resolve_logs_path(base_path)
            
            structure = DirectoryStructure(
                base=base_path,
                database=base_path / "database",
                cache=cache_path,
                logs=logs_path,
                temp=base_path / "temp"
            )
            
            logger.info("Планируемая структура директорий:")
            logger.info(f"  📁 База:      {structure.base}")
            logger.info(f"  🗄️  БД:        {structure.database}")
            logger.info(f"  💾 Кеш:       {structure.cache}")
            logger.info(f"  📋 Логи:      {structure.logs}")
            logger.info(f"  🗂️  Временные: {structure.temp}")
            
            # Валидируем структуру перед созданием
            logger.debug("Валидация структуры директорий...")
            if not structure.validate():
                raise DirectoryCreationError("Некорректная структура директорий")
            logger.debug("✅ Структура директорий валидна")
            
            # Создаем все директории
            logger.info("Создание директорий...")
            if not structure.create_all():
                raise DirectoryCreationError("Не удалось создать структуру директорий")
            logger.info("✅ Все директории созданы")
            
            # Устанавливаем права доступа для каждой платформы
            logger.debug("Установка прав доступа...")
            self._set_permissions(structure)
            logger.debug("✅ Права доступа установлены")
            
            # Проверяем что все директории доступны после создания
            logger.debug("Проверка доступности созданных директорий...")
            self._verify_structure_access(structure)
            logger.debug("✅ Все директории доступны")
            
            logger.info("✅ СТРУКТУРА ДИРЕКТОРИЙ СОЗДАНА УСПЕШНО")
            logger.info("=" * 50)
            return structure
            
        except (DirectoryCreationError, PermissionError, DiskSpaceError, ValidationError) as e:
            logger.error("❌ ОШИБКА СОЗДАНИЯ СТРУКТУРЫ ДИРЕКТОРИЙ")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Сообщение: {e.message}")
            if hasattr(e, 'suggested_solution') and e.suggested_solution:
                logger.error(f"Решение: {e.suggested_solution}")
            logger.error("=" * 50)
            # Перебрасываем специфичные исключения как есть
            raise
        except Exception as e:
            logger.error("❌ НЕОЖИДАННАЯ ОШИБКА СОЗДАНИЯ СТРУКТУРЫ ДИРЕКТОРИЙ")
            logger.error(f"Ошибка: {e}")
            logger.error("=" * 50)
            raise DirectoryCreationError(f"Не удалось создать структуру директорий: {e}")
    
    def _validate_base_path(self, base_path: Path) -> None:
        """Валидирует базовый путь перед созданием структуры."""
        if not isinstance(base_path, Path):
            raise DirectoryCreationError(f"Базовый путь должен быть объектом Path, получен {type(base_path)}")
        
        # Проверяем что путь не является файлом
        if base_path.exists() and base_path.is_file():
            raise DirectoryCreationError(f"Базовый путь является файлом: {base_path}")
        
        # Проверяем доступность родительской директории
        parent = base_path.parent
        if not parent.exists():
            raise DirectoryCreationError(f"Родительская директория не существует: {parent}")
        
        if not os.access(parent, os.W_OK):
            raise PermissionError(f"Нет прав на запись в родительскую директорию: {parent}")
    
    def _resolve_cache_path(self, base_path: Path) -> Path:
        """Определяет путь для директории кеша согласно конфигурации платформы."""
        if self.config.cache_directory:
            # Используем платформо-специфичный путь кеша
            return self.config.cache_directory
        else:
            # Fallback к поддиректории базового пути
            return base_path / "cache"
    
    def _resolve_logs_path(self, base_path: Path) -> Path:
        """Определяет путь для директории логов согласно конфигурации платформы."""
        if self.config.logs_directory:
            # Используем платформо-специфичный путь логов
            return self.config.logs_directory
        else:
            # Fallback к поддиректории базового пути
            return base_path / "logs"
    
    def _verify_structure_access(self, structure: DirectoryStructure) -> None:
        """Проверяет доступность всех директорий в структуре после создания."""
        directories = [
            ("base", structure.base),
            ("database", structure.database),
            ("cache", structure.cache),
            ("logs", structure.logs),
            ("temp", structure.temp)
        ]
        
        for name, path in directories:
            if path is None:
                continue
                
            if not self.validate_directory_access(path):
                raise DirectoryCreationError(f"Директория {name} недоступна после создания: {path}")
    
    def ensure_directory_exists(self, path: Path) -> bool:
        """Обеспечивает существование директории."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Устанавливаем права доступа если указаны
            if "directory" in self.config.permissions:
                path.chmod(self.config.permissions["directory"])
            
            return True
        except Exception as e:
            logger.error(f"Не удалось создать директорию {path}: {e}")
            return False
    
    def validate_directory_access(self, path: Path) -> bool:
        """Проверяет доступность директории для чтения и записи с подробной диагностикой."""
        try:
            return self._perform_directory_validation(path)
        except Exception as e:
            logger.error(f"Критическая ошибка проверки доступа к директории {path}: {e}")
            return False
    
    def _perform_directory_validation(self, path: Path) -> bool:
        """Выполняет детальную валидацию директории с информативными сообщениями."""
        logger.debug(f"🔍 Начало валидации директории: {path}")
        validation_errors = []
        
        # 1. Проверяем существование пути
        logger.debug(f"  1️⃣  Проверка существования пути...")
        if not path.exists():
            validation_errors.append(f"Директория не существует: {path}")
            logger.debug(f"    ❌ Путь не существует")
            self._log_directory_validation_error(path, validation_errors)
            return False
        logger.debug(f"    ✅ Путь существует")
        
        # 2. Проверяем что это директория, а не файл
        logger.debug(f"  2️⃣  Проверка типа пути...")
        if not path.is_dir():
            validation_errors.append(f"Путь не является директорией: {path}")
            if path.is_file():
                validation_errors.append("Указанный путь является файлом")
                logger.debug(f"    ❌ Путь является файлом")
            elif path.is_symlink():
                validation_errors.append("Указанный путь является символической ссылкой")
                logger.debug(f"    ❌ Путь является символической ссылкой")
            else:
                logger.debug(f"    ❌ Путь не является директорией (неизвестный тип)")
            self._log_directory_validation_error(path, validation_errors)
            return False
        logger.debug(f"    ✅ Путь является директорией")
        
        # 3. Проверяем права на чтение
        logger.debug(f"  3️⃣  Проверка прав на чтение...")
        if not os.access(path, os.R_OK):
            validation_errors.append(f"Нет прав на чтение директории: {path}")
            validation_errors.append(self._get_permission_fix_suggestion(path, "read"))
            logger.debug(f"    ❌ Нет прав на чтение")
        else:
            logger.debug(f"    ✅ Права на чтение есть")
        
        # 4. Проверяем права на запись
        logger.debug(f"  4️⃣  Проверка прав на запись...")
        if not os.access(path, os.W_OK):
            validation_errors.append(f"Нет прав на запись в директорию: {path}")
            validation_errors.append(self._get_permission_fix_suggestion(path, "write"))
            logger.debug(f"    ❌ Нет прав на запись")
        else:
            logger.debug(f"    ✅ Права на запись есть")
        
        # 5. Проверяем права на выполнение (для Unix-систем)
        logger.debug(f"  5️⃣  Проверка прав на выполнение...")
        if not os.access(path, os.X_OK):
            validation_errors.append(f"Нет прав на выполнение для директории: {path}")
            validation_errors.append(self._get_permission_fix_suggestion(path, "execute"))
            logger.debug(f"    ❌ Нет прав на выполнение")
        else:
            logger.debug(f"    ✅ Права на выполнение есть")
        
        # 6. Проверяем свободное место на диске
        logger.debug(f"  6️⃣  Проверка свободного места на диске...")
        disk_space_error = self._check_disk_space(path)
        if disk_space_error:
            validation_errors.append(disk_space_error)
            logger.debug(f"    ❌ Проблемы со свободным местом")
        else:
            logger.debug(f"    ✅ Достаточно свободного места")
        
        # 7. Проверяем возможность создания файлов (практический тест)
        logger.debug(f"  7️⃣  Практический тест записи...")
        write_test_error = self._test_write_access(path)
        if write_test_error:
            validation_errors.append(write_test_error)
            logger.debug(f"    ❌ Практический тест записи не пройден")
        else:
            logger.debug(f"    ✅ Практический тест записи пройден")
        
        # Если есть ошибки, логируем их и возвращаем False
        if validation_errors:
            logger.debug(f"🔍 Валидация директории {path} завершена с ошибками")
            self._log_directory_validation_error(path, validation_errors)
            return False
        
        logger.debug(f"🔍 Директория {path} прошла все проверки доступности ✅")
        return True
    
    def _check_disk_space(self, path: Path, min_space_mb: int = 100) -> Optional[str]:
        """Проверяет свободное место на диске."""
        try:
            stat = shutil.disk_usage(path)
            free_space_mb = stat.free / (1024 * 1024)
            total_space_mb = stat.total / (1024 * 1024)
            used_space_mb = (stat.total - stat.free) / (1024 * 1024)
            
            if free_space_mb < min_space_mb:
                return (f"Недостаточно свободного места на диске: {free_space_mb:.1f} MB "
                       f"(требуется минимум {min_space_mb} MB). "
                       f"Общий объем: {total_space_mb:.1f} MB, "
                       f"использовано: {used_space_mb:.1f} MB")
            
            # Предупреждение если свободного места меньше 1GB
            if free_space_mb < 1024:
                logger.warning(f"Мало свободного места в {path}: {free_space_mb:.1f} MB")
            
            return None
            
        except OSError as e:
            return f"Не удалось проверить свободное место на диске: {e}"
        except Exception as e:
            return f"Ошибка проверки дискового пространства: {e}"
    
    def _test_write_access(self, path: Path) -> Optional[str]:
        """Тестирует возможность записи в директорию созданием временного файла."""
        test_file = path / ".write_test_temp"
        
        try:
            # Пытаемся создать временный файл
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Пытаемся прочитать файл
            with open(test_file, 'r') as f:
                content = f.read()
                if content != "test":
                    return f"Ошибка чтения из директории {path}: содержимое файла не совпадает"
            
            # Удаляем тестовый файл
            test_file.unlink()
            
            return None
            
        except PermissionError as e:
            return f"Нет прав для создания файлов в директории {path}: {e}"
        except OSError as e:
            if e.errno == 28:  # No space left on device
                return f"Нет места на диске для создания файлов в {path}"
            elif e.errno == 30:  # Read-only file system
                return f"Файловая система доступна только для чтения: {path}"
            else:
                return f"Ошибка записи в директорию {path}: {e}"
        except Exception as e:
            return f"Неожиданная ошибка тестирования записи в {path}: {e}"
        finally:
            # Убеждаемся что тестовый файл удален
            try:
                if test_file.exists():
                    test_file.unlink()
            except Exception:
                pass  # Игнорируем ошибки удаления
    
    def _get_permission_fix_suggestion(self, path: Path, access_type: str) -> str:
        """Возвращает предложение по исправлению прав доступа."""
        platform = self.config.platform
        
        if platform == Platform.WINDOWS:
            return (f"Для Windows: проверьте права доступа к папке {path} в свойствах папки. "
                   f"Убедитесь что у вашего пользователя есть права на {access_type}.")
        
        elif platform in [Platform.LINUX, Platform.MACOS]:
            if access_type == "read":
                return f"Для исправления выполните: chmod +r '{path}'"
            elif access_type == "write":
                return f"Для исправления выполните: chmod +w '{path}'"
            elif access_type == "execute":
                return f"Для исправления выполните: chmod +x '{path}'"
            else:
                return f"Для исправления выполните: chmod 755 '{path}'"
        
        else:
            return f"Проверьте права доступа к директории {path}"
    
    def _log_directory_validation_error(self, path: Path, errors: list):
        """Логирует ошибки валидации директории с подробной информацией."""
        logger.error(f"Директория {path} не прошла проверку доступности:")
        for i, error in enumerate(errors, 1):
            logger.error(f"  {i}. {error}")
        
        # Добавляем дополнительную диагностическую информацию
        try:
            if path.exists():
                stat_info = path.stat()
                logger.error(f"Дополнительная информация о директории:")
                logger.error(f"  - Права доступа: {oct(stat_info.st_mode)}")
                logger.error(f"  - Владелец: UID {stat_info.st_uid}")
                logger.error(f"  - Группа: GID {stat_info.st_gid}")
                logger.error(f"  - Размер: {stat_info.st_size} байт")
        except Exception as e:
            logger.error(f"Не удалось получить дополнительную информацию о директории: {e}")
    
    def _set_permissions(self, structure: DirectoryStructure):
        """Устанавливает права доступа для структуры директорий согласно платформе."""
        platform = self.config.platform
        
        # Windows использует стандартные права доступа, не требует изменений
        if platform == Platform.WINDOWS:
            logger.debug("Windows: используются стандартные права доступа")
            return
        
        # Unix-подобные системы (Linux, macOS) требуют установки прав
        if platform in [Platform.LINUX, Platform.MACOS]:
            self._set_unix_permissions(structure)
        else:
            logger.warning(f"Неизвестная платформа {platform}, пропускаем установку прав")
    
    def _set_unix_permissions(self, structure: DirectoryStructure):
        """Устанавливает права доступа для Unix-подобных систем (Linux, macOS)."""
        logger.debug("🔐 Установка прав доступа для Unix-подобной системы")
        
        # Права 755 (rwxr-xr-x) для директорий - владелец может читать/писать/выполнять,
        # группа и остальные могут читать и выполнять
        directory_mode = 0o755
        logger.debug(f"   Целевые права доступа: {oct(directory_mode)} (rwxr-xr-x)")
        
        directories = [
            ("base", structure.base),
            ("database", structure.database),
            ("cache", structure.cache),
            ("logs", structure.logs),
            ("temp", structure.temp)
        ]
        
        for name, path in directories:
            if path is None:
                logger.debug(f"   Пропускаем {name}: путь не определен")
                continue
                
            try:
                logger.debug(f"   Обработка директории {name}: {path}")
                
                if path.exists() and path.is_dir():
                    # Получаем текущие права для сравнения
                    current_stat = path.stat()
                    current_mode = current_stat.st_mode & 0o777
                    current_uid = current_stat.st_uid
                    current_gid = current_stat.st_gid
                    
                    logger.debug(f"     Текущие права: {oct(current_mode)}")
                    logger.debug(f"     Владелец: UID {current_uid}, GID {current_gid}")
                    
                    if current_mode != directory_mode:
                        logger.debug(f"     Изменение прав с {oct(current_mode)} на {oct(directory_mode)}")
                        path.chmod(directory_mode)
                        
                        # Проверяем что права действительно изменились
                        new_mode = path.stat().st_mode & 0o777
                        if new_mode == directory_mode:
                            logger.debug(f"     ✅ Права успешно установлены: {oct(directory_mode)}")
                        else:
                            logger.warning(f"     ⚠️  Права не изменились: ожидалось {oct(directory_mode)}, получено {oct(new_mode)}")
                    else:
                        logger.debug(f"     ✅ Права {oct(directory_mode)} уже установлены")
                else:
                    logger.warning(f"     ❌ Директория {name} не существует или не является директорией: {path}")
                    
            except OSError as e:
                if e.errno == 1:  # Operation not permitted
                    logger.warning(f"     ❌ Нет прав для изменения прав доступа директории {name} ({path})")
                    logger.debug(f"        Детали ошибки: {e}")
                    logger.debug(f"        Возможные причины:")
                    logger.debug(f"        - Недостаточно прав пользователя")
                    logger.debug(f"        - Директория принадлежит другому пользователю")
                    logger.debug(f"        - Файловая система не поддерживает изменение прав")
                elif e.errno == 2:  # No such file or directory
                    logger.warning(f"     ❌ Директория {name} не найдена при установке прав: {path}")
                    logger.debug(f"        Детали ошибки: {e}")
                else:
                    logger.warning(f"     ❌ Ошибка установки прав для директории {name} ({path}): {e}")
                    logger.debug(f"        Код ошибки: {e.errno}")
                    logger.debug(f"        Описание: {e.strerror}")
            except Exception as e:
                logger.warning(f"     ❌ Неожиданная ошибка установки прав для директории {name} ({path}): {e}")
                logger.debug(f"        Тип ошибки: {type(e).__name__}")
                logger.debug(f"        Детали: {str(e)}")
        
        logger.debug("🔐 Установка прав доступа завершена")


class PathResolver:
    """Разрешает пути с учетом переменных окружения."""
    
    def __init__(self, platform_detector: Optional[PlatformDetector] = None):
        """Инициализирует PathResolver с детектором платформы."""
        self.platform_detector = platform_detector or PlatformDetector()
    
    def resolve_data_directory(self) -> Path:
        """Разрешает путь к директории данных с учетом переменных окружения."""
        # Проверяем переменную окружения для переопределения
        custom_path = os.environ.get('OFFERS_CHECK_DATA_DIR')
        if custom_path:
            path = self._resolve_custom_path(custom_path)
            logger.info(f"Используется кастомная директория данных: {path}")
            return path
        
        # Используем стандартную директорию для платформы
        config = PlatformConfig.for_current_platform()
        logger.info(f"Используется стандартная директория данных для {config.platform.value}: {config.base_directory}")
        return config.base_directory
    
    def _resolve_custom_path(self, custom_path: str) -> Path:
        """Разрешает и валидирует кастомный путь из переменной окружения."""
        try:
            # Разворачиваем пользовательские пути (~) и делаем абсолютным
            path = Path(custom_path).expanduser().resolve()
            
            # Валидируем путь
            self._validate_custom_path(path)
            
            # Создаем директорию если не существует
            self._ensure_custom_directory_exists(path)
            
            return path
            
        except Exception as e:
            logger.error(f"Ошибка разрешения кастомного пути '{custom_path}': {e}")
            raise ValidationError(
                f"Не удалось использовать кастомную директорию '{custom_path}': {e}",
                validation_type="environment",
                invalid_value=custom_path
            )
    
    def _validate_custom_path(self, path: Path) -> None:
        """Валидирует кастомный путь на корректность."""
        # Проверяем что путь не является файлом
        if path.exists() and path.is_file():
            raise ValidationError(
                f"Указанный путь '{path}' является файлом, а не директорией",
                validation_type="path",
                invalid_value=str(path)
            )
        
        # Проверяем что путь не является системной директорией
        system_paths = {
            Path("/"), Path("/usr"), Path("/etc"), Path("/var"), Path("/sys"), Path("/proc"),
            Path("C:\\"), Path("C:\\Windows"), Path("C:\\Program Files"), Path("C:\\Program Files (x86)")
        }
        
        for sys_path in system_paths:
            try:
                if path.resolve() == sys_path.resolve():
                    raise ValidationError(
                        f"Нельзя использовать системную директорию '{path}' для пользовательских данных",
                        validation_type="path",
                        invalid_value=str(path)
                    )
            except (OSError, ValueError):
                # Игнорируем ошибки разрешения путей для несуществующих системных путей
                continue
        
        # Проверяем что родительская директория существует и доступна
        parent = path.parent
        if not parent.exists():
            raise ValidationError(
                f"Родительская директория '{parent}' не существует. "
                f"Создайте её вручную или выберите другой путь.",
                validation_type="path",
                invalid_value=str(parent)
            )
        
        if not os.access(parent, os.W_OK):
            platform = self.platform_detector.get_platform()
            raise PermissionError(
                f"Нет прав на запись в родительскую директорию '{parent}'. "
                f"Проверьте права доступа или выберите другой путь.",
                directory_path=parent,
                access_type="write",
                platform=platform
            )
    
    def _ensure_custom_directory_exists(self, path: Path) -> None:
        """Создает кастомную директорию если она не существует."""
        if path.exists():
            # Проверяем доступность существующей директории
            self._validate_directory_access(path)
            return
        
        try:
            # Создаем директорию с родительскими директориями
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана кастомная директория данных: {path}")
            
            # Устанавливаем права доступа в соответствии с платформой
            self._set_custom_directory_permissions(path)
            
            # Проверяем что директория создалась и доступна
            self._validate_directory_access(path)
            
        except OSError as e:
            if e.errno == 13:  # Permission denied
                raise PermissionError(
                    f"Нет прав для создания директории '{path}'. "
                    f"Запустите программу с правами администратора или выберите другой путь."
                )
            elif e.errno == 28:  # No space left on device
                raise DirectoryCreationError(
                    f"Недостаточно места на диске для создания директории '{path}'. "
                    f"Освободите место или выберите другой путь."
                )
            else:
                raise DirectoryCreationError(
                    f"Не удалось создать директорию '{path}': {e}"
                )
    
    def _set_custom_directory_permissions(self, path: Path) -> None:
        """Устанавливает права доступа для кастомной директории."""
        platform = self.platform_detector.get_platform()
        
        try:
            if platform in [Platform.LINUX, Platform.MACOS]:
                # Unix-подобные системы: 755 (rwxr-xr-x)
                path.chmod(0o755)
                logger.debug(f"Установлены права 755 для директории {path}")
            # Windows использует стандартные права доступа
            
        except Exception as e:
            logger.warning(f"Не удалось установить права доступа для {path}: {e}")
    
    def _validate_directory_access(self, path: Path) -> None:
        """Валидирует доступность директории для чтения и записи."""
        if not path.exists():
            raise DirectoryCreationError(f"Директория '{path}' не существует")
        
        if not path.is_dir():
            raise DirectoryCreationError(f"Путь '{path}' не является директорией")
        
        # Проверяем права на чтение
        if not os.access(path, os.R_OK):
            raise PermissionError(
                f"Нет прав на чтение директории '{path}'. "
                f"Измените права доступа: chmod 755 '{path}'"
            )
        
        # Проверяем права на запись
        if not os.access(path, os.W_OK):
            raise PermissionError(
                f"Нет прав на запись в директорию '{path}'. "
                f"Измените права доступа: chmod 755 '{path}'"
            )
        
        # Проверяем свободное место (минимум 100MB)
        try:
            stat = shutil.disk_usage(path)
            free_space_mb = stat.free / (1024 * 1024)
            if free_space_mb < 100:
                logger.warning(
                    f"Мало свободного места в директории '{path}': {free_space_mb:.1f} MB. "
                    f"Рекомендуется освободить место для корректной работы."
                )
        except Exception as e:
            logger.warning(f"Не удалось проверить свободное место в '{path}': {e}")
    
    def validate_and_create_structure(self, base_path: Path) -> bool:
        """Валидирует путь и создает базовую структуру директорий."""
        try:
            # Валидируем базовый путь
            self._validate_directory_access(base_path)
            
            # Создаем базовую структуру поддиректорий
            subdirs = ["database", "cache", "logs", "temp"]
            
            for subdir in subdirs:
                subdir_path = base_path / subdir
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    self._set_custom_directory_permissions(subdir_path)
                    logger.debug(f"Создана поддиректория: {subdir_path}")
            
            logger.info(f"Структура директорий создана в кастомном расположении: {base_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания структуры в кастомном расположении: {e}")
            return False


class DataMigrator:
    """Мигрирует данные из старых расположений с расширенной функциональностью."""
    
    def __init__(self, target_structure: DirectoryStructure):
        self.target = target_structure
        self.migration_stats = {
            'database_files': 0,
            'cache_files': 0,
            'log_files': 0,
            'config_files': 0,
            'other_files': 0,
            'total_size': 0,
            'errors': []
        }
    
    def migrate_legacy_data(self) -> bool:
        """Мигрирует данные из старой директории ./data с валидацией и откатом."""
        # Проверяем, отключена ли автоматическая миграция
        if os.environ.get('OFFERS_CHECK_DISABLE_MIGRATION', '').lower() in ['true', '1', 'yes']:
            logger.info("Автоматическая миграция отключена через переменную окружения OFFERS_CHECK_DISABLE_MIGRATION")
            return True
        
        legacy_path = Path("data")
        
        # Проверяем существование и валидность старой директории
        if not self._detect_and_validate_legacy_directory(legacy_path):
            return True
        
        # Создаем точку восстановления для отката
        rollback_info = self._create_rollback_point()
        
        try:
            logger.info("=" * 60)
            logger.info("НАЧАЛО МИГРАЦИИ ПОЛЬЗОВАТЕЛЬСКИХ ДАННЫХ")
            logger.info("=" * 60)
            logger.info(f"📂 Источник:    {legacy_path.absolute()}")
            logger.info(f"📁 Назначение:  {self.target.base.absolute()}")
            logger.info(f"⏰ Время:       {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("")
            
            # Создаем целевые директории если не существуют
            logger.info("Подготовка целевых директорий...")
            if not self.target.create_all():
                raise MigrationError("Не удалось создать целевые директории для миграции")
            logger.info("✅ Целевые директории подготовлены")
            
            # Анализируем содержимое для миграции
            logger.info("Анализ содержимого для миграции...")
            self._analyze_legacy_content(legacy_path)
            
            # Выполняем миграцию по категориям с прогрессом
            logger.info("Выполнение миграции файлов...")
            self._migrate_with_progress(legacy_path)
            
            # Проверяем целостность мигрированных данных
            logger.info("Проверка целостности мигрированных данных...")
            if not self._verify_migration_integrity(legacy_path):
                logger.error("❌ Проверка целостности миграции не пройдена")
                self._perform_rollback(rollback_info)
                raise MigrationError("Миграция отменена из-за ошибок целостности данных")
            logger.info("✅ Целостность данных подтверждена")
            
            # Проверяем общую успешность миграции
            logger.info("Финальная проверка миграции...")
            if not self._verify_migration_success():
                logger.error("❌ Проверка успешности миграции не пройдена")
                self._perform_rollback(rollback_info)
                raise MigrationError("Миграция отменена из-за критических ошибок")
            logger.info("✅ Миграция прошла все проверки")
            
            # Только после успешной валидации переименовываем старую директорию
            logger.info("Финализация миграции...")
            self._finalize_migration(legacy_path)
            
            logger.info("=" * 60)
            logger.info("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
            logger.info("=" * 60)
            self._log_migration_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Критическая ошибка миграции данных: {e}")
            self.migration_stats['errors'].append(f"Критическая ошибка: {e}")
            
            # Выполняем откат при любой критической ошибке
            try:
                self._perform_rollback(rollback_info)
            except Exception as rollback_error:
                logger.error(f"Ошибка отката миграции: {rollback_error}")
            
            raise MigrationError(f"Не удалось мигрировать данные: {e}")
    
    def _detect_and_validate_legacy_directory(self, legacy_path: Path) -> bool:
        """Обнаруживает и валидирует существующую директорию ./data."""
        if not legacy_path.exists():
            logger.debug("Старая директория ./data не найдена, миграция не требуется")
            return False
        
        if not legacy_path.is_dir():
            logger.warning(f"Путь ./data существует, но не является директорией: {legacy_path}")
            return False
        
        # Проверяем права доступа к старой директории
        if not os.access(legacy_path, os.R_OK):
            logger.error(f"Нет прав на чтение старой директории: {legacy_path}")
            raise MigrationError(f"Недостаточно прав для чтения {legacy_path}")
        
        # Проверяем что директория не пустая
        try:
            contents = list(legacy_path.iterdir())
            if not contents:
                logger.info("Старая директория ./data пуста, миграция не требуется")
                return False
            
            # Проверяем, не используются ли файлы в данный момент
            if self._check_files_in_use(legacy_path):
                logger.info("Файлы в директории ./data используются, миграция отложена")
                return False
            
            logger.info(f"Обнаружена директория ./data с {len(contents)} элементами для миграции")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка анализа содержимого старой директории: {e}")
            raise MigrationError(f"Не удалось проанализировать содержимое {legacy_path}: {e}")
    
    def _check_files_in_use(self, legacy_path: Path) -> bool:
        """Проверяет, используются ли файлы в директории в данный момент."""
        try:
            # Проверяем Excel файлы, которые могут быть открыты
            excel_patterns = ["*.xlsx", "*.xls", "*.xlsm"]
            for pattern in excel_patterns:
                for excel_file in legacy_path.glob(pattern):
                    if self._is_file_locked(excel_file):
                        logger.info(f"Excel файл используется: {excel_file.name}")
                        return True
            
            # Проверяем файлы базы данных
            db_patterns = ["*.db", "*.sqlite"]
            for pattern in db_patterns:
                for db_file in legacy_path.glob(pattern):
                    if self._is_file_locked(db_file):
                        logger.info(f"Файл базы данных используется: {db_file.name}")
                        return True
            
            # Проверяем временные файлы, которые могут указывать на активную работу
            temp_patterns = ["*.tmp", "~$*", ".~lock*"]
            for pattern in temp_patterns:
                temp_files = list(legacy_path.glob(pattern))
                if temp_files:
                    logger.info(f"Обнаружены временные файлы, указывающие на активную работу: {[f.name for f in temp_files]}")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Не удалось проверить использование файлов: {e}")
            # В случае ошибки считаем что файлы используются (безопасный подход)
            return True
    
    def _is_file_locked(self, file_path: Path) -> bool:
        """Проверяет, заблокирован ли файл другим процессом."""
        try:
            # Пытаемся открыть файл в режиме записи
            with open(file_path, 'r+b') as f:
                pass
            return False
        except (PermissionError, OSError):
            # Файл заблокирован или недоступен для записи
            return True
        except Exception:
            # Любая другая ошибка - считаем файл заблокированным
            return True

    def _analyze_legacy_content(self, legacy_path: Path):
        """Анализирует содержимое старой директории перед миграцией."""
        logger.info("Анализ содержимого для миграции...")
        
        try:
            # Подсчитываем файлы по категориям
            db_files = list(legacy_path.glob("*.db")) + list(legacy_path.glob("*.sqlite"))
            cache_files = []
            for pattern in ["*.cache", "*.tmp", ".license_cache.json"]:
                cache_files.extend(legacy_path.glob(pattern))
            
            log_files = list(legacy_path.glob("*.log"))
            
            config_files = []
            for pattern in ["*.json", "*.yaml", "*.yml", "*.ini", "*.cfg"]:
                config_files.extend(legacy_path.glob(pattern))
            
            # Исключаем уже учтенные файлы кеша из конфигурационных
            config_files = [f for f in config_files if f.name != ".license_cache.json"]
            
            # Подсчитываем общий размер
            total_size = 0
            all_files = db_files + cache_files + log_files + config_files
            
            for file_path in all_files:
                try:
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                except Exception as e:
                    logger.warning(f"Не удалось получить размер файла {file_path}: {e}")
            
            # Логируем статистику
            logger.info(f"Найдено для миграции:")
            logger.info(f"  - Файлы БД: {len(db_files)}")
            logger.info(f"  - Файлы кеша: {len(cache_files)}")
            logger.info(f"  - Файлы логов: {len(log_files)}")
            logger.info(f"  - Конфигурационные файлы: {len(config_files)}")
            logger.info(f"  - Общий размер: {total_size / 1024 / 1024:.2f} MB")
            
            # Проверяем свободное место в целевой директории
            self._check_target_space(total_size)
            
        except Exception as e:
            logger.error(f"Ошибка анализа содержимого: {e}")
            raise MigrationError(f"Не удалось проанализировать содержимое для миграции: {e}")
    
    def _check_target_space(self, required_size: int):
        """Проверяет достаточность свободного места в целевой директории."""
        try:
            stat = shutil.disk_usage(self.target.base.parent)
            free_space = stat.free
            
            # Добавляем 20% буфер к требуемому размеру
            required_with_buffer = int(required_size * 1.2)
            
            if free_space < required_with_buffer:
                free_mb = free_space / 1024 / 1024
                required_mb = required_with_buffer / 1024 / 1024
                raise DiskSpaceError(
                    f"Недостаточно свободного места для миграции. "
                    f"Требуется: {required_mb:.2f} MB, доступно: {free_mb:.2f} MB",
                    required_space_mb=required_mb,
                    available_space_mb=free_mb,
                    directory_path=self.target.base
                )
            
            logger.debug(f"Проверка места: требуется {required_with_buffer / 1024 / 1024:.2f} MB, "
                        f"доступно {free_space / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            logger.warning(f"Не удалось проверить свободное место: {e}")
    
    def _migrate_with_progress(self, legacy_path: Path):
        """Выполняет миграцию с отслеживанием прогресса."""
        migration_steps = [
            ("Файлы базы данных", self._migrate_database_files),
            ("Файлы кеша", self._migrate_cache_files),
            ("Файлы логов", self._migrate_log_files),
            ("Конфигурационные файлы", self._migrate_other_files)
        ]
        
        for step_name, migration_func in migration_steps:
            try:
                logger.info(f"Миграция: {step_name}...")
                migration_func(legacy_path)
                logger.info(f"✓ Завершено: {step_name}")
            except Exception as e:
                error_msg = f"Ошибка миграции {step_name}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
                # Продолжаем миграцию других типов файлов
                continue
    
    def _migrate_database_files(self, legacy_path: Path):
        """Мигрирует файлы базы данных с проверкой целостности."""
        db_files = list(legacy_path.glob("*.db")) + list(legacy_path.glob("*.sqlite"))
        
        for db_file in db_files:
            try:
                target_file = self.target.database / db_file.name
                
                if target_file.exists():
                    logger.info(f"Файл БД уже существует, пропускаем: {db_file.name}")
                    continue
                
                # Проверяем что это действительно файл базы данных
                if not self._validate_database_file(db_file):
                    logger.warning(f"Файл {db_file} не является корректной базой данных, пропускаем")
                    continue
                
                # Безопасное копирование с проверкой
                self._safe_copy_file(db_file, target_file)
                self.migration_stats['database_files'] += 1
                logger.info(f"✓ Мигрирован файл БД: {db_file.name}")
                
            except Exception as e:
                error_msg = f"Ошибка миграции файла БД {db_file}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_cache_files(self, legacy_path: Path):
        """Мигрирует файлы кеша."""
        cache_patterns = ["*.cache", "*.tmp", ".license_cache.json"]
        
        for pattern in cache_patterns:
            for cache_file in legacy_path.glob(pattern):
                try:
                    target_file = self.target.cache / cache_file.name
                    
                    if target_file.exists():
                        logger.debug(f"Файл кеша уже существует, пропускаем: {cache_file.name}")
                        continue
                    
                    self._safe_copy_file(cache_file, target_file)
                    self.migration_stats['cache_files'] += 1
                    logger.debug(f"✓ Мигрирован файл кеша: {cache_file.name}")
                    
                except Exception as e:
                    error_msg = f"Ошибка миграции файла кеша {cache_file}: {e}"
                    logger.warning(error_msg)
                    self.migration_stats['errors'].append(error_msg)
    
    def _migrate_log_files(self, legacy_path: Path):
        """Мигрирует файлы логов."""
        log_files = list(legacy_path.glob("*.log"))
        
        for log_file in log_files:
            try:
                target_file = self.target.logs / log_file.name
                
                if target_file.exists():
                    # Для логов можем создать резервную копию
                    backup_name = f"{log_file.stem}_legacy{log_file.suffix}"
                    target_file = self.target.logs / backup_name
                    logger.info(f"Файл лога существует, создаем резервную копию: {backup_name}")
                
                self._safe_copy_file(log_file, target_file)
                self.migration_stats['log_files'] += 1
                logger.debug(f"✓ Мигрирован файл лога: {log_file.name}")
                
            except Exception as e:
                error_msg = f"Ошибка миграции файла лога {log_file}: {e}"
                logger.warning(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_other_files(self, legacy_path: Path):
        """Мигрирует конфигурационные и другие файлы."""
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.ini", "*.cfg"]
        
        for pattern in config_patterns:
            for config_file in legacy_path.glob(pattern):
                try:
                    # Пропускаем уже мигрированные файлы кеша
                    if config_file.name == ".license_cache.json":
                        continue
                    
                    target_file = self.target.base / config_file.name
                    
                    if target_file.exists():
                        logger.info(f"Конфигурационный файл уже существует, пропускаем: {config_file.name}")
                        continue
                    
                    self._safe_copy_file(config_file, target_file)
                    self.migration_stats['config_files'] += 1
                    logger.debug(f"✓ Мигрирован конфигурационный файл: {config_file.name}")
                    
                except Exception as e:
                    error_msg = f"Ошибка миграции конфигурационного файла {config_file}: {e}"
                    logger.warning(error_msg)
                    self.migration_stats['errors'].append(error_msg)
    
    def _validate_database_file(self, db_file: Path) -> bool:
        """Проверяет что файл является корректной базой данных SQLite."""
        try:
            # Проверяем размер файла (минимум 100 байт для SQLite)
            if db_file.stat().st_size < 100:
                return False
            
            # Проверяем SQLite заголовок
            with open(db_file, 'rb') as f:
                header = f.read(16)
                if header.startswith(b'SQLite format 3\x00'):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Не удалось валидировать файл БД {db_file}: {e}")
            return False
    
    def _safe_copy_file(self, source: Path, target: Path):
        """Безопасно копирует файл с проверкой целостности."""
        try:
            # Получаем размер исходного файла
            source_size = source.stat().st_size
            
            # Копируем файл
            shutil.copy2(source, target)
            
            # Проверяем размер скопированного файла
            target_size = target.stat().st_size
            
            if source_size != target_size:
                target.unlink()  # Удаляем поврежденную копию
                raise MigrationError(
                    f"Размер файлов не совпадает: исходный {source_size}, скопированный {target_size}"
                )
            
            # Обновляем статистику
            self.migration_stats['total_size'] += source_size
            
        except Exception as e:
            if target.exists():
                try:
                    target.unlink()
                except:
                    pass
            raise MigrationError(f"Ошибка копирования {source} -> {target}: {e}")
    
    def _verify_migration_success(self) -> bool:
        """Проверяет успешность миграции."""
        total_files = (self.migration_stats['database_files'] + 
                      self.migration_stats['cache_files'] + 
                      self.migration_stats['log_files'] + 
                      self.migration_stats['config_files'])
        
        if total_files == 0:
            logger.warning("Не было мигрировано ни одного файла")
            return True  # Это не ошибка, возможно директория была пуста
        
        # Проверяем что критических ошибок не было
        critical_errors = [e for e in self.migration_stats['errors'] 
                          if 'Критическая ошибка' in e or 'файла БД' in e]
        
        if critical_errors:
            logger.error("Обнаружены критические ошибки миграции:")
            for error in critical_errors:
                logger.error(f"  - {error}")
            return False
        
        return True
    
    def _create_rollback_point(self) -> dict:
        """Создает точку восстановления для отката миграции."""
        logger.info("Создана точка восстановления для отката миграции")
        rollback_info = {
            'migrated_files': [],
            'created_directories': [],
            'timestamp': None
        }
        
        # Записываем существующие файлы в целевых директориях
        target_dirs = [
            ('database', self.target.database),
            ('cache', self.target.cache),
            ('logs', self.target.logs),
            ('base', self.target.base)
        ]
        
        for dir_name, dir_path in target_dirs:
            if dir_path and dir_path.exists():
                try:
                    existing_files = [f for f in dir_path.iterdir() if f.is_file()]
                    rollback_info[f'existing_{dir_name}_files'] = [str(f) for f in existing_files]
                except Exception as e:
                    logger.warning(f"Не удалось записать существующие файлы в {dir_name}: {e}")
        
        return rollback_info
    
    def _verify_migration_integrity(self, legacy_path: Path) -> bool:
        """Проверяет целостность мигрированных данных."""
        logger.info("Проверка целостности мигрированных данных...")
        
        integrity_errors = []
        
        try:
            # Проверяем файлы базы данных
            if not self._verify_database_integrity(legacy_path):
                integrity_errors.append("Ошибка целостности файлов базы данных")
            
            # Проверяем файлы кеша
            if not self._verify_cache_integrity(legacy_path):
                integrity_errors.append("Ошибка целостности файлов кеша")
            
            # Проверяем файлы логов
            if not self._verify_logs_integrity(legacy_path):
                integrity_errors.append("Ошибка целостности файлов логов")
            
            # Проверяем конфигурационные файлы
            if not self._verify_config_integrity(legacy_path):
                integrity_errors.append("Ошибка целостности конфигурационных файлов")
            
            if integrity_errors:
                logger.error("Обнаружены ошибки целостности:")
                for error in integrity_errors:
                    logger.error(f"  - {error}")
                return False
            
            logger.info("✓ Проверка целостности пройдена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Критическая ошибка проверки целостности: {e}")
            return False
    
    def _verify_database_integrity(self, legacy_path: Path) -> bool:
        """Проверяет целостность мигрированных файлов базы данных."""
        db_files = list(legacy_path.glob("*.db")) + list(legacy_path.glob("*.sqlite"))
        
        for db_file in db_files:
            target_file = self.target.database / db_file.name
            
            if not target_file.exists():
                continue  # Файл мог быть пропущен из-за ошибок
            
            try:
                # Сравниваем размеры файлов
                source_size = db_file.stat().st_size
                target_size = target_file.stat().st_size
                
                if source_size != target_size:
                    logger.error(f"Размеры файлов БД не совпадают: {db_file.name}")
                    return False
                
                # Проверяем что целевой файл является корректной БД
                if not self._validate_database_file(target_file):
                    logger.error(f"Мигрированный файл БД поврежден: {target_file}")
                    return False
                
            except Exception as e:
                logger.error(f"Ошибка проверки файла БД {db_file.name}: {e}")
                return False
        
        return True
    
    def _verify_cache_integrity(self, legacy_path: Path) -> bool:
        """Проверяет целостность мигрированных файлов кеша."""
        cache_patterns = ["*.cache", "*.tmp", ".license_cache.json"]
        
        for pattern in cache_patterns:
            for cache_file in legacy_path.glob(pattern):
                target_file = self.target.cache / cache_file.name
                
                if not target_file.exists():
                    continue
                
                try:
                    # Сравниваем размеры файлов
                    source_size = cache_file.stat().st_size
                    target_size = target_file.stat().st_size
                    
                    if source_size != target_size:
                        logger.error(f"Размеры файлов кеша не совпадают: {cache_file.name}")
                        return False
                    
                except Exception as e:
                    logger.error(f"Ошибка проверки файла кеша {cache_file.name}: {e}")
                    return False
        
        return True
    
    def _verify_logs_integrity(self, legacy_path: Path) -> bool:
        """Проверяет целостность мигрированных файлов логов."""
        log_files = list(legacy_path.glob("*.log"))
        
        for log_file in log_files:
            # Файлы логов могли быть переименованы при конфликтах
            target_file = self.target.logs / log_file.name
            backup_name = f"{log_file.stem}_legacy{log_file.suffix}"
            backup_file = self.target.logs / backup_name
            
            target_exists = target_file.exists()
            backup_exists = backup_file.exists()
            
            if not target_exists and not backup_exists:
                continue
            
            try:
                check_file = target_file if target_exists else backup_file
                
                # Сравниваем размеры файлов
                source_size = log_file.stat().st_size
                target_size = check_file.stat().st_size
                
                if source_size != target_size:
                    logger.error(f"Размеры файлов логов не совпадают: {log_file.name}")
                    return False
                
            except Exception as e:
                logger.error(f"Ошибка проверки файла лога {log_file.name}: {e}")
                return False
        
        return True
    
    def _verify_config_integrity(self, legacy_path: Path) -> bool:
        """Проверяет целостность мигрированных конфигурационных файлов."""
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.ini", "*.cfg"]
        
        for pattern in config_patterns:
            for config_file in legacy_path.glob(pattern):
                # Пропускаем файлы кеша
                if config_file.name == ".license_cache.json":
                    continue
                
                target_file = self.target.base / config_file.name
                
                if not target_file.exists():
                    continue
                
                try:
                    # Сравниваем размеры файлов
                    source_size = config_file.stat().st_size
                    target_size = target_file.stat().st_size
                    
                    if source_size != target_size:
                        logger.error(f"Размеры конфигурационных файлов не совпадают: {config_file.name}")
                        return False
                    
                except Exception as e:
                    logger.error(f"Ошибка проверки конфигурационного файла {config_file.name}: {e}")
                    return False
        
        return True
    
    def _perform_rollback(self, rollback_info: dict):
        """Выполняет откат миграции при ошибках."""
        logger.warning("=== ВЫПОЛНЕНИЕ ОТКАТА МИГРАЦИИ ===")
        
        try:
            # Удаляем файлы, созданные во время миграции
            self._remove_migrated_files(rollback_info)
            
            logger.info("Откат миграции выполнен успешно")
            
        except Exception as e:
            logger.error(f"Критическая ошибка отката миграции: {e}")
            logger.error("ВНИМАНИЕ: Откат не удался! Возможно повреждение данных.")
            logger.error("Рекомендуется ручная проверка и восстановление данных.")
    
    def _remove_migrated_files(self, rollback_info: dict):
        """Удаляет файлы, созданные во время миграции."""
        target_dirs = [
            ('database', self.target.database),
            ('cache', self.target.cache),
            ('logs', self.target.logs),
            ('base', self.target.base)
        ]
        
        for dir_name, dir_path in target_dirs:
            if not dir_path or not dir_path.exists():
                continue
            
            try:
                existing_files_key = f'existing_{dir_name}_files'
                existing_files = set(rollback_info.get(existing_files_key, []))
                
                # Удаляем файлы, которых не было до миграции
                for file_path in dir_path.iterdir():
                    if file_path.is_file() and str(file_path) not in existing_files:
                        try:
                            file_path.unlink()
                            logger.debug(f"Удален файл при откате: {file_path}")
                        except Exception as e:
                            logger.warning(f"Не удалось удалить файл при откате {file_path}: {e}")
                
            except Exception as e:
                logger.warning(f"Ошибка отката файлов в директории {dir_name}: {e}")
    
    def _finalize_migration(self, legacy_path: Path):
        """Завершает миграцию переименованием старой директории."""
        try:
            # Еще раз проверяем, что файлы не используются перед финализацией
            if self._check_files_in_use(legacy_path):
                logger.warning("Файлы в директории ./data используются, финализация миграции отложена")
                logger.info("Миграция данных выполнена, но исходная директория сохранена")
                return
            
            migrated_path = Path("data.migrated")
            
            # Если целевая директория уже существует, создаем уникальное имя
            counter = 1
            while migrated_path.exists():
                migrated_path = Path(f"data.migrated.{counter}")
                counter += 1
            
            # Переименовываем исходную директорию
            legacy_path.rename(migrated_path)
            logger.info(f"✓ Старая директория переименована: {legacy_path} -> {migrated_path}")
            
        except Exception as e:
            logger.error(f"Ошибка переименования старой директории: {e}")
            logger.warning("Миграция выполнена, но старая директория не переименована")
            logger.warning("Рекомендуется вручную переименовать ./data в ./data.migrated")
            logger.info("Это не влияет на работу программы - данные уже скопированы в новое расположение")
    
    def _log_migration_summary(self):
        """Логирует итоговую статистику миграции."""
        logger.info("=== ИТОГИ МИГРАЦИИ ===")
        logger.info(f"Файлы БД: {self.migration_stats['database_files']}")
        logger.info(f"Файлы кеша: {self.migration_stats['cache_files']}")
        logger.info(f"Файлы логов: {self.migration_stats['log_files']}")
        logger.info(f"Конфигурационные файлы: {self.migration_stats['config_files']}")
        logger.info(f"Общий размер: {self.migration_stats['total_size'] / 1024 / 1024:.2f} MB")
        
        if self.migration_stats['errors']:
            logger.warning(f"Предупреждения и ошибки: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats['errors']:
                logger.warning(f"  - {error}")
        else:
            logger.info("Миграция выполнена без ошибок")
        
        logger.info("=" * 22)


class UserDataManager:
    """Основной класс для управления пользовательскими данными."""
    
    def __init__(self):
        self.platform_detector = PlatformDetector()
        self.path_resolver = PathResolver(self.platform_detector)
        self.platform_config = PlatformConfig.for_current_platform()
        self.directory_manager = DirectoryManager(self.platform_config)
        self._structure: Optional[DirectoryStructure] = None
        self._initialized = False
    
    def get_data_directory(self) -> Path:
        """Получает путь к основной директории данных."""
        if not self._initialized:
            self.initialize_directories()
        return self._structure.base
    
    def get_database_path(self) -> Path:
        """Получает путь к файлу базы данных."""
        if not self._initialized:
            self.initialize_directories()
        return self._structure.database / "products.db"
    
    def get_cache_directory(self) -> Path:
        """Получает путь к директории кеша."""
        if not self._initialized:
            self.initialize_directories()
        return self._structure.cache
    
    def get_logs_directory(self) -> Path:
        """Получает путь к директории логов."""
        if not self._initialized:
            self.initialize_directories()
        return self._structure.logs
    
    def get_temp_directory(self) -> Path:
        """Получает путь к временной директории."""
        if not self._initialized:
            self.initialize_directories()
        return self._structure.temp
    
    def initialize_directories(self) -> bool:
        """Инициализирует структуру директорий с подробным логированием."""
        if self._initialized:
            logger.debug("Директории уже инициализированы, пропускаем инициализацию")
            return True
        
        try:
            logger.info("=" * 70)
            logger.info("ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЬСКИМИ ДАННЫМИ")
            logger.info("=" * 70)
            
            # Логируем информацию о системе
            logger.info(f"🖥️  Операционная система: {self.platform_config.platform.value}")
            logger.info(f"🏠 Домашняя директория: {Path.home()}")
            
            # Определяем базовую директорию с учетом переменных окружения
            logger.info("Определение расположения данных...")
            base_path = self.path_resolver.resolve_data_directory()
            logger.info(f"📍 Выбранное расположение: {base_path}")
            
            # Если используется кастомный путь, создаем базовую структуру через PathResolver
            custom_path = os.environ.get('OFFERS_CHECK_DATA_DIR')
            if custom_path:
                logger.info(f"🔧 Используется переменная окружения OFFERS_CHECK_DATA_DIR: {custom_path}")
                # Для кастомных путей используем валидацию и создание через PathResolver
                logger.debug("Валидация и создание кастомной структуры...")
                if not self.path_resolver.validate_and_create_structure(base_path):
                    raise DirectoryCreationError(f"Не удалось создать структуру в кастомной директории {base_path}")
                logger.debug("✅ Кастомная структура создана")
            else:
                logger.info("📋 Используется стандартное расположение для платформы")
            
            # Создаем структуру директорий
            logger.info("Создание структуры директорий...")
            self._structure = self.directory_manager.create_directory_structure(base_path)
            
            # Проверяем доступность
            logger.debug("Финальная проверка доступности базовой директории...")
            if not self.directory_manager.validate_directory_access(self._structure.base):
                raise DirectoryCreationError(f"Директория {self._structure.base} недоступна")
            logger.debug("✅ Базовая директория доступна")
            
            # Выполняем миграцию если необходимо
            logger.info("Проверка необходимости миграции данных...")
            try:
                migration_result = self.migrate_legacy_data()
                if migration_result:
                    logger.info("✅ Миграция данных выполнена")
                else:
                    logger.info("ℹ️  Миграция данных не требовалась")
            except Exception as migration_error:
                logger.warning(f"⚠️  Ошибка миграции данных: {migration_error}")
                logger.info("Программа продолжит работу с новым расположением данных")
                # Не прерываем инициализацию из-за ошибок миграции
            
            self._initialized = True
            
            # Логируем информацию о директориях
            self._log_directory_info()
            
            logger.info("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error("=" * 70)
            logger.error("❌ ОШИБКА ИНИЦИАЛИЗАЦИИ ДИРЕКТОРИЙ")
            logger.error("=" * 70)
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Сообщение: {str(e)}")
            
            # Если это наша кастомная ошибка с дополнительной информацией
            if hasattr(e, 'get_user_friendly_message'):
                logger.error("ПОДРОБНАЯ ИНФОРМАЦИЯ ОБ ОШИБКЕ:")
                logger.error(e.get_user_friendly_message())
            
            logger.error("=" * 70)
            
            # Перебрасываем исключение для обработки на верхнем уровне
            if isinstance(e, (DirectoryCreationError, PermissionError, DiskSpaceError, ValidationError)):
                raise
            else:
                raise DirectoryCreationError(f"Не удалось инициализировать директории: {e}")
    
    def migrate_legacy_data(self) -> bool:
        """Выполняет миграцию данных из старых расположений."""
        if not self._structure:
            raise UserDataError("Структура директорий не инициализирована")
        
        try:
            migrator = DataMigrator(self._structure)
            return migrator.migrate_legacy_data()
        except Exception as e:
            logger.error(f"Ошибка миграции данных: {e}")
            return False
    
    def _log_directory_info(self):
        """Логирует подробную информацию о директориях для пользователя."""
        if not self._structure:
            return
        
        logger.info("=" * 60)
        logger.info("ИНФОРМАЦИЯ О РАСПОЛОЖЕНИИ ПОЛЬЗОВАТЕЛЬСКИХ ДАННЫХ")
        logger.info("=" * 60)
        
        # Основная информация
        logger.info(f"Операционная система: {self.platform_config.platform.value}")
        logger.info(f"Использование переменной окружения: {'Да' if os.environ.get('OFFERS_CHECK_DATA_DIR') else 'Нет'}")
        
        if os.environ.get('OFFERS_CHECK_DATA_DIR'):
            logger.info(f"Переменная OFFERS_CHECK_DATA_DIR: {os.environ.get('OFFERS_CHECK_DATA_DIR')}")
        
        logger.info("")
        logger.info("ПУТИ К ДИРЕКТОРИЯМ:")
        logger.info(f"📁 Базовая директория:    {self._structure.base}")
        logger.info(f"🗄️  База данных:          {self.get_database_path()}")
        logger.info(f"💾 Кеш:                  {self._structure.cache}")
        logger.info(f"📋 Логи:                 {self._structure.logs}")
        logger.info(f"🗂️  Временные файлы:      {self._structure.temp}")
        
        # Информация о доступности и размерах
        logger.info("")
        logger.info("СТАТУС ДИРЕКТОРИЙ:")
        self._log_directory_status("Базовая", self._structure.base)
        self._log_directory_status("База данных", self._structure.database)
        self._log_directory_status("Кеш", self._structure.cache)
        self._log_directory_status("Логи", self._structure.logs)
        self._log_directory_status("Временные", self._structure.temp)
        
        # Информация о свободном месте
        self._log_disk_space_info()
        
        logger.info("=" * 60)
        logger.info("Для резервного копирования сохраните содержимое базовой директории")
        logger.info("=" * 60)
    
    def _log_directory_status(self, name: str, path: Path):
        """Логирует статус конкретной директории."""
        try:
            if path.exists():
                if path.is_dir():
                    # Подсчитываем файлы в директории
                    file_count = len([f for f in path.iterdir() if f.is_file()])
                    dir_count = len([f for f in path.iterdir() if f.is_dir()])
                    
                    # Проверяем права доступа
                    readable = os.access(path, os.R_OK)
                    writable = os.access(path, os.W_OK)
                    
                    status = "✅ Доступна"
                    if not readable or not writable:
                        status = "⚠️  Ограниченный доступ"
                    
                    logger.info(f"  {name:15} {status} | Файлов: {file_count:3d} | Папок: {dir_count:2d}")
                    
                    if not readable:
                        logger.warning(f"    ⚠️  Нет прав на чтение: {path}")
                    if not writable:
                        logger.warning(f"    ⚠️  Нет прав на запись: {path}")
                        
                else:
                    logger.error(f"  {name:15} ❌ Не является директорией: {path}")
            else:
                logger.warning(f"  {name:15} ❓ Не существует: {path}")
                
        except Exception as e:
            logger.error(f"  {name:15} ❌ Ошибка проверки: {e}")
    
    def _log_disk_space_info(self):
        """Логирует информацию о свободном месте на диске."""
        try:
            logger.info("")
            logger.info("ИНФОРМАЦИЯ О ДИСКЕ:")
            
            # Проверяем место для каждой уникальной директории
            unique_paths = set()
            for path in [self._structure.base, self._structure.cache, self._structure.logs]:
                if path:
                    # Получаем корневой путь диска
                    root_path = path.anchor if hasattr(path, 'anchor') else path.parts[0]
                    unique_paths.add(path.parent)
            
            for path in unique_paths:
                try:
                    stat = shutil.disk_usage(path)
                    total_gb = stat.total / (1024**3)
                    free_gb = stat.free / (1024**3)
                    used_gb = (stat.total - stat.free) / (1024**3)
                    free_percent = (stat.free / stat.total) * 100
                    
                    status = "✅"
                    if free_percent < 10:
                        status = "🔴"
                    elif free_percent < 20:
                        status = "🟡"
                    
                    logger.info(f"  Диск {path}: {status} Свободно: {free_gb:.1f} GB ({free_percent:.1f}%) | "
                              f"Всего: {total_gb:.1f} GB")
                    
                    if free_gb < 0.1:  # Меньше 100 MB
                        logger.warning(f"    ⚠️  Критически мало места на диске {path}")
                    elif free_gb < 1.0:  # Меньше 1 GB
                        logger.warning(f"    ⚠️  Мало свободного места на диске {path}")
                        
                except Exception as e:
                    logger.warning(f"  Диск {path}: ❓ Не удалось получить информацию: {e}")
                    
        except Exception as e:
            logger.warning(f"Ошибка получения информации о диске: {e}")
    
    def get_directory_info(self) -> Dict[str, Any]:
        """Возвращает информацию о директориях для отладки."""
        if not self._initialized:
            self.initialize_directories()
        
        return {
            "platform": self.platform_config.platform.value,
            "base_directory": str(self._structure.base),
            "database_path": str(self.get_database_path()),
            "cache_directory": str(self._structure.cache),
            "logs_directory": str(self._structure.logs),
            "temp_directory": str(self._structure.temp),
            "initialized": self._initialized
        }