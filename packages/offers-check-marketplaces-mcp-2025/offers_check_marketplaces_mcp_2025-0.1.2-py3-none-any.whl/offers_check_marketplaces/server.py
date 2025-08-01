import os
import sys
import anyio
import click
import uvicorn
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP, Context

from .data_processor import DataProcessor
from .database_manager import DatabaseManager
from .search_engine import SearchEngine
from .statistics import StatisticsGenerator
from .marketplace_client import MarketplaceClient
from .marketplace_config import get_marketplace_config, get_all_marketplaces
from .license_manager import LicenseManager, check_license
from .excel_tools import ExcelTools
from .user_data_manager import UserDataManager
from .error_handling import (
    handle_errors,
    ErrorCategory,
    ErrorSeverity,
    create_user_friendly_error,
    get_error_summary,
    log_recovery_attempt
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

APP_ID = "offers-check-marketplaces"
mcp = FastMCP(APP_ID)

# Global component instances
user_data_manager: Optional[UserDataManager] = None
data_processor: Optional[DataProcessor] = None
database_manager: Optional[DatabaseManager] = None
search_engine: Optional[SearchEngine] = None
statistics_generator: Optional[StatisticsGenerator] = None
marketplace_client: Optional[MarketplaceClient] = None
excel_tools: Optional[ExcelTools] = None

async def initialize_components():
    """
    Инициализирует все компоненты системы.
    
    Создает экземпляры всех основных компонентов и настраивает
    их взаимодействие. Также инициализирует базу данных.
    """
    global user_data_manager, data_processor, database_manager, search_engine, statistics_generator, marketplace_client, excel_tools
    
    try:
        logger.info("Инициализация компонентов системы...")
        
        # Проверка лицензии перед инициализацией
        logger.info("Проверка лицензионного ключа...")
        is_valid, license_info = check_license()
        
        if not is_valid:
            error_msg = f"Недействительная лицензия: {license_info.get('message', 'Неизвестная ошибка')}"
            logger.error(error_msg)
            logger.error("Программа будет завершена из-за недействительной лицензии")
            print(f"ОШИБКА: {error_msg}")
            print("Программа завершена. Проверьте лицензионный ключ.")
            sys.exit(1)
        
        logger.info("Лицензия действительна, продолжаем инициализацию...")
        
        # Инициализация менеджера пользовательских данных
        logger.info("Инициализация менеджера пользовательских данных...")
        user_data_manager = UserDataManager()
        user_data_manager.initialize_directories()
        
        # Инициализация компонентов
        logger.info("Инициализация обработчика данных...")
        data_processor = DataProcessor()
        
        logger.info("Инициализация менеджера базы данных...")
        database_manager = DatabaseManager(user_data_manager)
        await database_manager.init_database()
        
        logger.info("Инициализация клиента маркетплейсов...")
        marketplace_client = MarketplaceClient()
        
        logger.info("Инициализация поискового движка...")
        search_engine = SearchEngine()
        
        logger.info("Инициализация генератора статистики...")
        statistics_generator = StatisticsGenerator(database_manager)
        
        logger.info("Инициализация Excel инструментов...")
        excel_tools = ExcelTools()
        
        logger.info("Все компоненты успешно инициализированы")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации компонентов: {e}")
        raise

# Minimal Starlette app for SSE
starlette_app = Starlette(routes=[Mount("/", app=mcp.sse_app())])

# System prompt for AI agent
SYSTEM_PROMPT = """
# MCP Сервер "offers-check-marketplaces"

Вы работаете с MCP сервером offers-check-marketplaces, который автоматизирует поиск товаров 
и сравнение цен на различных маркетплейсах. Этот сервер является координирующим центром для 
анализа рыночных цен и генерации комплексных отчетов.

## ДОСТУПНЫЕ ИНСТРУМЕНТЫ

### 1. search_products(model_name: str)
Поиск товаров на маркетплейсах по названию модели.
- **Принимает**: название модели товара (строка)
- **Возвращает**: результаты поиска с разных маркетплейсов включая цены, наличие и ссылки
- **Особенности**: 
  - Использует приоритетные источники из данных продукта
  - Работает через MCP Playwright для веб-скрапинга
  - Поддерживает параллельный поиск на нескольких маркетплейсах
  - Обрабатывает ошибки недоступности маркетплейсов

**Пример использования**:
```
search_products("Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ")
```

**Пример ответа**:
```json
{
  "status": "success",
  "query": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
  "results": [
    {
      "marketplace": "komus.ru",
      "product_found": true,
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.komus.ru/product/12345"
    },
    {
      "marketplace": "vseinstrumenti.ru",
      "product_found": true,
      "price": 1320.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.vseinstrumenti.ru/product/67890"
    }
  ],
  "search_time": "2023-07-21T15:30:45"
}
```

### 2. get_product_details(product_code: float)
Получение детальной информации о товаре по коду из базы данных.
- **Принимает**: код товара (число)
- **Возвращает**: полную информацию о товаре, текущие цены, процентные дельты
- **Особенности**:
  - Включает категорию, единицу измерения, приоритетные источники
  - Показывает сравнение цен между маркетплейсами
  - Рассчитывает процентные дельты между ценами
  - Определяет минимальные и максимальные цены

**Пример использования**:
```
get_product_details(195385.0)
```

**Пример ответа**:
```json
{
  "status": "success",
  "product": {
    "code": 195385.0,
    "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
    "category": "Хозтовары и посуда",
    "unit": "м",
    "priority_1_source": "Комус",
    "priority_2_source": "ВсеИнструменты"
  },
  "prices": [
    {
      "marketplace": "komus.ru",
      "price": 1250.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.komus.ru/product/12345",
      "scraped_at": "2023-07-21T15:30:45"
    },
    {
      "marketplace": "vseinstrumenti.ru",
      "price": 1320.0,
      "currency": "RUB",
      "availability": "в наличии",
      "product_url": "https://www.vseinstrumenti.ru/product/67890",
      "scraped_at": "2023-07-21T15:30:50"
    }
  ],
  "price_analysis": {
    "min_price": {
      "value": 1250.0,
      "marketplace": "komus.ru"
    },
    "max_price": {
      "value": 1320.0,
      "marketplace": "vseinstrumenti.ru"
    },
    "delta_percent": 5.6
  }
}
```

### 3. get_product_list()
Получение списка всех SKU товаров из базы данных.
- **Принимает**: ничего
- **Возвращает**: список всех товаров с их SKU и базовой информацией
- **Особенности**:
  - Возвращает все товары из базы данных
  - Включает SKU, название модели, категорию и единицу измерения
  - Полезно для получения полного списка доступных товаров
  - Можно использовать для последующего поиска конкретных товаров

**Пример использования**:
```
get_product_list()
```

**Пример ответа**:
```json
{
  "status": "success",
  "products": [
    {
      "sku": 195385.0,
      "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
      "category": "Хозтовары и посуда",
      "unit": "м"
    },
    {
      "sku": 195386.0,
      "model_name": "Бумага офисная А4 80г/м2",
      "category": "Канцелярские товары",
      "unit": "пачка"
    }
  ],
  "total_count": 150,
  "timestamp": "2023-07-21T16:45:30"
}
```

### 4. get_statistics()
Получение статистики по всем обработанным товарам.
- **Принимает**: ничего
- **Возвращает**: комплексную статистику по обработанным товарам
- **Особенности**:
  - Общее количество обработанных товаров
  - Количество товаров с успешными совпадениями цен
  - Средние процентные дельты цен
  - Разбивка по категориям товаров
  - Информация о покрытии маркетплейсов

**Пример использования**:
```
get_statistics()
```

**Пример ответа**:
```json
{
  "status": "success",
  "statistics": {
    "total_products": 150,
    "products_with_prices": 132,
    "average_delta_percent": 7.8,
    "category_breakdown": {
      "Хозтовары и посуда": 45,
      "Канцелярские товары": 38,
      "Офисная техника": 27,
      "Мебель": 22,
      "Прочее": 18
    },
    "marketplace_coverage": {
      "komus.ru": 128,
      "vseinstrumenti.ru": 95,
      "ozon.ru": 112,
      "wildberries.ru": 87,
      "officemag.ru": 76
    }
  },
  "timestamp": "2023-07-21T16:45:30"
}
```

## ПОДДЕРЖИВАЕМЫЕ МАРКЕТПЛЕЙСЫ

1. **komus.ru** (Комус) - офисные товары и канцелярия
2. **vseinstrumenti.ru** (ВсеИнструменты) - инструменты и оборудование
3. **ozon.ru** (Озон) - универсальный маркетплейс
4. **wildberries.ru** (Wildberries) - товары широкого потребления
5. **officemag.ru** (Офисмаг) - офисные принадлежности

## РАБОЧИЙ ПРОЦЕСС

### Этап 1: Подготовка данных
- Система читает входной Excel файл `data/Таблица на вход.xlsx`
- Данные парсятся в JSON формат с сохранением структуры полей
- Информация сохраняется в SQLite базу данных для эффективных запросов

### Этап 2: Поиск товаров
- Для каждого товара определяются приоритетные источники
- Выполняется поиск через `search_products` на указанных маркетплейсах
- Система делегирует веб-скрапинг MCP Playwright серверу
- Результаты агрегируются и сохраняются в базу данных

### Этап 3: Анализ и детализация
- Используйте `get_product_details` для получения подробной информации
- Система рассчитывает процентные дельты между ценами
- Определяются минимальные и максимальные цены по источникам

### Этап 4: Статистика и отчеты
- `get_statistics` предоставляет общую аналитику
- Генерируется выходной Excel файл `data/Таблица на выход (отработанная).xlsx`
- Файл содержит исходные данные плюс найденные цены и расчеты

## ОСОБЕННОСТИ АРХИТЕКТУРЫ

- **Координирующая роль**: Сервер не выполняет веб-скрапинг напрямую, а координирует работу через MCP Playwright
- **Асинхронная обработка**: Поддержка параллельного поиска на нескольких маркетплейсах
- **Обработка ошибок**: Graceful degradation при недоступности отдельных маркетплейсов
- **Rate limiting**: Соблюдение ограничений скорости для каждого маркетплейса

## ФОРМАТЫ ДАННЫХ

### Входной Excel
Содержит поля с символами переноса строк:
- "Код\nмодели" - уникальный код товара
- "model_name" - название модели товара
- "Категория" - категория товара
- "Единица измерения" - единица измерения товара
- "Приоритет \n1 Источники" - первичный источник поиска
- "Приоритет \n2 Источники" - вторичный источник поиска
- "Цена позиции\nМП c НДС" - пустое поле для заполнения
- "Цена позиции\nB2C c НДС" - пустое поле для заполнения
- "Дельта в процентах" - пустое поле для заполнения
- "Ссылка на источник" - пустое поле для заполнения
- "Цена 2 позиции\nB2C c НДС" - пустое поле для заполнения

### Выходной Excel
Дополняется заполненными полями:
- "Цена позиции\nМП c НДС" - цена на маркетплейсе
- "Цена позиции\nB2C c НДС" - B2C цена
- "Дельта в процентах" - процентная разница цен
- "Ссылка на источник" - URL товара на маркетплейсе
- "Цена 2 позиции\nB2C c НДС" - цена на втором маркетплейсе

## РЕКОМЕНДУЕМАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

1. Начните с поиска товаров через `search_products`
2. Получите детальную информацию о найденных товарах через `get_product_details`
3. Проанализируйте статистику через `get_statistics`
4. При необходимости, повторите поиск для других товаров

## ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Поиск конкретного товара
```
search_products("Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ")
```

### Пример 2: Получение детальной информации о товаре
```
get_product_details(195385.0)
```

### Пример 3: Получение общей статистики
```
get_statistics()
```

## EXCEL ИНСТРУМЕНТЫ

### 1. parse_excel_file(file_path: str, sheet_name: Optional[str] = None, header_row: int = 0, max_rows: Optional[int] = None)
Парсинг Excel файла и возврат структурированных данных.
- **Принимает**: путь к файлу, название листа (опционально), номер строки заголовков, максимальное количество строк
- **Возвращает**: структурированные данные из Excel файла
- **Особенности**:
  - Поддержка различных листов Excel файла
  - Автоматическое определение заголовков
  - Обработка различных типов данных
  - Возможность ограничения количества читаемых строк

**Пример использования**:
```
parse_excel_file("data/input.xlsx", sheet_name="Данные", header_row=0, max_rows=100)
```

### 2. get_excel_info(file_path: str)
Получение информации о структуре Excel файла без полного чтения данных.
- **Принимает**: путь к Excel файлу
- **Возвращает**: информацию о листах, заголовках, размерах
- **Особенности**:
  - Быстрое получение метаданных файла
  - Информация о всех листах в файле
  - Определение заголовков и размеров данных

**Пример использования**:
```
get_excel_info("data/input.xlsx")
```

### 3. export_to_excel(data: List[Dict], file_path: str, sheet_name: str = "Data", include_index: bool = False, auto_adjust_columns: bool = True, apply_formatting: bool = True)
Экспорт данных в Excel файл с форматированием.
- **Принимает**: данные для экспорта, путь к файлу, настройки форматирования
- **Возвращает**: результат экспорта
- **Особенности**:
  - Автоматическое форматирование таблиц
  - Подгонка ширины колонок
  - Применение стилей к заголовкам
  - Настраиваемые параметры экспорта

**Пример использования**:
```
export_to_excel(data, "data/output.xlsx", sheet_name="Результаты", apply_formatting=True)
```

### 4. filter_excel_data(data: List[Dict], filters: Dict)
Фильтрация данных Excel по заданным критериям.
- **Принимает**: данные для фильтрации, критерии фильтрации
- **Возвращает**: отфильтрованные данные
- **Особенности**:
  - Поддержка сложных критериев фильтрации
  - Числовые и текстовые фильтры
  - Множественные условия фильтрации

**Пример использования**:
```
filter_excel_data(data, {"Категория": "Хозтовары", "Цена": {"greater_than": 1000}})
```

### 5. transform_excel_data(data: List[Dict], transformations: Dict)
Трансформация данных Excel согласно заданным правилам.
- **Принимает**: данные для трансформации, правила трансформации
- **Возвращает**: трансформированные данные
- **Особенности**:
  - Преобразование типов данных
  - Строковые операции (замена, изменение регистра)
  - Математические операции с числами
  - Настраиваемые правила трансформации

**Пример использования**:
```
transform_excel_data(data, {"model_name": {"to_upper": true}, "price": {"multiply": 1.2}})
```

### 6. parse_excel_and_save_to_database(file_path: str, sheet_name: Optional[str] = None, header_row: int = 0, start_row: Optional[int] = None, max_rows: Optional[int] = None)
**УЛУЧШЕННЫЙ ИНСТРУМЕНТ** - Парсинг Excel файла и автоматическое сохранение товаров в базу данных с поддержкой диапазонов.
- **Принимает**: путь к файлу, название листа (опционально), номер строки заголовков, начальная строка данных, максимальное количество строк
- **Возвращает**: результат парсинга и сохранения в БД
- **Особенности**:
  - Автоматически парсит Excel файл с товарами
  - **НОВОЕ**: Поддержка чтения определенного диапазона строк (start_row, max_rows)
  - **НОВОЕ**: Возможность загружать большие файлы частями
  - Сохраняет новые товары в базу данных SQLite
  - Обновляет существующие товары при совпадении кода
  - Поддерживает стандартный формат Excel с полями: "Код\nмодели", "model_name", "Категория", "Единица измерения", "Приоритет \n1 Источники", "Приоритет \n2 Источники"
  - Обрабатывает ошибки и предоставляет детальную статистику
  - Возвращает информацию о созданных и обновленных товарах

**Примеры использования**:
```
# Загрузить все товары
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0)

# Загрузить товары с 151 по 300 строку
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0, start_row=150, max_rows=150)

# Загрузить следующие 100 товаров начиная с 301 строки
parse_excel_and_save_to_database("data/Таблица на вход.xlsx", sheet_name="Лист1", header_row=0, start_row=300, max_rows=100)
```

**Пример ответа**:
```json
{
  "status": "success",
  "message": "Успешно обработано 150 товаров из Excel файла",
  "file_path": "data/Таблица на вход.xlsx",
  "start_row": 150,
  "rows_requested": 150,
  "total_rows_parsed": 150,
  "products_created": 120,
  "products_updated": 30,
  "total_processed": 150,
  "products_saved": [
    {
      "code": 195385.0,
      "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
      "action": "created",
      "id": 1
    }
  ],
  "parse_info": {
    "sheet_name": "Лист1",
    "columns": ["Код\nмодели", "model_name", "Категория"],
    "available_sheets": ["Лист1", "Лист2"],
    "data_range": "строки 150-299"
  },
  "timestamp": "2023-07-21T15:30:45"
}
```

## РАБОЧИЙ ПРОЦЕСС С EXCEL

### БЫСТРЫЙ СПОСОБ (РЕКОМЕНДУЕТСЯ)
**Для загрузки товаров из Excel в базу данных:**
1. Используйте `parse_excel_and_save_to_database` для одновременного парсинга и сохранения
2. Функция автоматически создаст новые товары и обновит существующие
3. Получите детальную статистику по обработанным товарам

### ПОШАГОВЫЙ СПОСОБ (ДЛЯ СЛОЖНОЙ ОБРАБОТКИ)

#### Этап 1: Анализ структуры файла
- Используйте `get_excel_info` для получения информации о структуре Excel файла
- Определите листы, заголовки и размеры данных

#### Этап 2: Парсинг данных
- Используйте `parse_excel_file` для чтения данных из Excel файла
- Настройте параметры чтения (лист, заголовки, количество строк)

#### Этап 3: Обработка данных
- Применяйте `filter_excel_data` для фильтрации данных по критериям
- Используйте `transform_excel_data` для преобразования данных

#### Этап 4: Экспорт результатов
- Экспортируйте обработанные данные с помощью `export_to_excel`
- Настройте форматирование и стили для лучшего представления

### ИНТЕГРАЦИЯ С ОСНОВНОЙ СИСТЕМОЙ
После загрузки товаров в базу данных через `parse_excel_and_save_to_database`:
1. Используйте `get_product_list` для получения списка всех товаров
2. Выполняйте поиск цен через `search_products` для конкретных товаров
3. Сохраняйте найденные цены через `save_product_prices`
4. Получайте статистику через `get_statistics`

Используйте инструменты последовательно для полного анализа товаров и генерации отчетов.
"""

@mcp.prompt("system")
def get_system_prompt() -> str:
    """Get system prompt for AI agent"""
    return SYSTEM_PROMPT

# MCP Tools implementations
async def _search_products(model_name: str, ctx: Context = None) -> dict:
    """
    Internal function to search for products across multiple marketplaces
    
    Args:
        model_name: Name of the product model to search for
        ctx: MCP context object
        
    Returns:
        Dictionary with search results from different marketplaces
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на поиск товара: '{model_name}'")
    
    try:
        # Валидация входных данных
        if not model_name or not isinstance(model_name, str) or len(model_name.strip()) == 0:
            error = ValidationError("Необходимо указать непустое название модели товара", field="model_name", value=model_name)
            return create_user_friendly_error(error, "поиск товаров")
        
        # Проверяем инициализацию компонентов
        if search_engine is None:
            logger.error("Поисковый движок не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: поисковый движок не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем список всех маркетплейсов
        marketplaces = get_all_marketplaces()
        logger.info(f"Поиск будет выполнен на {len(marketplaces)} маркетплейсах")
        
        # Выполняем поиск через поисковый движок
        # Передаем playwright_tools из контекста, если они доступны
        playwright_tools = ctx.tools.get("playwright") if ctx and hasattr(ctx, "tools") else None
        
        search_results = await search_engine.search_product(
            model_name=model_name,
            marketplaces=marketplaces,
            playwright_tools=playwright_tools
        )
        
        # Проверяем результаты поиска
        if not search_results:
            logger.warning(f"Не получены результаты поиска для '{model_name}'")
            log_recovery_attempt(
                component="server",
                action="Возврат пустого результата поиска",
                success=False
            )
            return {
                "status": "not_found",
                "message": "Товар не найден ни на одном из маркетплейсов",
                "user_message": "По вашему запросу товары не найдены, попробуйте изменить поисковый запрос",
                "query": model_name,
                "results": [],
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Логируем успешные результаты
        successful_results = [r for r in search_results.get("results", []) if r.get("product_found")]
        logger.info(
            f"Поиск завершен: найдено {len(successful_results)} результатов из {len(search_results.get('results', []))}"
        )
        
        # Если есть успешные результаты, сохраняем их в базу данных
        if successful_results and database_manager:
            try:
                # Здесь можно добавить сохранение результатов в базу данных
                # Это будет реализовано в последующих задачах
                log_recovery_attempt(
                    component="server",
                    action="Подготовка к сохранению результатов в БД",
                    success=True
                )
                pass
            except Exception as db_error:
                error_handler.log_error(
                    error=db_error,
                    category=ErrorCategory.DATABASE,
                    severity=ErrorSeverity.MEDIUM,
                    component="server",
                    details={"operation": "save_search_results", "model_name": model_name},
                    recovery_action="Продолжение без сохранения в БД"
                )
        
        # Возвращаем результаты поиска
        return {
            "status": "success",
            "query": model_name,
            "results": search_results.get("results", []),
            "total_found": search_results.get("total_found", 0),
            "search_timestamp": search_results.get("search_timestamp", "")
        }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "search_products", "model_name": model_name},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "поиск товаров")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def search_products(model_name: str, ctx: Context = None) -> dict:
    """
    Search for products across multiple marketplaces
    
    Args:
        model_name: Name of the product model to search for
        ctx: MCP context object
        
    Returns:
        Dictionary with search results from different marketplaces
    """
    return await _search_products(model_name, ctx)

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_product_details(product_code: float, ctx: Context = None) -> dict:
    """
    Get detailed information about a product including price comparison
    
    Args:
        product_code: Unique product code from the database
        ctx: MCP context object
        
    Returns:
        Dictionary with detailed product information and price data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на получение информации о товаре с кодом: {product_code}")
    
    try:
        # Валидация входных данных
        if not isinstance(product_code, (int, float)):
            error = ValidationError("Код товара должен быть числом", field="product_code", value=product_code)
            return create_user_friendly_error(error, "получение информации о товаре")
        
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем информацию о продукте из базы данных
        product = await database_manager.get_product_by_code(product_code)
        
        if not product:
            logger.warning(f"Продукт с кодом {product_code} не найден в базе данных")
            log_recovery_attempt(
                component="server",
                action=f"Продукт с кодом {product_code} не найден",
                success=False
            )
            return {
                "status": "not_found",
                "message": f"Продукт с кодом {product_code} не найден",
                "error_code": "PRODUCT_NOT_FOUND",
                "user_message": "Товар с указанным кодом не найден в базе данных",
                "recoverable": False,
                "retry_suggested": False
            }
        
        # Получаем цены продукта с разных маркетплейсов
        prices = await database_manager.get_product_prices(product["id"])
        
        # Если цены не найдены, возвращаем только информацию о продукте
        if not prices:
            logger.info(f"Для продукта с кодом {product_code} не найдены цены")
            log_recovery_attempt(
                component="server",
                action="Возврат информации о товаре без цен",
                success=True
            )
            return {
                "status": "success",
                "product": {
                    "code": product["code"],
                    "model_name": product["model_name"],
                    "category": product["category"],
                    "unit": product["unit"],
                    "priority_1_source": product["priority_1_source"],
                    "priority_2_source": product["priority_2_source"]
                },
                "prices": [],
                "price_analysis": {
                    "min_price": None,
                    "max_price": None,
                    "delta_percent": None
                },
                "message": "Для данного продукта не найдены цены на маркетплейсах"
            }
        
        # Анализируем цены для расчета минимальной, максимальной и дельты
        valid_prices = [p for p in prices if p["price"] is not None and p["price"] > 0]
        
        price_analysis = {
            "min_price": None,
            "max_price": None,
            "delta_percent": None
        }
        
        if valid_prices:
            # Находим минимальную цену
            min_price_item = min(valid_prices, key=lambda x: x["price"])
            price_analysis["min_price"] = {
                "value": min_price_item["price"],
                "marketplace": min_price_item["marketplace"]
            }
            
            # Находим максимальную цену
            max_price_item = max(valid_prices, key=lambda x: x["price"])
            price_analysis["max_price"] = {
                "value": max_price_item["price"],
                "marketplace": max_price_item["marketplace"]
            }
            
            # Рассчитываем процентную дельту между мин и макс ценами
            if min_price_item["price"] > 0:
                delta = ((max_price_item["price"] - min_price_item["price"]) / min_price_item["price"]) * 100
                price_analysis["delta_percent"] = round(delta, 2)
        
        # Формируем итоговый ответ
        response = {
            "status": "success",
            "product": {
                "code": product["code"],
                "model_name": product["model_name"],
                "category": product["category"],
                "unit": product["unit"],
                "priority_1_source": product["priority_1_source"],
                "priority_2_source": product["priority_2_source"]
            },
            "prices": prices,
            "price_analysis": price_analysis
        }
        
        logger.info(f"Успешно получена информация о товаре с кодом {product_code}")
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение информации о товаре {product_code}",
            success=True
        )
        return response
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_product_details", "product_code": product_code},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение информации о товаре")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_product_list(offset: int = 0, limit: int = 150, filter_status: str = "all", ctx: Context = None) -> dict:
    """
    Get list of all product SKUs from the database with pagination support
    
    Args:
        offset: Starting position (0-based index) for pagination
        limit: Maximum number of products to return (default: 150, if None, returns all from offset)
        filter_status: Filter by processing status ("all", "processed", "not_processed")
        ctx: MCP context object
        
    Returns:
        Dictionary with list of product codes (SKUs) and basic info with pagination info
        Each product includes processing status (processed/not_processed)
        
    Usage Examples:
        - Get first 150 products (recommended): offset=0, limit=150
        - Get products 151-300: offset=150, limit=150
        - Get products 301-450: offset=300, limit=150
        - Get all products from position 100: offset=99, limit=None
        - Get all products: offset=0, limit=None
        - Get only processed products: filter_status="processed"
        - Get only unprocessed products: filter_status="not_processed"
        
    Recommendation: Use limit=150 for optimal performance and memory usage
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на получение списка SKU товаров")
    
    try:
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем все продукты из базы данных
        products = await database_manager.get_all_products()
        
        if not products:
            logger.info("В базе данных нет товаров")
            return {
                "status": "no_data",
                "message": "В базе данных нет товаров",
                "user_message": "База данных пока не содержит товаров",
                "products": [],
                "total_count": 0,
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Формируем список SKU с базовой информацией и статусом обработки
        product_list = []
        for product in products:
            # Проверяем, есть ли у товара цены (обработан ли он)
            has_prices = await database_manager.has_product_prices(product["id"])
            
            product_info = {
                "sku": product["code"],
                "model_name": product["model_name"],
                "category": product["category"],
                "unit": product["unit"],
                "processed": has_prices,
                "status": "processed" if has_prices else "not_processed"
            }
            
            # Применяем фильтр по статусу обработки
            if filter_status == "all":
                product_list.append(product_info)
            elif filter_status == "processed" and has_prices:
                product_list.append(product_info)
            elif filter_status == "not_processed" and not has_prices:
                product_list.append(product_info)
        
        total_count = len(product_list)
        
        # Применяем пагинацию
        if offset < 0:
            offset = 0
        
        if offset >= total_count:
            logger.info(f"Offset {offset} превышает общее количество товаров {total_count}")
            return {
                "status": "success",
                "products": [],
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "filter_status": filter_status,
                "returned_count": 0,
                "has_more": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Применяем срез для пагинации
        if limit is None:
            paginated_products = product_list[offset:]
        else:
            if limit <= 0:
                limit = 150  # Рекомендуемое значение по умолчанию
            paginated_products = product_list[offset:offset + limit]
        
        returned_count = len(paginated_products)
        has_more = (offset + returned_count) < total_count
        
        logger.info(f"Получен список из {returned_count} товаров (offset: {offset}, limit: {limit}, total: {total_count})")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение списка {returned_count} товаров с пагинацией",
            success=True
        )
        
        return {
            "status": "success",
            "products": paginated_products,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "filter_status": filter_status,
            "returned_count": returned_count,
            "has_more": has_more,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_product_list"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение списка товаров")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_statistics(ctx: Context = None) -> dict:
    """
    Get statistics about processed products and price comparisons
    
    Args:
        ctx: MCP context object
        
    Returns:
        Dictionary with comprehensive statistics about the processed data
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на получение статистики")
    
    try:
        # Проверяем инициализацию компонентов
        if statistics_generator is None:
            logger.error("Генератор статистики не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: генератор статистики не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Генерируем полную статистику через StatisticsGenerator
        logger.info("Генерация статистики через StatisticsGenerator...")
        full_statistics = await statistics_generator.generate_full_statistics()
        
        # Проверяем, что статистика получена
        if not full_statistics:
            logger.warning("Не удалось получить статистику")
            log_recovery_attempt(
                component="server",
                action="Возврат пустой статистики",
                success=True
            )
            return {
                "status": "no_data",
                "message": "Нет данных для генерации статистики",
                "user_message": "В базе данных пока нет обработанных товаров для анализа",
                "statistics": {
                    "total_products": 0,
                    "products_with_prices": 0,
                    "average_delta_percent": 0.0,
                    "category_breakdown": {},
                    "marketplace_coverage": {}
                },
                "timestamp": datetime.now().isoformat(),
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Формируем ответ в соответствии с требованиями
        response = {
            "status": "success",
            "statistics": {
                "total_products": full_statistics.total_products,
                "products_with_prices": full_statistics.products_with_prices,
                "average_delta_percent": round(full_statistics.average_delta_percent, 2),
                "category_breakdown": full_statistics.category_breakdown,
                "marketplace_coverage": full_statistics.marketplace_coverage
            },
            "timestamp": full_statistics.processing_timestamp.isoformat() if hasattr(full_statistics, 'processing_timestamp') and full_statistics.processing_timestamp else datetime.now().isoformat()
        }
        
        # Логируем успешное получение статистики
        logger.info(
            f"Статистика успешно получена: {full_statistics.total_products} товаров, "
            f"{full_statistics.products_with_prices} с ценами, "
            f"средняя дельта: {full_statistics.average_delta_percent:.2f}%"
        )
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная генерация статистики для {full_statistics.total_products} товаров",
            success=True
        )
        
        return response
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_statistics"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение статистики")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def save_product_prices(product_code: float, search_results: dict, ctx: Context = None) -> dict:
    """
    Save found prices for a specific product to the database
    
    Args:
        product_code: Unique product code from the database
        search_results: Dictionary with search results (supports multiple formats)
        ctx: MCP context object
        
    Returns:
        Dictionary with save operation results
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на сохранение цен для товара с кодом: {product_code}")
    logger.debug(f"Получены данные: {search_results}")
    
    try:
        # Валидация входных данных
        if not isinstance(product_code, (int, float)):
            error = ValidationError("Код товара должен быть числом", field="product_code", value=product_code)
            return create_user_friendly_error(error, "сохранение цен товара")
        
        if not search_results or not isinstance(search_results, dict):
            error = ValidationError("Результаты поиска должны быть словарем", field="search_results", value=search_results)
            return create_user_friendly_error(error, "сохранение цен товара")
        
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем продукт из базы данных
        product = await database_manager.get_product_by_code(product_code)
        if not product:
            logger.warning(f"Продукт с кодом {product_code} не найден в базе данных")
            return {
                "status": "not_found",
                "message": f"Продукт с кодом {product_code} не найден",
                "error_code": "PRODUCT_NOT_FOUND",
                "user_message": "Товар с указанным кодом не найден в базе данных",
                "recoverable": False,
                "retry_suggested": False
            }
        
        # Нормализуем входные данные - поддерживаем различные форматы
        results = []
        
        # Формат 1: {"results": [...]}
        if "results" in search_results and isinstance(search_results["results"], list):
            results = search_results["results"]
            logger.debug(f"Обнаружен формат 1: results array с {len(results)} элементами")
        
        # Формат 2: {"found_offers": [...]}
        elif "found_offers" in search_results and isinstance(search_results["found_offers"], list):
            results = search_results["found_offers"]
            logger.debug(f"Обнаружен формат 2: found_offers array с {len(results)} элементами")
            # Нормализуем структуру для found_offers
            for result in results:
                if "product_found" not in result:
                    result["product_found"] = True  # Если цена есть, значит товар найден
        
        # Формат 3: Прямые поля в корне (один товар)
        elif "marketplace" in search_results and "price" in search_results:
            results = [search_results]
            search_results["product_found"] = True
            logger.debug("Обнаружен формат 3: прямые поля в корне")
        
        # Формат 4: Массив в корне
        elif isinstance(search_results, list):
            results = search_results
            logger.debug(f"Обнаружен формат 4: массив в корне с {len(results)} элементами")
            # Нормализуем структуру
            for result in results:
                if "product_found" not in result:
                    result["product_found"] = True
        
        # Проверяем, что у нас есть данные для сохранения
        if not results:
            logger.warning(f"Нет результатов поиска для сохранения")
            logger.debug(f"Структура полученных данных: {list(search_results.keys())}")
            return {
                "status": "no_data",
                "message": "Нет результатов поиска для сохранения",
                "user_message": "Результаты поиска пусты, нечего сохранять",
                "received_format": list(search_results.keys()),
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Сохраняем цены для каждого маркетплейса
        saved_count = 0
        errors = []
        saved_prices = []
        
        for i, result in enumerate(results):
            logger.debug(f"Обработка результата {i+1}: {result}")
            
            # Проверяем наличие цены (гибко)
            price = result.get("price")
            if not price:
                logger.debug(f"Результат {i+1}: отсутствует цена")
                continue
                
            # Проверяем, что товар найден (если поле есть)
            if "product_found" in result and not result.get("product_found"):
                logger.debug(f"Результат {i+1}: товар не найден")
                continue
                
            try:
                price_data = {
                    "marketplace": result.get("marketplace", "unknown"),
                    "price": float(price),
                    "currency": result.get("currency", "RUB"),
                    "availability": result.get("availability", "Неизвестно"),
                    "product_url": result.get("product_url") or result.get("url")
                }
                
                await database_manager.save_price(product["id"], price_data)
                saved_count += 1
                saved_prices.append({
                    "marketplace": price_data["marketplace"],
                    "price": price_data["price"],
                    "currency": price_data["currency"],
                    "availability": price_data["availability"]
                })
                logger.info(f"Сохранена цена для {price_data['marketplace']}: {price_data['price']} {price_data['currency']}")
                
            except Exception as price_error:
                error_msg = f"Ошибка сохранения цены для {result.get('marketplace', 'unknown')}: {price_error}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Формируем ответ
        if saved_count > 0:
            logger.info(f"Успешно сохранено {saved_count} цен для товара {product_code}")
            log_recovery_attempt(
                component="server",
                action=f"Сохранение {saved_count} цен для товара {product_code}",
                success=True
            )
            
            response = {
                "status": "success",
                "message": f"Сохранено {saved_count} цен для товара {product_code}",
                "product_code": product_code,
                "product_name": product["model_name"],
                "saved_prices": saved_count,
                "total_results": len(results),
                "prices_saved": saved_prices,
                "timestamp": datetime.now().isoformat()
            }
            
            if errors:
                response["warnings"] = errors
                
            return response
        else:
            logger.warning(f"Не удалось сохранить ни одной цены для товара {product_code}")
            return {
                "status": "no_data",
                "message": "Не удалось сохранить ни одной цены",
                "user_message": "В результатах поиска нет валидных цен для сохранения",
                "product_code": product_code,
                "total_results": len(results),
                "errors": errors,
                "recoverable": True,
                "retry_suggested": True
            }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "save_product_prices", "product_code": product_code},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "сохранение цен товара")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def update_all_prices(limit: int = 10, ctx: Context = None) -> dict:
    """
    Update prices for multiple products from the database
    
    Args:
        limit: Maximum number of products to update (default: 10, max: 50)
        ctx: MCP context object
        
    Returns:
        Dictionary with batch update results
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на массовое обновление цен (лимит: {limit})")
    
    try:
        # Валидация входных данных
        if not isinstance(limit, int) or limit <= 0:
            error = ValidationError("Лимит должен быть положительным числом", field="limit", value=limit)
            return create_user_friendly_error(error, "массовое обновление цен")
        
        if limit > 50:
            limit = 50  # Ограничиваем максимальное количество для безопасности
            logger.warning("Лимит ограничен до 50 товаров для безопасности")
        
        # Проверяем инициализацию компонентов
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем список продуктов для обновления
        products = await database_manager.get_all_products(limit=limit)
        if not products:
            logger.info("Нет товаров для обновления цен")
            return {
                "status": "no_data",
                "message": "В базе данных нет товаров для обновления",
                "user_message": "База данных не содержит товаров для обновления цен",
                "recoverable": True,
                "retry_suggested": False
            }
        
        # Обновляем цены для каждого продукта
        results = {
            "total_products": len(products),
            "successful_updates": 0,
            "failed_updates": 0,
            "products_processed": [],
            "errors": []
        }
        
        for i, product in enumerate(products, 1):
            try:
                logger.info(f"[{i}/{len(products)}] Обновление цен для товара {product['code']}: {product['model_name']}")
                
                # Выполняем поиск цен
                search_result = await search_products(product["model_name"], ctx)
                
                if search_result.get("status") == "success" and search_result.get("results"):
                    # Сохраняем найденные цены
                    save_result = await save_product_prices(product["code"], search_result, ctx)
                    
                    product_result = {
                        "code": product["code"],
                        "name": product["model_name"],
                        "status": save_result.get("status"),
                        "saved_prices": save_result.get("saved_prices", 0),
                        "found_results": len(search_result.get("results", []))
                    }
                    
                    if save_result.get("status") == "success":
                        results["successful_updates"] += 1
                        logger.info(f"[{i}/{len(products)}] Успешно обновлены цены для товара {product['code']}: {save_result.get('saved_prices', 0)} цен")
                    else:
                        results["failed_updates"] += 1
                        logger.warning(f"[{i}/{len(products)}] Не удалось сохранить цены для товара {product['code']}")
                        if save_result.get("warnings"):
                            product_result["warnings"] = save_result["warnings"]
                else:
                    results["failed_updates"] += 1
                    product_result = {
                        "code": product["code"],
                        "name": product["model_name"],
                        "status": "search_failed",
                        "saved_prices": 0,
                        "found_results": 0,
                        "message": "Поиск не дал результатов"
                    }
                    logger.warning(f"[{i}/{len(products)}] Поиск не дал результатов для товара {product['code']}")
                
                results["products_processed"].append(product_result)
                
            except Exception as product_error:
                error_msg = f"Ошибка обновления товара {product['code']}: {product_error}"
                results["errors"].append(error_msg)
                results["failed_updates"] += 1
                logger.error(f"[{i}/{len(products)}] {error_msg}")
        
        # Формируем итоговый ответ
        success_rate = (results["successful_updates"] / results["total_products"]) * 100 if results["total_products"] > 0 else 0
        
        response = {
            "status": "completed",
            "message": f"Массовое обновление завершено: {results['successful_updates']}/{results['total_products']} успешно",
            "results": results,
            "success_rate": round(success_rate, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Массовое обновление завершено: {results['successful_updates']}/{results['total_products']} успешно ({success_rate:.1f}%)")
        
        log_recovery_attempt(
            component="server",
            action=f"Массовое обновление {results['total_products']} товаров",
            success=results["successful_updates"] > 0
        )
        
        return response
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "update_all_prices", "limit": limit},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "массовое обновление цен")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.LOW,
    component="mcp_server",
    recovery_action="Возврат информации о лицензии"
)
@mcp.tool()
async def check_license_status(ctx: Context = None) -> dict:
    """
    Check the current license status and information
    
    Args:
        ctx: MCP context object
        
    Returns:
        Dictionary with license status and information
    """
    from .error_handling import (
        create_user_friendly_error,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на проверку статуса лицензии")
    
    try:
        # Создаем экземпляр менеджера лицензий
        license_manager = LicenseManager()
        
        # Получаем информацию о лицензии
        license_info = license_manager.get_license_info()
        
        is_valid = license_info["is_valid"]
        license_data = license_info["license_data"]
        
        if is_valid:
            logger.info("Лицензия действительна")
            log_recovery_attempt(
                component="server",
                action="Успешная проверка лицензии",
                success=True
            )
            
            return {
                "status": "valid",
                "message": "Лицензия действительна",
                "license_key": license_info["license_key"],
                "license_info": {
                    "valid": license_data.get("valid", False),
                    "checked_at": license_data.get("checked_at"),
                    "expires_at": license_data.get("expires_at"),
                    "plan": license_data.get("plan"),
                    "features": license_data.get("features", [])
                },
                "api_url": license_info["api_url"]
            }
        else:
            logger.warning("Лицензия недействительна")
            log_recovery_attempt(
                component="server",
                action="Обнаружена недействительная лицензия",
                success=False
            )
            
            return {
                "status": "invalid",
                "message": "Лицензия недействительна",
                "license_key": license_info["license_key"],
                "error": license_data.get("error", "UNKNOWN_ERROR"),
                "error_message": license_data.get("message", "Неизвестная ошибка"),
                "user_message": license_data.get("user_message", "Лицензия недействительна"),
                "api_url": license_info["api_url"]
            }
            
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            component="server",
            details={"tool": "check_license_status"},
            recovery_action="Возврат информации об ошибке проверки лицензии"
        )
        return create_user_friendly_error(e, "проверка статуса лицензии")

