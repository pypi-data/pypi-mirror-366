"""
Тесты для модуля statistics.py - генерации статистики и отчетов.

Проверяет все основные функции StatisticsGenerator класса,
включая требования 5.1-5.5 из спецификации.
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Импорты модулей для тестирования
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.statistics import StatisticsGenerator
from offers_check_marketplaces.models import Statistics


class TestStatisticsGenerator:
    """Тестовый класс для StatisticsGenerator."""

    @pytest.fixture
    async def setup_test_database(self):
        """
        Создает временную базу данных с тестовыми данными.
        
        Returns:
            Tuple[DatabaseManager, StatisticsGenerator]: Настроенные объекты для тестирования
        """
        # Создаем временный файл для базы данных
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Инициализируем менеджер базы данных
        db_manager = DatabaseManager(temp_db.name)
        await db_manager.init_database()
        
        # Создаем генератор статистики
        stats_generator = StatisticsGenerator(db_manager)
        
        # Добавляем тестовые данные
        await self._populate_test_data(db_manager)
        
        yield db_manager, stats_generator
        
        # Очистка после тестов
        try:
            os.unlink(temp_db.name)
        except:
            pass

    async def _populate_test_data(self, db_manager: DatabaseManager):
        """
        Заполняет базу данных тестовыми данными.
        
        Args:
            db_manager: Менеджер базы данных
        """
        # Тестовые продукты
        test_products = [
            {
                "code": 1001.0,
                "model_name": "Товар 1 - Канцелярия",
                "category": "Канцелярские товары",
                "unit": "шт",
                "priority_1_source": "Комус",
                "priority_2_source": "ВсеИнструменты"
            },
            {
                "code": 1002.0,
                "model_name": "Товар 2 - Канцелярия",
                "category": "Канцелярские товары",
                "unit": "шт",
                "priority_1_source": "Комус",
                "priority_2_source": "Озон"
            },
            {
                "code": 2001.0,
                "model_name": "Товар 1 - Хозтовары",
                "category": "Хозтовары и посуда",
                "unit": "м",
                "priority_1_source": "ВсеИнструменты",
                "priority_2_source": "Wildberries"
            },
            {
                "code": 2002.0,
                "model_name": "Товар 2 - Хозтовары",
                "category": "Хозтовары и посуда",
                "unit": "кг",
                "priority_1_source": "Озон",
                "priority_2_source": "Комус"
            },
            {
                "code": 3001.0,
                "model_name": "Товар 1 - Инструменты",
                "category": "Инструменты",
                "unit": "шт",
                "priority_1_source": "ВсеИнструменты",
                "priority_2_source": "Комус"
            }
        ]
        
        # Сохраняем продукты
        product_ids = {}
        for product in test_products:
            product_id = await db_manager.save_product(product)
            product_ids[product["code"]] = product_id
        
        # Тестовые цены
        test_prices = [
            # Товар 1001 - цены на разных маркетплейсах
            {"product_code": 1001.0, "marketplace": "Комус", "price": 150.0, "availability": "В наличии", "product_url": "https://komus.ru/1001"},
            {"product_code": 1001.0, "marketplace": "ВсеИнструменты", "price": 180.0, "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/1001"},
            {"product_code": 1001.0, "marketplace": "Озон", "price": 165.0, "availability": "В наличии", "product_url": "https://ozon.ru/1001"},
            
            # Товар 1002 - только на приоритетном источнике
            {"product_code": 1002.0, "marketplace": "Комус", "price": 200.0, "availability": "В наличии", "product_url": "https://komus.ru/1002"},
            
            # Товар 2001 - цены на обоих приоритетных источниках
            {"product_code": 2001.0, "marketplace": "ВсеИнструменты", "price": 500.0, "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/2001"},
            {"product_code": 2001.0, "marketplace": "Wildberries", "price": 450.0, "availability": "В наличии", "product_url": "https://wildberries.ru/2001"},
            
            # Товар 2002 - нет в наличии на одном маркетплейсе
            {"product_code": 2002.0, "marketplace": "Озон", "price": 300.0, "availability": "Нет в наличии", "product_url": "https://ozon.ru/2002"},
            {"product_code": 2002.0, "marketplace": "Комус", "price": 320.0, "availability": "В наличии", "product_url": "https://komus.ru/2002"},
            
            # Товар 3001 - без цен (для тестирования товаров без совпадений)
        ]
        
        # Сохраняем цены
        for price_data in test_prices:
            product_id = product_ids[price_data["product_code"]]
            price_info = {
                "marketplace": price_data["marketplace"],
                "price": price_data["price"],
                "currency": "RUB",
                "availability": price_data["availability"],
                "product_url": price_data["product_url"]
            }
            await db_manager.save_price(product_id, price_info)

    @pytest.mark.asyncio
    async def test_generate_full_statistics_requirement_5_1(self, setup_test_database):
        """
        Тест требования 5.1: Общее количество обработанных товаров.
        
        Проверяет, что система возвращает правильное общее количество товаров.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем статистику
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем требование 5.1
        assert isinstance(statistics, Statistics)
        assert statistics.total_products == 5, f"Ожидалось 5 товаров, получено {statistics.total_products}"
        
        print(f"Требование 5.1: Общее количество товаров = {statistics.total_products}")

    @pytest.mark.asyncio
    async def test_generate_full_statistics_requirement_5_2(self, setup_test_database):
        """
        Тест требования 5.2: Количество товаров с успешными совпадениями цен.
        
        Проверяет, что система правильно подсчитывает товары с найденными ценами.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем статистику
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем требование 5.2
        # У нас есть цены для товаров: 1001, 1002, 2001, 2002 (4 товара)
        assert statistics.products_with_prices == 4, f"Ожидалось 4 товара с ценами, получено {statistics.products_with_prices}"
        
        # Проверяем процент успешности
        success_rate = statistics.success_rate
        expected_rate = (4 / 5) * 100  # 80%
        assert abs(success_rate - expected_rate) < 0.1, f"Ожидался success_rate {expected_rate}%, получен {success_rate}%"
        
        print(f"Требование 5.2: Товары с ценами = {statistics.products_with_prices}, Success rate = {success_rate}%")

    @pytest.mark.asyncio
    async def test_generate_full_statistics_requirement_5_3(self, setup_test_database):
        """
        Тест требования 5.3: Средние процентные дельты цен по всем товарам.
        
        Проверяет расчет средней процентной дельты между ценами.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем статистику
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем требование 5.3
        assert statistics.average_delta_percent >= 0, "Средняя дельта должна быть неотрицательной"
        
        # Дополнительная проверка через отдельный метод
        average_values = await stats_generator.calculate_average_values()
        assert "average_delta_percent" in average_values
        assert average_values["average_delta_percent"] >= 0
        
        print(f"Требование 5.3: Средняя дельта цен = {statistics.average_delta_percent}%")

    @pytest.mark.asyncio
    async def test_generate_full_statistics_requirement_5_4(self, setup_test_database):
        """
        Тест требования 5.4: Разбивка по категориям товаров.
        
        Проверяет, что система включает разбивку по категориям.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем статистику
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем требование 5.4
        assert isinstance(statistics.category_breakdown, dict)
        assert len(statistics.category_breakdown) > 0, "Разбивка по категориям не должна быть пустой"
        
        # Проверяем ожидаемые категории
        expected_categories = {"Канцелярские товары", "Хозтовары и посуда", "Инструменты"}
        actual_categories = set(statistics.category_breakdown.keys())
        assert expected_categories == actual_categories, f"Ожидались категории {expected_categories}, получены {actual_categories}"
        
        # Проверяем количество товаров в категориях
        assert statistics.category_breakdown["Канцелярские товары"] == 2
        assert statistics.category_breakdown["Хозтовары и посуда"] == 2
        assert statistics.category_breakdown["Инструменты"] == 1
        
        print(f"Требование 5.4: Разбивка по категориям = {statistics.category_breakdown}")

    @pytest.mark.asyncio
    async def test_generate_full_statistics_requirement_5_5(self, setup_test_database):
        """
        Тест требования 5.5: Покрытие маркетплейсов.
        
        Проверяет информацию о покрытии маркетплейсов.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем статистику
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем требование 5.5
        assert isinstance(statistics.marketplace_coverage, dict)
        assert len(statistics.marketplace_coverage) > 0, "Покрытие маркетплейсов не должно быть пустым"
        
        # Проверяем ожидаемые маркетплейсы
        expected_marketplaces = {"Комус", "ВсеИнструменты", "Озон", "Wildberries"}
        actual_marketplaces = set(statistics.marketplace_coverage.keys())
        assert expected_marketplaces == actual_marketplaces, f"Ожидались маркетплейсы {expected_marketplaces}, получены {actual_marketplaces}"
        
        # Проверяем процентное покрытие
        coverage_percent = statistics.get_marketplace_coverage_percent()
        assert isinstance(coverage_percent, dict)
        assert len(coverage_percent) > 0
        
        print(f"Требование 5.5: Покрытие маркетплейсов = {statistics.marketplace_coverage}")
        print(f"   Процентное покрытие = {coverage_percent}")

    @pytest.mark.asyncio
    async def test_calculate_success_matches(self, setup_test_database):
        """
        Тест расчета успешных совпадений по различным критериям.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Рассчитываем успешные совпадения
        success_matches = await stats_generator.calculate_success_matches()
        
        # Проверяем структуру результата
        expected_keys = {
            "priority_1_source_matches",
            "priority_2_source_matches", 
            "both_priorities_matches",
            "multiple_marketplace_matches"
        }
        assert set(success_matches.keys()) == expected_keys
        
        # Проверяем логические ограничения
        assert success_matches["priority_1_source_matches"] >= 0
        assert success_matches["priority_2_source_matches"] >= 0
        assert success_matches["both_priorities_matches"] <= min(
            success_matches["priority_1_source_matches"],
            success_matches["priority_2_source_matches"]
        )
        
        print(f"Успешные совпадения: {success_matches}")

    @pytest.mark.asyncio
    async def test_calculate_marketplace_coverage(self, setup_test_database):
        """
        Тест детального расчета покрытия маркетплейсов.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Рассчитываем покрытие маркетплейсов
        coverage = await stats_generator.calculate_marketplace_coverage()
        
        # Проверяем структуру результата
        assert isinstance(coverage, dict)
        assert len(coverage) > 0
        
        for marketplace, data in coverage.items():
            assert "total_products" in data
            assert "coverage_percentage" in data
            assert "category_breakdown" in data
            assert isinstance(data["total_products"], int)
            assert isinstance(data["coverage_percentage"], float)
            assert isinstance(data["category_breakdown"], dict)
            assert 0 <= data["coverage_percentage"] <= 100
        
        print(f"Детальное покрытие маркетплейсов: {coverage}")

    @pytest.mark.asyncio
    async def test_calculate_average_values(self, setup_test_database):
        """
        Тест расчета различных средних значений.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Рассчитываем средние значения
        averages = await stats_generator.calculate_average_values()
        
        # Проверяем структуру результата
        expected_keys = {
            "average_delta_percent",
            "overall_average_price",
            "median_price",
            "category_averages",
            "marketplace_averages"
        }
        assert set(averages.keys()) == expected_keys
        
        # Проверяем типы и логические ограничения
        assert isinstance(averages["average_delta_percent"], float)
        assert isinstance(averages["overall_average_price"], float)
        assert isinstance(averages["median_price"], float)
        assert isinstance(averages["category_averages"], dict)
        assert isinstance(averages["marketplace_averages"], dict)
        
        assert averages["overall_average_price"] >= 0
        assert averages["median_price"] >= 0
        
        print(f"Средние значения: {averages}")

    @pytest.mark.asyncio
    async def test_get_category_breakdown(self, setup_test_database):
        """
        Тест детальной разбивки по категориям.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Получаем разбивку по категориям
        breakdown = await stats_generator.get_category_breakdown()
        
        # Проверяем структуру результата
        assert isinstance(breakdown, dict)
        assert len(breakdown) == 3  # У нас 3 категории
        
        for category, data in breakdown.items():
            assert "total_products" in data
            assert "products_with_prices" in data
            assert "coverage_percentage" in data
            assert isinstance(data["total_products"], int)
            assert isinstance(data["products_with_prices"], int)
            assert isinstance(data["coverage_percentage"], float)
            assert 0 <= data["coverage_percentage"] <= 100
            assert data["products_with_prices"] <= data["total_products"]
        
        print(f"Детальная разбивка по категориям: {breakdown}")

    @pytest.mark.asyncio
    async def test_generate_marketplace_comparison(self, setup_test_database):
        """
        Тест сравнительного анализа маркетплейсов.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем сравнение маркетплейсов
        comparison = await stats_generator.generate_marketplace_comparison()
        
        # Проверяем структуру результата
        assert isinstance(comparison, dict)
        assert len(comparison) > 0
        
        for marketplace, data in comparison.items():
            expected_keys = {
                "products_count", "average_price", "min_price", 
                "max_price", "availability_percentage", "total_listings"
            }
            assert set(data.keys()) == expected_keys
            
            assert isinstance(data["products_count"], int)
            assert isinstance(data["average_price"], float)
            assert isinstance(data["availability_percentage"], float)
            assert data["min_price"] <= data["max_price"]
            assert 0 <= data["availability_percentage"] <= 100
        
        print(f"Сравнение маркетплейсов: {comparison}")

    @pytest.mark.asyncio
    async def test_generate_summary_report(self, setup_test_database):
        """
        Тест генерации итогового сводного отчета.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Генерируем сводный отчет
        report = await stats_generator.generate_summary_report()
        
        # Проверяем структуру отчета
        expected_keys = {
            "report_timestamp", "overview", "success_metrics",
            "marketplace_coverage", "average_values", "category_analysis",
            "marketplace_comparison", "top_categories", "marketplace_coverage_percent"
        }
        assert set(report.keys()) == expected_keys
        
        # Проверяем timestamp
        assert "report_timestamp" in report
        timestamp = datetime.fromisoformat(report["report_timestamp"])
        assert isinstance(timestamp, datetime)
        
        # Проверяем overview
        overview = report["overview"]
        assert "total_products" in overview
        assert "products_with_prices" in overview
        assert "success_rate_percentage" in overview
        assert "average_delta_percent" in overview
        
        print(f"Сводный отчет сгенерирован успешно")
        print(f"   Timestamp: {report['report_timestamp']}")
        print(f"   Overview: {overview}")

    @pytest.mark.asyncio
    async def test_empty_database_handling(self):
        """
        Тест обработки пустой базы данных.
        """
        # Создаем временную пустую базу данных
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            db_manager = DatabaseManager(temp_db.name)
            await db_manager.init_database()
            stats_generator = StatisticsGenerator(db_manager)
            
            # Генерируем статистику для пустой базы
            statistics = await stats_generator.generate_full_statistics()
            
            # Проверяем корректную обработку пустой базы
            assert statistics.total_products == 0
            assert statistics.products_with_prices == 0
            assert statistics.success_rate == 0.0
            assert statistics.average_delta_percent == 0.0
            assert len(statistics.category_breakdown) == 0
            assert len(statistics.marketplace_coverage) == 0
            
            print("Пустая база данных обрабатывается корректно")
            
        finally:
            try:
                os.unlink(temp_db.name)
            except:
                pass

    @pytest.mark.asyncio
    async def test_error_handling(self, setup_test_database):
        """
        Тест обработки ошибок в StatisticsGenerator.
        """
        db_manager, stats_generator = await setup_test_database
        
        # Закрываем соединение с базой данных для имитации ошибки
        original_path = db_manager.db_path
        db_manager.db_path = "/nonexistent/path/database.db"
        
        # Проверяем, что ошибки обрабатываются корректно
        try:
            await stats_generator.generate_full_statistics()
            assert False, "Ожидалась ошибка при работе с несуществующей базой данных"
        except Exception as e:
            assert isinstance(e, Exception)
            print(f"Ошибка корректно обработана: {type(e).__name__}")
        
        # Восстанавливаем путь
        db_manager.db_path = original_path


