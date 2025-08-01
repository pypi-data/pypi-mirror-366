#!/usr/bin/env python3
"""
Тестирование новых Excel Tools для MCP сервера offers-check-marketplaces.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.excel_tools import ExcelTools


async def test_excel_tools():
    """Тестирование Excel инструментов."""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ EXCEL TOOLS")
    print("=" * 60)
    
    # Создаем экземпляр Excel Tools
    excel_tools = ExcelTools()
    
    # Создаем тестовые данные
    test_data = [
        {
            "Код\nмодели": 195385.0,
            "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ, рулон 1,5х50 м",
            "Категория": "Хозтовары и посуда",
            "Единица измерения": "м",
            "Приоритет \n1 Источники": "Комус",
            "Приоритет \n2 Источники": "ВсеИнструменты",
            "Цена позиции\nМП c НДС": 1250.0,
            "Цена позиции\nB2C c НДС": 1320.0,
            "Дельта в процентах": "5.6%",
            "Ссылка на источник": "https://www.komus.ru/product/12345",
            "Цена 2 позиции\nB2C c НДС": 1400.0
        },
        {
            "Код\nмодели": 195386.0,
            "model_name": "Бумага офисная А4 80г/м2, пачка 500 листов",
            "Категория": "Канцелярские товары",
            "Единица измерения": "пачка",
            "Приоритет \n1 Источники": "Комус",
            "Приоритет \n2 Источники": "Озон",
            "Цена позиции\nМП c НДС": 450.0,
            "Цена позиции\nB2C c НДС": 480.0,
            "Дельта в процентах": "6.7%",
            "Ссылка на источник": "https://www.komus.ru/product/67890",
            "Цена 2 позиции\nB2C c НДС": 520.0
        },
        {
            "Код\nмодели": 195387.0,
            "model_name": "Степлер офисный металлический №24/6",
            "Категория": "Канцелярские товары",
            "Единица измерения": "шт",
            "Приоритет \n1 Источники": "ВсеИнструменты",
            "Приоритет \n2 Источники": "Wildberries",
            "Цена позиции\nМП c НДС": 890.0,
            "Цена позиции\nB2C c НДС": 950.0,
            "Дельта в процентах": "6.7%",
            "Ссылка на источник": "https://www.vseinstrumenti.ru/product/11111",
            "Цена 2 позиции\nB2C c НДС": 1020.0
        }
    ]
    
    # Создаем директорию для тестов
    test_dir = Path("data/test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Тест 1: Экспорт данных в Excel
    print("\n1. Тестирование экспорта данных в Excel...")
    test_file = test_dir / "test_export.xlsx"
    
    try:
        result = await excel_tools.export_to_excel(
            data=test_data,
            file_path=str(test_file),
            sheet_name="Тестовые данные",
            include_index=False,
            auto_adjust_columns=True,
            apply_formatting=True
        )
        
        print(f"✅ Экспорт успешен: {result}")
        print(f"   Файл создан: {test_file}")
        print(f"   Экспортировано строк: {result.get('rows_exported', 0)}")
        print(f"   Экспортировано колонок: {result.get('columns_exported', 0)}")
        
    except Exception as e:
        print(f"❌ Ошибка экспорта: {e}")
        return False
    
    # Тест 2: Получение информации о файле
    print("\n2. Тестирование получения информации о Excel файле...")
    
    try:
        info_result = await excel_tools.get_excel_info(str(test_file))
        
        print(f"✅ Информация получена: {info_result['status']}")
        print(f"   Количество листов: {info_result.get('total_sheets', 0)}")
        print(f"   Размер файла: {info_result.get('file_size', 0)} байт")
        
        for sheet in info_result.get('sheets', []):
            print(f"   Лист '{sheet['name']}': {sheet['max_row']} строк, {sheet['max_column']} колонок")
            print(f"     Заголовки: {sheet['headers'][:3]}..." if len(sheet['headers']) > 3 else f"     Заголовки: {sheet['headers']}")
        
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")
        return False
    
    # Тест 3: Парсинг Excel файла
    print("\n3. Тестирование парсинга Excel файла...")
    
    try:
        parse_result = await excel_tools.parse_excel_file(
            file_path=str(test_file),
            sheet_name="Тестовые данные",
            header_row=0,
            max_rows=None
        )
        
        print(f"✅ Парсинг успешен: {parse_result['status']}")
        print(f"   Прочитано строк: {parse_result.get('total_rows', 0)}")
        print(f"   Колонки: {parse_result.get('columns', [])[:3]}..." if len(parse_result.get('columns', [])) > 3 else f"   Колонки: {parse_result.get('columns', [])}")
        
        parsed_data = parse_result.get('data', [])
        if parsed_data:
            print(f"   Первая строка данных: {list(parsed_data[0].keys())[:3]}...")
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return False
    
    # Тест 4: Фильтрация данных
    print("\n4. Тестирование фильтрации данных...")
    
    try:
        filter_criteria = {
            "Категория": "Канцелярские товары",
            "Цена позиции\nМП c НДС": {
                "greater_than": 400,
                "less_than": 1000
            }
        }
        
        filter_result = await excel_tools.filter_excel_data(
            data=test_data,
            filters=filter_criteria
        )
        
        print(f"✅ Фильтрация успешна: {filter_result['status']}")
        print(f"   Исходное количество: {filter_result.get('original_count', 0)}")
        print(f"   После фильтрации: {filter_result.get('filtered_count', 0)}")
        print(f"   Критерии: {filter_criteria}")
        
        filtered_data = filter_result.get('data', [])
        for item in filtered_data:
            print(f"   - {item.get('model_name', 'N/A')}: {item.get('Цена позиции\\nМП c НДС', 'N/A')} руб.")
        
    except Exception as e:
        print(f"❌ Ошибка фильтрации: {e}")
        return False
    
    # Тест 5: Трансформация данных
    print("\n5. Тестирование трансформации данных...")
    
    try:
        transformation_rules = {
            "model_name": {
                "to_upper": True
            },
            "Цена позиции\nМП c НДС": {
                "multiply": 1.2  # Увеличиваем цену на 20%
            },
            "Категория": {
                "replace": {
                    "Канцелярские товары": "КАНЦТОВАРЫ",
                    "Хозтовары и посуда": "ХОЗТОВАРЫ"
                }
            }
        }
        
        transform_result = await excel_tools.transform_excel_data(
            data=test_data.copy(),  # Копируем данные чтобы не изменить оригинал
            transformations=transformation_rules
        )
        
        print(f"✅ Трансформация успешна: {transform_result['status']}")
        print(f"   Обработано строк: {transform_result.get('transformed_count', 0)}")
        print(f"   Правила: {transformation_rules}")
        
        transformed_data = transform_result.get('data', [])
        if transformed_data:
            first_item = transformed_data[0]
            print(f"   Пример трансформации:")
            print(f"     Название: {first_item.get('model_name', 'N/A')}")
            print(f"     Категория: {first_item.get('Категория', 'N/A')}")
            print(f"     Цена (увеличена на 20%): {first_item.get('Цена позиции\\nМП c НДС', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Ошибка трансформации: {e}")
        return False
    
    # Тест 6: Экспорт трансформированных данных
    print("\n6. Тестирование экспорта трансформированных данных...")
    
    try:
        output_file = test_dir / "test_transformed_export.xlsx"
        
        export_result = await excel_tools.export_to_excel(
            data=transformed_data,
            file_path=str(output_file),
            sheet_name="Трансформированные данные",
            include_index=True,
            auto_adjust_columns=True,
            apply_formatting=True
        )
        
        print(f"✅ Экспорт трансформированных данных успешен: {export_result}")
        print(f"   Файл создан: {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка экспорта трансформированных данных: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ EXCEL TOOLS ПРОЙДЕНЫ УСПЕШНО! ✅")
    print("=" * 60)
    
    print(f"\nСозданные файлы:")
    print(f"- {test_file}")
    print(f"- {output_file}")
    
    return True


async def main():
    """Главная функция тестирования."""
    
    try:
        success = await test_excel_tools()
        
        if success:
            print("\n🎉 Все тесты Excel Tools прошли успешно!")
            sys.exit(0)
        else:
            print("\n❌ Некоторые тесты не прошли")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Критическая ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())