@handle_errors(
    category=ErrorCategory.SYSTEM,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат результата установки лицензии"
)
@mcp.tool()
async def set_license_key(license_key: str, ctx: Context = None) -> dict:
    """
    Set a new license key for the system
    
    Args:
        license_key: New license key to set
        ctx: MCP context object
        
    Returns:
        Dictionary with result of license key setting
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info("Запрос на установку нового лицензионного ключа")
    
    try:
        # Валидация входных данных
        if not license_key or not isinstance(license_key, str) or len(license_key.strip()) == 0:
            error = ValidationError("Необходимо указать непустой лицензионный ключ", field="license_key", value=license_key)
            return create_user_friendly_error(error, "установка лицензионного ключа")
        
        license_key = license_key.strip()
        
        # Создаем экземпляр менеджера лицензий
        license_manager = LicenseManager()
        
        # Устанавливаем новый ключ
        success = license_manager.set_license_key(license_key, save_to_config=True)
        
        if success:
            logger.info("Новый лицензионный ключ успешно установлен")
            log_recovery_attempt(
                component="server",
                action="Успешная установка нового лицензионного ключа",
                success=True
            )
            
            # Получаем информацию о новой лицензии
            license_info = license_manager.get_license_info()
            
            return {
                "status": "success",
                "message": "Лицензионный ключ успешно установлен и проверен",
                "license_key": license_key,
                "license_info": license_info["license_data"],
                "saved_to_config": True
            }
        else:
            logger.error("Не удалось установить новый лицензионный ключ")
            log_recovery_attempt(
                component="server",
                action="Неудачная установка лицензионного ключа",
                success=False
            )
            
            return {
                "status": "error",
                "message": "Лицензионный ключ недействителен",
                "error_code": "INVALID_LICENSE_KEY",
                "user_message": "Указанный лицензионный ключ недействителен",
                "license_key": license_key,
                "recoverable": True,
                "retry_suggested": True
            }
            
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "set_license_key", "license_key": license_key[:8] + "..." if license_key else "None"},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "установка лицензионного ключа")

# Excel Tools MCP Functions

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def parse_excel_file(file_path: str, sheet_name: Optional[str] = None, 
                          header_row: int = 0, max_rows: Optional[int] = None, 
                          ctx: Context = None) -> dict:
    """
    Parse Excel file and return structured data
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name (if None, uses first sheet)
        header_row: Header row number (0-based)
        max_rows: Maximum number of rows to read
        ctx: MCP context object
        
    Returns:
        Dictionary with parsed Excel data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на парсинг Excel файла: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        if header_row < 0:
            error = ValidationError("Номер строки заголовков не может быть отрицательным", field="header_row", value=header_row)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        if max_rows is not None and max_rows <= 0:
            error = ValidationError("Максимальное количество строк должно быть положительным", field="max_rows", value=max_rows)
            return create_user_friendly_error(error, "парсинг Excel файла")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Парсим Excel файл
        result = await excel_tools.parse_excel_file(
            file_path=file_path,
            sheet_name=sheet_name,
            header_row=header_row,
            max_rows=max_rows
        )
        
        logger.info(f"Успешно распарсен Excel файл: {result.get('total_rows', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешный парсинг Excel файла {file_path}",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "parse_excel_file", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "парсинг Excel файла")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def get_excel_info(file_path: str, ctx: Context = None) -> dict:
    """
    Get information about Excel file structure without reading all data
    
    Args:
        file_path: Path to Excel file
        ctx: MCP context object
        
    Returns:
        Dictionary with Excel file structure information
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на получение информации о Excel файле: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "получение информации о Excel файле")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Получаем информацию о файле
        result = await excel_tools.get_excel_info(file_path)
        
        logger.info(f"Получена информация о Excel файле: {result.get('total_sheets', 0)} листов")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешное получение информации о Excel файле {file_path}",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "get_excel_info", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "получение информации о Excel файле")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def export_to_excel(data: List[Dict[str, Any]], file_path: str,
                         sheet_name: str = "Data", include_index: bool = False,
                         auto_adjust_columns: bool = True, apply_formatting: bool = True,
                         ctx: Context = None) -> dict:
    """
    Export data to Excel file with formatting
    
    Args:
        data: List of dictionaries with data to export
        file_path: Path to save Excel file
        sheet_name: Sheet name
        include_index: Whether to include row index
        auto_adjust_columns: Auto-adjust column widths
        apply_formatting: Apply formatting to the file
        ctx: MCP context object
        
    Returns:
        Dictionary with export result
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на экспорт данных в Excel файл: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь для сохранения Excel файла", field="file_path", value=file_path)
            return create_user_friendly_error(error, "экспорт в Excel файл")
        
        if not data or not isinstance(data, list):
            error = ValidationError("Данные должны быть списком словарей", field="data", value=type(data).__name__)
            return create_user_friendly_error(error, "экспорт в Excel файл")
        
        if not sheet_name or not isinstance(sheet_name, str):
            error = ValidationError("Название листа должно быть непустой строкой", field="sheet_name", value=sheet_name)
            return create_user_friendly_error(error, "экспорт в Excel файл")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Экспортируем данные
        result = await excel_tools.export_to_excel(
            data=data,
            file_path=file_path,
            sheet_name=sheet_name,
            include_index=include_index,
            auto_adjust_columns=auto_adjust_columns,
            apply_formatting=apply_formatting
        )
        
        logger.info(f"Успешно экспортированы данные в Excel файл: {result.get('rows_exported', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешный экспорт данных в Excel файл {file_path}",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "export_to_excel", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "экспорт в Excel файл")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def filter_excel_data(data: List[Dict[str, Any]], filters: Dict[str, Any], 
                           ctx: Context = None) -> dict:
    """
    Filter Excel data by specified criteria
    
    Args:
        data: Source data to filter
        filters: Dictionary with filter criteria
        ctx: MCP context object
        
    Returns:
        Filtered data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на фильтрацию данных по критериям: {filters}")
    
    try:
        # Валидация входных данных
        if not data or not isinstance(data, list):
            error = ValidationError("Данные должны быть списком словарей", field="data", value=type(data).__name__)
            return create_user_friendly_error(error, "фильтрация данных")
        
        if not filters or not isinstance(filters, dict):
            error = ValidationError("Фильтры должны быть словарем", field="filters", value=type(filters).__name__)
            return create_user_friendly_error(error, "фильтрация данных")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Фильтруем данные
        result = await excel_tools.filter_excel_data(data, filters)
        
        logger.info(f"Фильтрация завершена: {result.get('filtered_count', 0)} из {result.get('original_count', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная фильтрация данных",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "filter_excel_data", "filters": filters},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "фильтрация данных")

@handle_errors(
    category=ErrorCategory.PARSING,
    severity=ErrorSeverity.MEDIUM,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def transform_excel_data(data: List[Dict[str, Any]], transformations: Dict[str, Any], 
                              ctx: Context = None) -> dict:
    """
    Transform Excel data according to specified rules
    
    Args:
        data: Source data to transform
        transformations: Dictionary with transformation rules
        ctx: MCP context object
        
    Returns:
        Transformed data
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на трансформацию данных по правилам: {transformations}")
    
    try:
        # Валидация входных данных
        if not data or not isinstance(data, list):
            error = ValidationError("Данные должны быть списком словарей", field="data", value=type(data).__name__)
            return create_user_friendly_error(error, "трансформация данных")
        
        if not transformations or not isinstance(transformations, dict):
            error = ValidationError("Правила трансформации должны быть словарем", field="transformations", value=type(transformations).__name__)
            return create_user_friendly_error(error, "трансформация данных")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Трансформируем данные
        result = await excel_tools.transform_excel_data(data, transformations)
        
        logger.info(f"Трансформация завершена: {result.get('transformed_count', 0)} строк")
        
        log_recovery_attempt(
            component="server",
            action=f"Успешная трансформация данных",
            success=True
        )
        
        return result
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "transform_excel_data", "transformations": transformations},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "трансформация данных")

