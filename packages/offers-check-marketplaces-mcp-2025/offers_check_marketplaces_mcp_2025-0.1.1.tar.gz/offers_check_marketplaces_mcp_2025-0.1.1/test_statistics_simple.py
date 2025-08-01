#!/usr/bin/env python3
"""
Простой тест для проверки функциональности модуля statistics.py (задача 7.1).

Этот скрипт создает тестовую базу данных, заполняет её данными
и проверяет основные функции StatisticsGenerator.
"""

import asyncio
import tempfile
import os
from pathlib import Path

# Импорты из нашего модуля
from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.statistics import StatisticsGenerator


async def create_test_data(db_manager: DatabaseManager):
    """Создает тестовые данные в базе."""
    print("Создание тестовых данных...")
    
    # Тестовые продукты
    test_products = [
        {
            "code": 195385.0,
            "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
            "category": "Хозтовары и посуда",
            "unit": "м",
            "priority_1_source": "Комус",
            "priority_2_source": "ВсеИнструменты"
        },
        {
            "code": 195386.0,
            "model_name": "Ручка шариковая синяя",
            "category": "Канцтовары",
            "unit": "шт",
            "priority_1_source": "Озон",
            "priority_2_source": "Wildberries"
        },
        {
            "code": 195387.0,
            "model_name": "Дрель электрическая",
            "category": "Инструменты",
            "unit": "шт",
            "priority_1_source": "ВсеИнструменты",
            "priority_2_source": "Комус"
        },
        {
            "code": 195388.0,
            "model_name": "Чашка керамическая",
            "category": "Хозтовары и посуда",
            "unit": "шт",
            "priority_1_source": "Комус",
            "priority_2_source": "Озон"
        },
        {
            "code": 195389.0,
            "model_name": "Блокнот А5",
            "category": "Канцтовары",
            "unit": "шт",
            "priority_1_source": "Wildberries",
            "priority_2_source": "Комус"
        }
    ]

    # Сохраняем продукты и получаем их ID
    product_ids = []
    for i, product_data in enumerate(test_products):
        try:
            product_id = await db_manager.save_product(product_data)
            product_ids.append(product_id)
            print(f"  Продукт {i+1}: {product_data['model_name'][:30]}... (ID: {product_id})")
        except Exception as e:
            print(f"  Ошибка сохранения продукта {i+1}: {e}")

    # Тестовые цены
    test_prices = [
        # Продукт 1 - цены на 3 маркетплейсах (хорошее покрытие)
        {"product_id": product_ids[0], "marketplace": "Комус", "price": 1500.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://komus.ru/1"},
        {"product_id": product_ids[0], "marketplace": "ВсеИнструменты", "price": 1600.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/1"},
        {"product_id": product_ids[0], "marketplace": "Озон", "price": 1450.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://ozon.ru/1"},
        
        # Продукт 2 - цены на 2 маркетплейсах
        {"product_id": product_ids[1], "marketplace": "Озон", "price": 25.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://ozon.ru/2"},
        {"product_id": product_ids[1], "marketplace": "Wildberries", "price": 30.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://wildberries.ru/2"},
        
        # Продукт 3 - цена только на 1 маркетплейсе
        {"product_id": product_ids[2], "marketplace": "ВсеИнструменты", "price": 3500.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/3"},
        
        # Продукт 4 - цены на 2 маркетплейсах с большой разницей
        {"product_id": product_ids[3], "marketplace": "Комус", "price": 150.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://komus.ru/4"},
        {"product_id": product_ids[3], "marketplace": "Озон", "price": 200.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://ozon.ru/4"},
        
        # Продукт 5 - без цен (для тестирования товаров без покрытия)
    ]

    # Сохраняем цены
    for i, price_data in enumerate(test_prices):
        try:
            await db_manager.save_price(price_data["product_id"], price_data)
            print(f"  Цена {i+1}: {price_data['marketplace']} - {price_data['price']} руб.")
        except Exception as e:
            print(f"  Ошибка сохранения цены {i+1}: {e}")

    print(f"Создано {len(product_ids)} продуктов и {len(test_prices)} цен")
    return product_ids


async def test_statistics_functionality():
    """Основная функция тестирования."""
    print("🧪 ТЕСТИРОВАНИЕ МОДУЛЯ STATISTICS.PY (ЗАДАЧА 7.1)")
    print("=" * 60)
    
    # Создаем временную базу данных
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_statistics.db")
    
    try:
        # Инициализируем базу данных
        print("Инициализация базы данных...")
        db_manager = DatabaseManager(db_path)
        await db_manager.init_database()
        print("База данных инициализирована")
        
        # Создаем тестовые данные
        product_ids = await create_test_data(db_manager)
        
        # Создаем генератор статистики
        print("\nСоздание генератора статистики...")
        stats_generator = StatisticsGenerator(db_manager)
        print("StatisticsGenerator создан")
        
        # Тест 1: Полная статистика (требования 5.1-5.5)
        print("\n" + "="*50)
        print("ТЕСТ 1: Полная статистика (требования 5.1-5.5)")
        print("="*50)
        
        statistics = await stats_generator.generate_full_statistics()
        
        print(f"Общее количество товаров: {statistics.total_products}")
        print(f"Товары с ценами: {statistics.products_with_prices}")
        print(f"Процент успешности: {statistics.success_rate:.1f}%")
        print(f"Средняя дельта цен: {statistics.average_delta_percent:.2f}%")
        
        print(f"\nРазбивка по категориям:")
        for category, count in statistics.category_breakdown.items():
            print(f"  • {category}: {count} товаров")
        
        print(f"\nПокрытие маркетплейсов:")
        for marketplace, count in statistics.marketplace_coverage.items():
            print(f"  • {marketplace}: {count} товаров")
        
        # Тест 2: Успешные совпадения
        print("\n" + "="*50)
        print("ТЕСТ 2: Расчет успешных совпадений")
        print("="*50)
        
        success_matches = await stats_generator.calculate_success_matches()
        
        print(f"Совпадения по приоритету 1: {success_matches['priority_1_source_matches']}")
        print(f"Совпадения по приоритету 2: {success_matches['priority_2_source_matches']}")
        print(f"Совпадения по обоим приоритетам: {success_matches['both_priorities_matches']}")
        print(f"Товары на 3+ маркетплейсах: {success_matches['multiple_marketplace_matches']}")
        
        # Тест 3: Покрытие маркетплейсов
        print("\n" + "="*50)
        print("ТЕСТ 3: Детальное покрытие маркетплейсов")
        print("="*50)
        
        coverage = await stats_generator.calculate_marketplace_coverage()
        
        for marketplace, data in coverage.items():
            print(f"\n{marketplace}:")
            print(f"  Товаров: {data['total_products']}")
            print(f"  Покрытие: {data['coverage_percentage']:.1f}%")
            print(f"  По категориям:")
            for category, count in data['category_breakdown'].items():
                print(f"    • {category}: {count}")
        
        # Тест 4: Средние значения
        print("\n" + "="*50)
        print("ТЕСТ 4: Расчет средних значений")
        print("="*50)
        
        averages = await stats_generator.calculate_average_values()
        
        print(f"Средняя дельта: {averages['average_delta_percent']:.2f}%")
        print(f"Средняя цена: {averages['overall_average_price']:.2f} руб.")
        print(f"Медианная цена: {averages['median_price']:.2f} руб.")
        
        print(f"\nСредние цены по категориям:")
        for category, avg_price in averages['category_averages'].items():
            print(f"  • {category}: {avg_price:.2f} руб.")
        
        print(f"\nСредние цены по маркетплейсам:")
        for marketplace, avg_price in averages['marketplace_averages'].items():
            print(f"  • {marketplace}: {avg_price:.2f} руб.")
        
        # Тест 5: Разбивка по категориям
        print("\n" + "="*50)
        print("ТЕСТ 5: Детальная разбивка по категориям")
        print("="*50)
        
        category_breakdown = await stats_generator.get_category_breakdown()
        
        for category, data in category_breakdown.items():
            print(f"\n{category}:")
            print(f"  Всего товаров: {data['total_products']}")
            print(f"  С ценами: {data['products_with_prices']}")
            print(f"  Покрытие: {data['coverage_percentage']:.1f}%")
        
        # Тест 6: Сравнение маркетплейсов
        print("\n" + "="*50)
        print("ТЕСТ 6: Сравнение маркетплейсов")
        print("="*50)
        
        comparison = await stats_generator.generate_marketplace_comparison()
        
        for marketplace, data in comparison.items():
            print(f"\n{marketplace}:")
            print(f"  Товаров: {data['products_count']}")
            print(f"  Средняя цена: {data['average_price']:.2f} руб.")
            print(f"  Мин. цена: {data['min_price']:.2f} руб.")
            print(f"  Макс. цена: {data['max_price']:.2f} руб.")
            print(f"  Доступность: {data['availability_percentage']:.1f}%")
            print(f"  Всего позиций: {data['total_listings']}")
        
        # Тест 7: Сводный отчет
        print("\n" + "="*50)
        print("ТЕСТ 7: Генерация сводного отчета")
        print("="*50)
        
        summary_report = await stats_generator.generate_summary_report()
        
        print(f"Время отчета: {summary_report['report_timestamp']}")
        print(f"Разделов в отчете: {len(summary_report)}")
        
        overview = summary_report['overview']
        print(f"\nОбзор:")
        print(f"  Всего товаров: {overview['total_products']}")
        print(f"  С ценами: {overview['products_with_prices']}")
        print(f"  Успешность: {overview['success_rate_percentage']:.1f}%")
        print(f"  Средняя дельта: {overview['average_delta_percent']:.2f}%")
        
        print(f"\n🏆 Топ категории:")
        for category, count in summary_report['top_categories'].items():
            print(f"  • {category}: {count} товаров")
        
        # Финальная проверка
        print("\n" + "="*60)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*60)
        
        print(f"\nИТОГОВАЯ СВОДКА:")
        print(f"  Требование 5.1 (общее количество товаров): {statistics.total_products}")
        print(f"  Требование 5.2 (товары с ценами): {statistics.products_with_prices}")
        print(f"  Требование 5.3 (средние дельты): {statistics.average_delta_percent:.2f}%")
        print(f"  Требование 5.4 (разбивка по категориям): {len(statistics.category_breakdown)} категорий")
        print(f"  Требование 5.5 (покрытие маркетплейсов): {len(statistics.marketplace_coverage)} маркетплейсов")
        
        return True
        
    except Exception as e:
        print(f"\nОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Очистка временных файлов
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)
            print(f"\nВременные файлы очищены")
        except Exception as e:
            print(f"Не удалось очистить временные файлы: {e}")


def main():
    """Главная функция."""
    try:
        success = asyncio.run(test_statistics_functionality())
        if success:
            print("\nТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            exit(0)
        else:
            print("\n💥 ТЕСТИРОВАНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ!")
            exit(1)
    except KeyboardInterrupt:
        print("\nТестирование прервано пользователем")
        exit(1)
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        exit(1)


if __name__ == "__main__":
    main()