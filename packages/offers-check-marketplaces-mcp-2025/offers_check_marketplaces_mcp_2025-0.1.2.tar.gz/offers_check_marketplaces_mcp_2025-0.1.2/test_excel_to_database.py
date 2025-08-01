#!/usr/bin/env python3
"""
Тест новой функции parse_excel_and_save_to_database.
Проверяет парсинг Excel файла и сохранение данных в базу данных.
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.server import initialize_components
from offers_check_marketplaces.excel_tools import ExcelTools
from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.user_data_manager import UserDataManager
import pandas as pd

async def create_test_excel_file():
    """Создает тестовый Excel файл с товарами."""
    test_data = [
        {
            "Код\nмодели": 195385.0,
            "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
            "Категория": "Хозтовары и посуда",
            "Единица измерения": "м",
            "Приоритет \n1 Источники": "Комус",
            "Приоритет \n2 Источники": "ВсеИнструменты",
            "Цена позиции\nМП c НДС": "",
            "Цена позиции\nB2C c НДС": "",
            "Дельта в процентах": "",
            "Ссылка на источник": "",
            "Цена 2 позиции\nB2C c НДС": ""
        },
        {
            "Код\nмодели": 195386.0,
            "model_name": "Бумага офисная А4 80г/м2, пачка 500 листов",
            "Категория": "Канцелярские товары",
            "Единица измерения": "пачка",
            "Приоритет \n1 Источники": "Офисмаг",
            "Приоритет \n2 Источники": "Комус",
            "Цена позиции\nМП c НДС": "",
            "Цена позиции\nB2C c НДС": "",
            "Дельта в процентах": "",
            "Ссылка на источник": "",
            "Цена 2 позиции\nB2C c НДС": ""
        },
        {
            "Код\nмодели": 195387.0,
            "model_name": "Ручка шариковая синяя 0.7мм",
            "Категория": "Канцелярские товары",
            "Единица измерения": "шт",
            "Приоритет \n1 Источники": "Комус",
            "Приоритет \n2 Источники": "Офисмаг",
            "Цена позиции\nМП c НДС": "",
            "Цена позиции\nB2C c НДС": "",
            "Дельта в процентах": "",
            "Ссылка на источник": "",
            "Цена 2 позиции\nB2C c НДС": ""
        }
    ]
    
    # Создаем директорию data если не существует
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Создаем Excel файл
    test_file_path = data_dir / "test_products.xlsx"
    df = pd.DataFrame(test_data)
    df.to_excel(test_file_path, index=False, sheet_name="Товары")
    
    print(f"✅ Создан тестовый Excel файл: {test_file_path}")
    print(f"   Содержит {len(test_data)} товаров")
    
    return str(test_file_path)

async def test_parse_excel_and_save():
    """Тестирует новую функцию parse_excel_and_save_to_database."""
    print("=" * 60)
    print("ТЕСТ ФУНКЦИИ parse_excel_and_save_to_database")
    print("=" * 60)
    
    try:
        # Создаем тестовый Excel файл
        test_file_path = await create_test_excel_file()
        
        # Инициализируем компоненты
        print("\n📋 Инициализация компонентов...")
        await initialize_components()
        
        # Импортируем функцию после инициализации
        from offers_check_marketplaces.server import parse_excel_and_save_to_database
        
        # Тестируем функцию
        print(f"\n📊 Тестирование парсинга и сохранения: {test_file_path}")
        result = await parse_excel_and_save_to_database(
            file_path=test_file_path,
            sheet_name="Товары",
            header_row=0
        )
        
        print("\n📈 РЕЗУЛЬТАТ ТЕСТА:")
        print(f"   Статус: {result.get('status')}")
        print(f"   Сообщение: {result.get('message')}")
        
        if result.get('status') == 'success':
            print(f"   📁 Файл: {result.get('file_path')}")
            print(f"   📊 Строк распарсено: {result.get('total_rows_parsed')}")
            print(f"   ➕ Товаров создано: {result.get('products_created')}")
            print(f"   🔄 Товаров обновлено: {result.get('products_updated')}")
            print(f"   ✅ Всего обработано: {result.get('total_processed')}")
            
            if result.get('warnings'):
                print(f"   ⚠️  Предупреждений: {len(result.get('warnings'))}")
                for warning in result.get('warnings')[:3]:  # Показываем первые 3
                    print(f"      - {warning}")
            
            # Показываем несколько сохраненных товаров
            saved_products = result.get('products_saved', [])
            if saved_products:
                print(f"\n📦 СОХРАНЕННЫЕ ТОВАРЫ (первые 3):")
                for product in saved_products[:3]:
                    print(f"   • Код: {product.get('code')} | {product.get('model_name')[:50]}... | Действие: {product.get('action')}")
        
        else:
            print(f"   ❌ Ошибка: {result.get('message')}")
            if result.get('errors'):
                print("   📋 Детали ошибок:")
                for error in result.get('errors')[:3]:
                    print(f"      - {error}")
        
        # Проверяем базу данных
        print(f"\n🗄️  ПРОВЕРКА БАЗЫ ДАННЫХ:")
        from offers_check_marketplaces.server import database_manager
        
        if database_manager:
            # Получаем статистику
            stats = await database_manager.get_statistics()
            print(f"   📊 Всего товаров в БД: {stats.total_products}")
            print(f"   📈 Товаров с ценами: {stats.products_with_prices}")
            print(f"   📂 Категорий: {len(stats.category_breakdown)}")
            
            # Показываем категории
            if stats.category_breakdown:
                print("   📋 Разбивка по категориям:")
                for category, count in list(stats.category_breakdown.items())[:3]:
                    print(f"      - {category}: {count} товаров")
        
        print("\n" + "=" * 60)
        print("ТЕСТ ЗАВЕРШЕН УСПЕШНО! ✅")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТА: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Главная функция теста."""
    print("🚀 Запуск теста новой функции parse_excel_and_save_to_database")
    
    # Устанавливаем переменную окружения для лицензии (для теста)
    os.environ['OFFERS_CHECK_LICENSE_KEY'] = 'test-license-key-for-development'
    
    result = await test_parse_excel_and_save()
    
    if result and result.get('status') == 'success':
        print("\n🎉 Новая функция работает корректно!")
        print("   Теперь можно парсить Excel файлы и автоматически сохранять товары в базу данных.")
    else:
        print("\n⚠️  Обнаружены проблемы с новой функцией.")
        print("   Проверьте логи выше для диагностики.")

if __name__ == "__main__":
    asyncio.run(main())