@handle_errors(
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.HIGH,
    component="mcp_server",
    recovery_action="Возврат пользовательского сообщения об ошибке"
)
@mcp.tool()
async def parse_excel_and_save_to_database(file_path: str, sheet_name: Optional[str] = None, 
                                          header_row: int = 0, start_row: Optional[int] = None,
                                          max_rows: Optional[int] = None,
                                          ctx: Context = None) -> dict:
    """
    Parse Excel file and automatically save products to database
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name (if None, uses first sheet)
        header_row: Header row number (0-based)
        start_row: Starting row number for data reading (0-based, after header). If None, starts from header_row + 1
        max_rows: Maximum number of rows to read from start_row. If None, reads all remaining rows
        ctx: MCP context object
        
    Returns:
        Dictionary with parsing and saving results
    """
    from .error_handling import (
        create_user_friendly_error,
        ValidationError,
        error_handler,
        ErrorCategory,
        ErrorSeverity,
        log_recovery_attempt
    )
    
    logger.info(f"Запрос на парсинг Excel файла и сохранение в БД: {file_path}")
    
    try:
        # Валидация входных данных
        if not file_path or not isinstance(file_path, str):
            error = ValidationError("Необходимо указать путь к Excel файлу", field="file_path", value=file_path)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        if start_row is not None and start_row < 0:
            error = ValidationError("Начальная строка не может быть отрицательной", field="start_row", value=start_row)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        if max_rows is not None and max_rows <= 0:
            error = ValidationError("Количество строк должно быть положительным", field="max_rows", value=max_rows)
            return create_user_friendly_error(error, "парсинг и сохранение Excel файла")
        
        # Проверяем инициализацию компонентов
        if excel_tools is None:
            logger.error("Excel инструменты не инициализированы")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: Excel инструменты не инициализированы",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        if database_manager is None:
            logger.error("Менеджер базы данных не инициализирован")
            return {
                "status": "error",
                "message": "Внутренняя ошибка: менеджер базы данных не инициализирован",
                "error_code": "COMPONENT_NOT_INITIALIZED",
                "user_message": "Система временно недоступна, попробуйте позже",
                "recoverable": True,
                "retry_suggested": True
            }
        
        # Шаг 1: Парсим Excel файл
        logger.info("Шаг 1: Парсинг Excel файла...")
        
        # Определяем параметры для чтения Excel
        if start_row is not None:
            # Если указана начальная строка, нужно пропустить строки до неё
            skip_rows = start_row
            # Читаем заголовки отдельно
            header_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=1  # Читаем только заголовки
            )
            
            if header_result.get("status") != "success":
                logger.error(f"Ошибка чтения заголовков Excel файла: {header_result}")
                return {
                    "status": "error",
                    "message": "Ошибка чтения заголовков Excel файла",
                    "parse_result": header_result,
                    "user_message": "Не удалось прочитать заголовки Excel файла",
                    "recoverable": True,
                    "retry_suggested": True
                }
            
            # Теперь читаем данные начиная с указанной строки
            # Нужно использовать более низкоуровневый подход для чтения с определенной строки
            logger.info(f"Чтение данных начиная со строки {start_row}, максимум {max_rows or 'все'} строк")
            
            # Для упрощения, пока используем существующий метод с корректировкой
            total_rows_to_read = (start_row + max_rows) if max_rows else None
            parse_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=total_rows_to_read
            )
            
            if parse_result.get("status") == "success":
                # Обрезаем данные до нужного диапазона
                all_data = parse_result.get("data", [])
                if start_row < len(all_data):
                    end_row = start_row + max_rows if max_rows else len(all_data)
                    parse_result["data"] = all_data[start_row:end_row]
                    parse_result["total_rows"] = len(parse_result["data"])
                    logger.info(f"Выбран диапазон строк {start_row}-{min(end_row, len(all_data))}, получено {len(parse_result['data'])} строк")
                else:
                    parse_result["data"] = []
                    parse_result["total_rows"] = 0
                    logger.warning(f"Начальная строка {start_row} превышает количество данных в файле ({len(all_data)})")
        else:
            # Обычное чтение с начала
            parse_result = await excel_tools.parse_excel_file(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                max_rows=max_rows
            )
        
        if parse_result.get("status") != "success":
            logger.error(f"Ошибка парсинга Excel файла: {parse_result}")
            return {
                "status": "error",
                "message": "Ошибка парсинга Excel файла",
                "parse_result": parse_result,
                "user_message": "Не удалось прочитать Excel файл, проверьте формат и путь к файлу",
                "recoverable": True,
                "retry_suggested": True
            }
        
        data = parse_result.get("data", [])
        if not data:
            logger.warning("Excel файл не содержит данных")
            return {
                "status": "no_data",
                "message": "Excel файл не содержит данных",
                "user_message": "Excel файл пуст или не содержит данных для обработки",
                "parse_result": parse_result,
                "recoverable": False,
                "retry_suggested": False
            }
        
        range_info = f" (строки {start_row}-{start_row + len(data) - 1})" if start_row is not None else ""
        logger.info(f"Успешно распарсено {len(data)} строк из Excel файла{range_info}")
        
        # Шаг 2: Сохраняем товары в базу данных
        logger.info("Шаг 2: Сохранение товаров в базу данных...")
        saved_count = 0
        updated_count = 0
        errors = []
        saved_products = []
        
        for i, row_data in enumerate(data):
            try:
                # Проверяем наличие обязательных полей
                code = row_data.get("Код\nмодели") or row_data.get("code")
                model_name = row_data.get("model_name")
                
                if not code or not model_name:
                    error_msg = f"Строка {i+1}: отсутствуют обязательные поля (код или название модели)"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # Проверяем, существует ли товар в базе данных
                existing_product = await database_manager.get_product_by_code(float(code))
                
                if existing_product:
                    # Обновляем существующий товар
                    product_data = {
                        "code": float(code),
                        "model_name": model_name,
                        "category": row_data.get("Категория") or row_data.get("category", ""),
                        "unit": row_data.get("Единица измерения") or row_data.get("unit", ""),
                        "priority_1_source": row_data.get("Приоритет \n1 Источники") or row_data.get("priority_1_source", ""),
                        "priority_2_source": row_data.get("Приоритет \n2 Источники") or row_data.get("priority_2_source", "")
                    }
                    
                    success = await database_manager.update_product(product_data)
                    if success:
                        updated_count += 1
                        saved_products.append({
                            "code": code,
                            "model_name": model_name,
                            "action": "updated"
                        })
                        logger.info(f"Обновлен товар с кодом {code}")
                    else:
                        error_msg = f"Строка {i+1}: не удалось обновить товар с кодом {code}"
                        errors.append(error_msg)
                        logger.warning(error_msg)
                else:
                    # Создаем новый товар
                    try:
                        product_id = await database_manager.save_product(row_data)
                        saved_count += 1
                        saved_products.append({
                            "code": code,
                            "model_name": model_name,
                            "action": "created",
                            "id": product_id
                        })
                        logger.info(f"Создан новый товар с кодом {code}, ID: {product_id}")
                    except Exception as save_error:
                        error_msg = f"Строка {i+1}: ошибка сохранения товара с кодом {code}: {save_error}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        
            except Exception as row_error:
                error_msg = f"Строка {i+1}: ошибка обработки: {row_error}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Формируем итоговый ответ
        total_processed = saved_count + updated_count
        
        if total_processed > 0:
            logger.info(f"Успешно обработано {total_processed} товаров: {saved_count} новых, {updated_count} обновлено")
            log_recovery_attempt(
                component="server",
                action=f"Сохранение {total_processed} товаров из Excel в БД",
                success=True
            )
            
            response = {
                "status": "success",
                "message": f"Успешно обработано {total_processed} товаров из Excel файла",
                "file_path": file_path,
                "start_row": start_row,
                "rows_requested": max_rows,
                "total_rows_parsed": len(data),
                "products_created": saved_count,
                "products_updated": updated_count,
                "total_processed": total_processed,
                "products_saved": saved_products,
                "parse_info": {
                    "sheet_name": parse_result.get("sheet_name"),
                    "columns": parse_result.get("columns"),
                    "available_sheets": parse_result.get("available_sheets"),
                    "data_range": f"строки {start_row}-{start_row + len(data) - 1}" if start_row is not None else "все строки"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            if errors:
                response["warnings"] = errors
                response["errors_count"] = len(errors)
                
            return response
        else:
            logger.warning("Не удалось сохранить ни одного товара")
            return {
                "status": "no_data",
                "message": "Не удалось сохранить ни одного товара",
                "user_message": "Все строки Excel файла содержат ошибки или отсутствуют обязательные поля",
                "file_path": file_path,
                "start_row": start_row,
                "rows_requested": max_rows,
                "total_rows_parsed": len(data),
                "errors": errors,
                "errors_count": len(errors),
                "recoverable": True,
                "retry_suggested": True
            }
        
    except Exception as e:
        error_handler.log_error(
            error=e,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            component="server",
            details={"tool": "parse_excel_and_save_to_database", "file_path": file_path},
            recovery_action="Возврат пользовательского сообщения об ошибке"
        )
        return create_user_friendly_error(e, "парсинг и сохранение Excel файла")

# Runners
async def run_stdio():
    print("Запуск MCP сервера offers-check-marketplaces в режиме STDIO")
    print(f"ID приложения: {APP_ID}")
    print(f"Версия Python: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG']:
        value = os.getenv(key, 'не установлено')
        print(f"   {key}: {value}")
    
    # Initialize all system components
    print("Инициализация компонентов системы...")
    try:
        await initialize_components()
        print("Компоненты успешно инициализированы")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        print("Программа завершена из-за ошибки инициализации")
        sys.exit(1)
    
    # Show registered tools
    print("Зарегистрированные MCP инструменты:")
    print("   1. search_products - поиск товаров на маркетплейсах")
    print("   2. get_product_details - детальная информация о товаре")
    print("   3. get_product_list - список всех SKU товаров")
    print("   4. get_statistics - статистика по обработанным товарам")
    print("   5. save_product_prices - сохранение найденных цен в БД")
    print("   6. update_all_prices - массовое обновление цен товаров")
    print("   7. check_license_status - проверка статуса лицензии")
    print("   8. set_license_key - установка нового лицензионного ключа")
    
    print("Ожидание подключения через STDIO...")
    await mcp.run_stdio_async()

async def run_sse_async(host: str, port: int):
    print("Запуск MCP сервера offers-check-marketplaces в режиме SSE")
    print(f"ID приложения: {APP_ID}")
    print(f"Версия Python: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Хост: {host}")
    print(f"Порт: {port}")
    print(f"URL сервера: http://{host}:{port}")
    print(f"Переменные окружения:")
    for key in ['HOST', 'PORT', 'DEBUG']:
        value = os.getenv(key, 'не установлено')
        print(f"   {key}: {value}")
    
    # Initialize all system components
    print("Инициализация компонентов системы...")
    try:
        await initialize_components()
        print("Компоненты успешно инициализированы")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        print("Программа завершена из-за ошибки инициализации")
        sys.exit(1)
    
    # Show registered tools
    print("Зарегистрированные MCP инструменты:")
    print("   1. search_products - поиск товаров на маркетплейсах")
    print("   2. get_product_details - детальная информация о товаре")
    print("   3. get_product_list - список всех SKU товаров")
    print("   4. get_statistics - статистика по обработанным товарам")
    print("   5. save_product_prices - сохранение найденных цен в БД")
    print("   6. update_all_prices - массовое обновление цен товаров")
    print("   7. check_license_status - проверка статуса лицензии")
    print("   8. set_license_key - установка нового лицензионного ключа")
    
    print("Запуск Uvicorn сервера...")
    
    # Create uvicorn config and server
    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run server in current event loop
    await server.serve()

def run_sse(host: str, port: int):
    anyio.run(run_sse_async, host, port)

# CLI
@click.command()
@click.option("--sse", is_flag=True, help="Start as SSE server (otherwise stdio).")
@click.option("--host", default=lambda: os.getenv("HOST", "0.0.0.0"),
              show_default=True, help="Host for SSE mode")
@click.option("--port", type=int, default=lambda: int(os.getenv("PORT", 8000)),
              show_default=True, help="Port for SSE mode")
def main(sse: bool, host: str, port: int):
    print("=" * 60)
    print("Begin start MCP offers-check-marketplaces")
    print("=" * 60)
    print(f"* Режим запуска: {'SSE' if sse else 'STDIO'}")
    print(f"* Время запуска: {os.getenv('TZ', 'системное время')}")
    print(f"* Платформа: {sys.platform}")
    print(f"* Домашняя директория: {os.path.expanduser('~')}")
    print("=" * 60)
    
    if sse:
        run_sse(host, port)
    else:
        anyio.run(run_stdio)

if __name__ == "__main__":
    main()