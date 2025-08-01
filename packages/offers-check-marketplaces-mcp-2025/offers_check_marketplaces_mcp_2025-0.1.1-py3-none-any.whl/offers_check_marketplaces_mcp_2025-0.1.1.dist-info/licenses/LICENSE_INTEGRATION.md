# Интеграция лицензионного ключа

## Обзор

В проект успешно интегрирована система проверки лицензионных ключей, которая обеспечивает:

- Автоматическую проверку лицензии при запуске сервера
- MCP инструменты для управления лицензией
- Кэширование результатов проверки для производительности
- Сохранение лицензионного ключа в конфигурации

## Компоненты интеграции

### 1. LicenseManager (`offers_check_marketplaces/license_manager.py`)

Основной класс для управления лицензиями:

```python
from offers_check_marketplaces.license_manager import LicenseManager, check_license

# Быстрая проверка лицензии
is_valid, license_info = check_license()

# Создание менеджера лицензий
license_manager = LicenseManager()

# Проверка лицензии
is_valid, license_data = license_manager.verify_license()

# Установка нового ключа
success = license_manager.set_license_key("новый-ключ", save_to_config=True)
```

### 2. Интеграция с сервером

Проверка лицензии интегрирована в функцию `initialize_components()` в `server.py`:

- Лицензия проверяется перед инициализацией компонентов
- При недействительной лицензии сервер не запускается
- Логируются все операции с лицензией

### 3. MCP инструменты

Добавлены два новых MCP инструмента:

#### `check_license_status`

Проверяет текущий статус лицензии:

```json
{
  "status": "valid",
  "message": "Лицензия действительна",
  "license_key": "743017d6-221c-4e0a-93ed-e417ae006db2",
  "license_info": {
    "valid": true,
    "checked_at": "2025-07-24T19:30:14.633000",
    "expires_at": null,
    "plan": null,
    "features": []
  },
  "api_url": "http://utils-licensegateproxy-yodjsn-513a08-83-222-22-34.traefik.me:1884/license/a2029/743017d6-221c-4e0a-93ed-e417ae006db2/verify"
}
```

#### `set_license_key`

Устанавливает новый лицензионный ключ:

```json
{
  "status": "success",
  "message": "Лицензионный ключ успешно установлен и проверен",
  "license_key": "743017d6-221c-4e0a-93ed-e417ae006db2",
  "license_info": {...},
  "saved_to_config": true
}
```

## Конфигурация

### Источники лицензионного ключа (по приоритету):

1. **Параметр конструктора** - передается напрямую в `LicenseManager(license_key)`
2. **Переменная окружения** - `LICENSE_KEY`
3. **Файл конфигурации** - `data/.license_config.json`
4. **Ключ по умолчанию** - `743017d6-221c-4e0a-93ed-e417ae006db2`

### Файлы

- **`data/.license_config.json`** - сохраненный лицензионный ключ
- **`data/.license_cache.json`** - кэш результатов проверки (1 час)

### API сервер

Текущий адрес API: `http://utils-licensegateproxy-yodjsn-513a08-83-222-22-34.traefik.me:1884/license/a2029`

## Использование

### Запуск сервера

```bash
# STDIO режим
python -m offers_check_marketplaces

# SSE режим
python -m offers_check_marketplaces --sse --host 0.0.0.0 --port 8000
```

### Установка лицензионного ключа через переменную окружения

```bash
# Windows
set LICENSE_KEY=ваш-лицензионный-ключ
python -m offers_check_marketplaces

# Linux/Mac
export LICENSE_KEY=ваш-лицензионный-ключ
python -m offers_check_marketplaces
```

### Программная установка ключа

```python
from offers_check_marketplaces.license_manager import LicenseManager

license_manager = LicenseManager()
success = license_manager.set_license_key("новый-ключ", save_to_config=True)
```

## Тестирование

Доступны следующие тесты:

```bash
# Базовая интеграция лицензии
python test_license_integration.py

# Подключение к новому API адресу
python test_new_license_url.py

# MCP инструменты лицензии
python test_mcp_license_tools.py

# Полная интеграция с сервером
python test_final_integration.py
```

## Обработка ошибок

Система обрабатывает следующие сценарии:

- **Недоступность API** - возвращает ошибку с предложением повторить позже
- **Недействительный ключ** - не сохраняет в конфигурацию, возвращает старый ключ
- **Таймаут подключения** - логирует ошибку и возвращает соответствующее сообщение
- **Отсутствие ключа** - использует ключ по умолчанию

## Логирование

Все операции с лицензией логируются:

```
2025-07-24 19:30:14,592 - offers_check_marketplaces.server - INFO - Проверка лицензионного ключа...
2025-07-24 19:30:14,611 - offers_check_marketplaces.server - INFO - Лицензия действительна, продолжаем инициализацию...
```

## Безопасность

- Лицензионные ключи не логируются полностью (только первые 8 символов)
- Файлы конфигурации создаются в локальной директории `data/`
- Кэш автоматически обновляется каждый час
- Недействительные ключи не сохраняются в конфигурацию

## Зависимости

Добавлена зависимость в `pyproject.toml`:

```toml
dependencies = [
    # ... другие зависимости
    "requests>=2.28.0"
]
```

## Статус интеграции

✅ **ЗАВЕРШЕНО** - Интеграция лицензионного ключа полностью реализована и протестирована.

Сервер готов к работе с интегрированной системой лицензирования.
