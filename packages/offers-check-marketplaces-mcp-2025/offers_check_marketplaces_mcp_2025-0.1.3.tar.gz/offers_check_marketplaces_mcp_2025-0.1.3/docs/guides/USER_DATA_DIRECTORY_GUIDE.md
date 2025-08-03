# Руководство по системе управления пользовательскими данными

## Обзор

MCP сервер `offers-check-marketplaces` теперь автоматически использует стандартные директории данных пользователя в зависимости от операционной системы. Это обеспечивает корректную работу после установки через pip и соответствие стандартам каждой ОС.

## Расположение данных по умолчанию

### Windows

- **Базовая директория**: `%APPDATA%\offers-check-marketplaces\`
- **База данных**: `%APPDATA%\offers-check-marketplaces\database\products.db`
- **Кеш**: `%APPDATA%\offers-check-marketplaces\cache\`
- **Логи**: `%APPDATA%\offers-check-marketplaces\logs\`

**Пример пути**: `C:\Users\Username\AppData\Roaming\offers-check-marketplaces\`

### macOS

- **Базовая директория**: `~/Library/Application Support/offers-check-marketplaces/`
- **База данных**: `~/Library/Application Support/offers-check-marketplaces/database/products.db`
- **Кеш**: `~/Library/Caches/offers-check-marketplaces/`
- **Логи**: `~/Library/Logs/offers-check-marketplaces/`

**Пример пути**: `/Users/username/Library/Application Support/offers-check-marketplaces/`

### Linux

- **Базовая директория**: `~/.local/share/offers-check-marketplaces/`
- **База данных**: `~/.local/share/offers-check-marketplaces/database/products.db`
- **Кеш**: `~/.cache/offers-check-marketplaces/`
- **Логи**: `~/.local/share/offers-check-marketplaces/logs/`

**Пример пути**: `/home/username/.local/share/offers-check-marketplaces/`

#### Поддержка XDG Base Directory (Linux)

Если установлены переменные окружения XDG:

- `$XDG_DATA_HOME/offers-check-marketplaces/` вместо `~/.local/share/offers-check-marketplaces/`
- `$XDG_CACHE_HOME/offers-check-marketplaces/` вместо `~/.cache/offers-check-marketplaces/`

## Переопределение расположения

### Переменная окружения

Вы можете переопределить расположение данных с помощью переменной окружения:

```bash
export OFFERS_CHECK_DATA_DIR="/path/to/custom/directory"
```

**Windows (PowerShell)**:

```powershell
$env:OFFERS_CHECK_DATA_DIR = "C:\path\to\custom\directory"
```

**Windows (CMD)**:

```cmd
set OFFERS_CHECK_DATA_DIR=C:\path\to\custom\directory
```

### MCP конфигурация

В файле конфигурации MCP можно указать переменную окружения:

```json
{
  "mcpServers": {
    "offers_check_marketplaces": {
      "command": "offers-check-marketplaces",
      "env": {
        "LICENSE_KEY": "your-license-key-here",
        "OFFERS_CHECK_DATA_DIR": "/custom/path/to/data"
      }
    }
  }
}
```

## Структура директорий

После первого запуска создается следующая структура:

```
offers-check-marketplaces/
├── database/
│   └── products.db          # База данных SQLite
├── cache/
│   ├── .license_cache.json  # Кеш лицензии
│   └── *.tmp               # Временные файлы кеша
├── logs/
│   └── *.log               # Файлы логов
└── temp/
    └── *                   # Временные файлы