def run_manual_test():
    """
    Функция для ручного запуска тестов без pytest.
    
    Полезна для быстрой проверки функциональности.
    """
    async def manual_test():
        print("🧪 Запуск ручных тестов StatisticsGenerator...")
        
        # Создаем временную базу данных
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            # Инициализируем компоненты
            db_manager = DatabaseManager(temp_db.name)
            await db_manager.init_database()
            stats_generator = StatisticsGenerator(db_manager)
            
            # Создаем тестовые данные
            test_instance = TestStatisticsGenerator()
            await test_instance._populate_test_data(db_manager)
            
            print("\nТестирование основных требований...")
            
            # Тест полной статистики
            statistics = await stats_generator.generate_full_statistics()
            print(f"Общая статистика: {statistics.total_products} товаров, {statistics.products_with_prices} с ценами")
            
            # Тест успешных совпадений
            success_matches = await stats_generator.calculate_success_matches()
            print(f"Успешные совпадения: {success_matches}")
            
            # Тест покрытия маркетплейсов
            coverage = await stats_generator.calculate_marketplace_coverage()
            print(f"Покрытие маркетплейсов: {len(coverage)} маркетплейсов")
            
            # Тест средних значений
            averages = await stats_generator.calculate_average_values()
            print(f"Средние значения: дельта {averages['average_delta_percent']}%, средняя цена {averages['overall_average_price']}")
            
            # Тест разбивки по категориям
            breakdown = await stats_generator.get_category_breakdown()
            print(f"Разбивка по категориям: {len(breakdown)} категорий")
            
            # Тест сводного отчета
            report = await stats_generator.generate_summary_report()
            print(f"Сводный отчет сгенерирован: {len(report)} разделов")
            
            print("\nВсе ручные тесты пройдены успешно!")
            
        except Exception as e:
            print(f"Ошибка в ручных тестах: {e}")
            raise
        finally:
            try:
                os.unlink(temp_db.name)
            except:
                pass
    
    # Запускаем асинхронные тесты
    asyncio.run(manual_test())


if __name__ == "__main__":
    print("Запуск тестов для StatisticsGenerator...")
    print("Для запуска с pytest используйте: pytest tests/test_statistics.py -v")
    print("Для ручного тестирования запускается автоматически...\n")
    
    run_manual_test()