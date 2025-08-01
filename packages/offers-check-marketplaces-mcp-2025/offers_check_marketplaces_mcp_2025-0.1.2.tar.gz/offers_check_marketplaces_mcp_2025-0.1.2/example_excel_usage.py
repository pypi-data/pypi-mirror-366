#!/usr/bin/env python3
"""
Пример использования новых Excel MCP Tools.
Демонстрирует основные возможности работы с Excel файлами.
"""

# Примеры вызовов новых MCP Tools для работы с Excel

# 1. Парсинг Excel файла
parse_excel_example = {
    "tool": "parse_excel_file",
    "parameters": {
        "file_path": "data/Таблица на вход.xlsx",
        "sheet_name": "Лист1",
        "header_row": 0,
        "max_rows": 100
    },
    "description": "Парсит Excel файл и возвращает структурированные данные"
}

# 2. Получение информации о структуре Excel файла
get_info_example = {
    "tool": "get_excel_info", 
    "parameters": {
        "file_path": "data/Таблица на вход.xlsx"
    },
    "description": "Получает информацию о листах, заголовках и размерах без полного чтения"
}

# 3. Экспорт данных в Excel с форматированием
export_example = {
    "tool": "export_to_excel",
    "parameters": {
        "data": [
            {
                "Код\nмодели": 195385.0,
                "model_name": "Полотно техническое БЯЗЬ ОТБЕЛЕННАЯ ГОСТ",
                "Категория": "Хозтовары и посуда",
                "Цена позиции\nМП c НДС": 1250.0,
                "Цена позиции\nB2C c НДС": 1320.0
            }
        ],
        "file_path": "data/Таблица на выход (отработанная).xlsx",
        "sheet_name": "Результаты",
        "include_index": False,
        "auto_adjust_columns": True,
        "apply_formatting": True
    },
    "description": "Экспортирует данные в Excel с автоматическим форматированием"
}

# 4. Фильтрация данных по критериям
filter_example = {
    "tool": "filter_excel_data",
    "parameters": {
        "data": [
            {"Категория": "Хозтовары и посуда", "Цена": 1250.0},
            {"Категория": "Канцелярские товары", "Цена": 450.0},
            {"Категория": "Хозтовары и посуда", "Цена": 890.0}
        ],
        "filters": {
            "Категория": "Хозтовары и посуда",
            "Цена": {
                "greater_than": 500,
                "less_than": 2000
            }
        }
    },
    "description": "Фильтрует данные по заданным критериям"
}

# 5. Трансформация данных
transform_example = {
    "tool": "transform_excel_data",
    "parameters": {
        "data": [
            {"model_name": "полотно техническое", "price": 1000.0},
            {"model_name": "бумага офисная", "price": 500.0}
        ],
        "transformations": {
            "model_name": {
                "to_upper": True,
                "replace": {
                    "ПОЛОТНО": "ТКАНЬ"
                }
            },
            "price": {
                "multiply": 1.2  # Увеличиваем цену на 20%
            }
        }
    },
    "description": "Трансформирует данные согласно заданным правилам"
}

# Рабочий процесс с Excel
workflow_example = """
ТИПИЧНЫЙ РАБОЧИЙ ПРОЦЕСС С EXCEL:

1. Анализ структуры файла:
   get_excel_info("data/input.xlsx")
   
2. Парсинг данных:
   parse_excel_file("data/input.xlsx", sheet_name="Данные", header_row=0)
   
3. Фильтрация данных:
   filter_excel_data(parsed_data, {"Категория": "Хозтовары"})
   
4. Трансформация данных:
   transform_excel_data(filtered_data, {"price": {"multiply": 1.1}})
   
5. Экспорт результатов:
   export_to_excel(transformed_data, "data/output.xlsx", apply_formatting=True)
"""

# Примеры сложных фильтров
complex_filters_examples = {
    "text_filters": {
        "model_name": {
            "contains": "ГОСТ",
            "not_contains": "устаревший"
        }
    },
    "numeric_filters": {
        "price": {
            "greater_equal": 100,
            "less_equal": 5000
        }
    },
    "combined_filters": {
        "Категория": "Канцелярские товары",
        "Цена позиции\nМП c НДС": {
            "greater_than": 200
        },
        "model_name": {
            "contains": "А4"
        }
    }
}

# Примеры трансформаций
transformation_examples = {
    "string_transformations": {
        "model_name": {
            "to_upper": True,
            "strip": True,
            "replace": {
                "старое_значение": "новое_значение"
            }
        }
    },
    "numeric_transformations": {
        "price": {
            "multiply": 1.2,
            "convert_to": "float"
        }
    },
    "type_conversions": {
        "code": {
            "convert_to": "int"
        },
        "description": {
            "convert_to": "str"
        }
    }
}

if __name__ == "__main__":
    print("=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ EXCEL MCP TOOLS")
    print("=" * 60)
    
    examples = [
        parse_excel_example,
        get_info_example, 
        export_example,
        filter_example,
        transform_example
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['tool'].upper()}")
        print(f"   Описание: {example['description']}")
        print(f"   Параметры: {list(example['parameters'].keys())}")
        
        # Показываем ключевые параметры
        params = example['parameters']
        if 'file_path' in params:
            print(f"   Файл: {params['file_path']}")
        if 'data' in params and isinstance(params['data'], list):
            print(f"   Данных: {len(params['data'])} записей")
        if 'filters' in params:
            print(f"   Фильтры: {list(params['filters'].keys())}")
        if 'transformations' in params:
            print(f"   Трансформации: {list(params['transformations'].keys())}")
    
    print(f"\n{workflow_example}")
    
    print("\n" + "=" * 60)
    print("НОВЫЕ EXCEL TOOLS УСПЕШНО ДОБАВЛЕНЫ! ✅")
    print("=" * 60)
    
    print("\nДоступные MCP Tools для работы с Excel:")
    print("• parse_excel_file - парсинг Excel файлов")
    print("• get_excel_info - информация о структуре файла")
    print("• export_to_excel - экспорт с форматированием")
    print("• filter_excel_data - фильтрация по критериям")
    print("• transform_excel_data - трансформация данных")