```

## Миграция данных

### Автоматическая миграция

При первом запуске с новой системой, если обнаружена старая директория `./data`, происходит автоматическая миграция:

1. **Копирование файлов**:

   - `*.db`, `*.sqlite` → `database/`
   - `*.cache`, `*.tmp`, `.license_cache.json` → `cache/`
   - `*.log` → `logs/`
   - `*.json`, `*.yaml`, `*.ini` → базовая директория

2. **Переименование старой директории**:

   - `./data` → `./data.migrated`

3. **Логирование процесса**:
   - Подробная информация о миграции в логах

### Ручная миграция

Если автоматическая миграция не сработала, можно выполнить ручную:

1. Найдите новую директорию данных (см. логи при запуске)
2. Скопируйте файлы из старой `./data` в соответствующие поддиректории
3. Удалите или переименуйте старую директорию

## Права доступа

### Windows

Используются стандартные права доступа Windows. Файлы доступны только текущему пользователю.

### macOS и Linux

- **Директории**: `755` (rwxr-xr-x)
- **Файлы**: `644` (rw-r--r--)

## Диагностика проблем

### Проверка расположения данных

При запуске сервера в логах выводится информация о директориях:

```
=== ИНФОРМАЦИЯ О ДИРЕКТОРИЯХ ДАННЫХ ===
Платформа: windows
Базовая директория: C:\Users\Username\AppData\Roaming\offers-check-marketplaces
База данных: C:\Users\Username\AppData\Roaming\offers-check-marketplaces\database\products.db
Кеш: C:\Users\Username\AppData\Roaming\offers-check-marketplaces\cache
Логи: C:\Users\Username\AppData\Roaming\offers-check-marketplaces\logs
Временные файлы: C:\Users\Username\AppData\Roaming\offers-check-marketplaces\temp
=============================================
```

### Частые проблемы

#### 1. Недостаточно прав доступа

**Симптомы**: Ошибки создания файлов или директорий
**Решение**:

- Проверьте права доступа к родительской директории
- На Windows убедитесь что не требуются права администратора
- На Linux/macOS проверьте права с помощью `ls -la`

#### 2. Нехватка места на диске

**Симптомы**: Ошибки записи файлов
**Решение**: Освободите место на диске (требуется минимум 100MB)

#### 3. Директория недоступна

**Симптомы**: Ошибки доступа к директории
**Решение**:

- Проверьте что директория не заблокирована другими процессами
- Убедитесь что путь корректен и доступен

#### 4. Проблемы с переменными окружения

**Симптомы**: Игнорирование `OFFERS_CHECK_DATA_DIR`
**Решение**:

- Убедитесь что переменная установлена в той же сессии
- Проверьте корректность пути
- Перезапустите терминал/IDE

## Резервное копирование

### Что копировать

Для полного резервного копирования скопируйте всю директорию данных:

- **Windows**: `%APPDATA%\offers-check-marketplaces\`
- **macOS**: `~/Library/Application Support/offers-check-marketplaces/`
- **Linux**: `~/.local/share/offers-check-marketplaces/`

### Важные файлы

- `database/products.db` - основная база данных
- `cache/.license_cache.json` - кеш лицензии
- Конфигурационные файлы в базовой директории

### Восстановление

1. Остановите MCP сервер
2. Скопируйте резервную копию в директорию данных
3. Запустите MCP сервер

## Для разработчиков

### Использование в коде

```python
from offers_check_marketplaces.user_data_manager import UserDataManager

# Создание менеджера
manager = UserDataManager()

# Получение путей
data_dir = manager.get_data_directory()
db_path = manager.get_database_path()
cache_dir = manager.get_cache_directory()

# Информация о директориях
info = manager.get_directory_info()
```

### Тестирование

Для тестирования используйте переменную окружения:

```python
import os
os.environ['OFFERS_CHECK_DATA_DIR'] = '/tmp/test_data'
```

### Кастомизация

Можно создать собственную конфигурацию:

```python
from offers_check_marketplaces.user_data_manager import PlatformConfig, Platform

config = PlatformConfig(
    platform=Platform.LINUX,
    base_directory=Path("/custom/path"),
    permissions={"directory": 0o700}
)
```

## Совместимость

### Обратная совместимость

- Старые установки автоматически мигрируются
- Поддерживается переопределение через переменные окружения
- Сохраняется работоспособность существующих скриптов

### Версии Python

- Python 3.10+
- Все поддерживаемые операционные системы

### Зависимости

Новая система не требует дополнительных зависимостей и использует только стандартную библиотеку Python.
