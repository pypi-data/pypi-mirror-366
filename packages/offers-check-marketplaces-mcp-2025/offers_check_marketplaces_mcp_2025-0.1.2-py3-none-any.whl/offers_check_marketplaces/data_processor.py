"""
Модуль для обработки Excel данных.
Обеспечивает чтение входных Excel файлов, преобразование в JSON формат
и генерацию выходных Excel файлов с результатами анализа цен.
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .error_handling import (
    handle_errors,
    ErrorCategory,
    ErrorSeverity,
    DataProcessingError,
    ValidationError,
    handle_validation_errors,
    error_handler,
    log_recovery_attempt
)

logger = logging.getLogger(__name__)


class DataProcessor:
    """Класс для обработки Excel данных и преобразования в JSON формат."""
    
    def __init__(self):
        """Инициализация процессора данных."""
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    @handle_errors(
        category=ErrorCategory.PARSING,
        severity=ErrorSeverity.HIGH,
        component="data_processor",
        recovery_action="Возврат пустого списка при ошибке чтения Excel",
        return_on_error=[]
    )
    async def load_excel_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Загружает данные из Excel файла и преобразует в JSON формат.
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            Список словарей с данными продуктов в требуемом JSON формате
            
        Raises:
            FileNotFoundError: Если файл не найден
            PermissionError: Если нет доступа к файлу
            ValueError: Если структура файла некорректна
        """
        try:
            # Проверяем существование файла
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Excel файл не найден: {file_path}")
            
            logger.info(f"Загрузка Excel данных из {file_path}")
            
            # Асинхронно читаем Excel файл
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                self.executor, 
                self._read_excel_sync, 
                file_path
            )
            
            # Преобразуем в требуемый JSON формат
            json_data = self._convert_to_json_format(df)
            
            logger.info(f"Успешно загружено {len(json_data)} записей")
            return json_data
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            raise
        except PermissionError:
            logger.error(f"Нет доступа к файлу: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при чтении Excel файла: {e}")
            raise ValueError(f"Не удалось прочитать Excel файл: {e}")
    
    def _read_excel_sync(self, file_path: str) -> pd.DataFrame:
        """
        Синхронное чтение Excel файла.
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            DataFrame с данными из Excel
        """
        return pd.read_excel(file_path, engine='openpyxl')
    
    def _convert_to_json_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Преобразует DataFrame в требуемый JSON формат.
        
        Args:
            df: DataFrame с данными из Excel
            
        Returns:
            Список словарей в требуемом JSON формате
        """
        json_data = []
        
        for _, row in df.iterrows():
            # Создаем запись в точном соответствии с требуемым форматом
            record = {
                "Код\nмодели": self._safe_convert_to_float(row.get("Код\nмодели", "")),
                "model_name": self._safe_convert_to_string(row.get("model_name", "")),
                "Категория": self._safe_convert_to_string(row.get("Категория", "")),
                "Единица измерения": self._safe_convert_to_string(row.get("Единица измерения", "")),
                "Приоритет \n1 Источники": self._safe_convert_to_string(row.get("Приоритет \n1 Источники", "")),
                "Приоритет \n2 Источники": self._safe_convert_to_string(row.get("Приоритет \n2 Источники", "")),
                "Цена позиции\nМП c НДС": "",
                "Цена позиции\nB2C c НДС": "",
                "Дельта в процентах": "",
                "Ссылка на источник": "",
                "Цена 2 позиции\nB2C c НДС": ""
            }
            
            json_data.append(record)
        
        return json_data
    
    def _safe_convert_to_float(self, value: Any) -> float:
        """
        Безопасное преобразование значения в float.
        
        Args:
            value: Значение для преобразования
            
        Returns:
            Float значение или 0.0 если преобразование невозможно
        """
        if pd.isna(value) or value == "":
            return 0.0
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Не удалось преобразовать в float: {value}")
            return 0.0
    
    def _safe_convert_to_string(self, value: Any) -> str:
        """
        Безопасное преобразование значения в строку.
        
        Args:
            value: Значение для преобразования
            
        Returns:
            Строковое значение или пустая строка
        """
        if pd.isna(value):
            return ""
        
        return str(value).strip()
    
    @handle_validation_errors(
        component="data_processor",
        return_default=False
    )
    def validate_product_data(self, product: Dict[str, Any]) -> bool:
        """
        Валидирует структуру данных продукта.
        
        Args:
            product: Словарь с данными продукта
            
        Returns:
            True если структура корректна, False иначе
        """
        required_fields = [
            "Код\nмодели",
            "model_name", 
            "Категория",
            "Единица измерения",
            "Приоритет \n1 Источники",
            "Приоритет \n2 Источники"
        ]
        
        # Проверяем наличие обязательных полей
        for field in required_fields:
            if field not in product:
                logger.error(f"Отсутствует обязательное поле: {field}")
                return False
        
        # Проверяем, что код модели является числом
        if not isinstance(product["Код\nмодели"], (int, float)) or product["Код\nмодели"] <= 0:
            logger.error(f"Некорректный код модели: {product['Код\nмодели']}")
            return False
        
        # Проверяем, что название модели не пустое
        if not product["model_name"] or not product["model_name"].strip():
            logger.error("Название модели не может быть пустым")
            return False
        
        return True
    
    @handle_errors(
        category=ErrorCategory.PARSING,
        severity=ErrorSeverity.HIGH,
        component="data_processor",
        recovery_action="Возврат False при ошибке сохранения Excel",
        return_on_error=False
    )
    async def save_excel_data(self, data: List[Dict[str, Any]], file_path: str) -> bool:
        """
        Сохраняет данные в Excel файл с заполненными ценовыми данными.
        
        Args:
            data: Список словарей с данными для сохранения
            file_path: Путь для сохранения Excel файла
            
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            logger.info(f"Сохранение данных в Excel файл: {file_path}")
            
            # Обрабатываем данные перед сохранением
            processed_data = self._process_data_for_output(data)
            
            # Создаем DataFrame из обработанных данных
            df = pd.DataFrame(processed_data)
            
            # Асинхронно сохраняем Excel файл
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._save_excel_sync,
                df,
                file_path
            )
            
            logger.info(f"Данные успешно сохранены в {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении Excel файла: {e}")
            return False
    
    def _process_data_for_output(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Обрабатывает данные для выходного файла, заполняя ценовые поля и рассчитывая дельты.
        
        Args:
            data: Исходные данные продуктов
            
        Returns:
            Обработанные данные с заполненными ценовыми полями
        """
        processed_data = []
        
        for item in data:
            processed_item = item.copy()
            
            # Извлекаем ценовые данные если они есть
            mp_price = self._extract_price_from_data(item, "mp_price")
            b2c_price = self._extract_price_from_data(item, "b2c_price")
            second_b2c_price = self._extract_price_from_data(item, "second_b2c_price")
            source_link = item.get("source_link", "")
            
            # Заполняем ценовые поля
            processed_item["Цена позиции\nМП c НДС"] = self._format_price(mp_price)
            processed_item["Цена позиции\nB2C c НДС"] = self._format_price(b2c_price)
            processed_item["Цена 2 позиции\nB2C c НДС"] = self._format_price(second_b2c_price)
            processed_item["Ссылка на источник"] = source_link if source_link else ""
            
            # Рассчитываем и заполняем дельту в процентах
            if mp_price and b2c_price:
                delta = self.calculate_price_delta(mp_price, b2c_price)
                processed_item["Дельта в процентах"] = f"{delta}%" if delta is not None else ""
            else:
                processed_item["Дельта в процентах"] = ""
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def _extract_price_from_data(self, item: Dict[str, Any], price_key: str) -> Optional[float]:
        """
        Извлекает цену из данных продукта.
        
        Args:
            item: Данные продукта
            price_key: Ключ для извлечения цены
            
        Returns:
            Цена как float или None
        """
        price_value = item.get(price_key)
        
        if price_value is None or price_value == "":
            return None
        
        try:
            return float(price_value)
        except (ValueError, TypeError):
            return None
    
    def _format_price(self, price: Optional[float]) -> str:
        """
        Форматирует цену для отображения в Excel.
        
        Args:
            price: Цена для форматирования
            
        Returns:
            Отформатированная строка с ценой
        """
        if price is None or price <= 0:
            return ""
        
        return f"{price:.2f}"
    
    def _save_excel_sync(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Синхронное сохранение DataFrame в Excel файл.
        
        Args:
            df: DataFrame для сохранения
            file_path: Путь для сохранения
        """
        # Создаем директорию если не существует
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем с настройками для корректного отображения
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Данные')
            
            # Настраиваем ширину колонок для лучшего отображения
            worksheet = writer.sheets['Данные']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def calculate_price_delta(self, price1: Optional[float], price2: Optional[float]) -> Optional[float]:
        """
        Рассчитывает процентную разницу между двумя ценами.
        
        Args:
            price1: Первая цена (базовая)
            price2: Вторая цена для сравнения
            
        Returns:
            Процентная разница или None если расчет невозможен
        """
        if not price1 or not price2 or price1 <= 0 or price2 <= 0:
            return None
        
        try:
            delta = ((price2 - price1) / price1) * 100
            return round(delta, 2)
        except (ZeroDivisionError, TypeError):
            logger.warning(f"Не удалось рассчитать дельту для цен: {price1}, {price2}")
            return None
    
    def validate_excel_structure(self, df: pd.DataFrame) -> bool:
        """
        Валидирует структуру Excel файла.
        
        Args:
            df: DataFrame для валидации
            
        Returns:
            True если структура корректна, False иначе
        """
        required_columns = [
            "Код\nмодели",
            "model_name",
            "Категория", 
            "Единица измерения",
            "Приоритет \n1 Источники",
            "Приоритет \n2 Источники"
        ]
        
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            logger.error(f"Отсутствуют обязательные колонки в Excel файле: {missing_columns}")
            return False
        
        # Проверяем, что есть хотя бы одна строка данных
        if len(df) == 0:
            logger.error("Excel файл не содержит данных")
            return False
        
        return True
    
    def validate_product_list(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Валидирует список продуктов и возвращает только корректные записи.
        
        Args:
            products: Список продуктов для валидации
            
        Returns:
            Список валидных продуктов
        """
        valid_products = []
        invalid_count = 0
        
        for i, product in enumerate(products):
            if self.validate_product_data(product):
                valid_products.append(product)
            else:
                invalid_count += 1
                logger.warning(f"Продукт #{i+1} не прошел валидацию и будет пропущен")
        
        if invalid_count > 0:
            logger.warning(f"Пропущено {invalid_count} некорректных записей из {len(products)}")
        
        logger.info(f"Валидация завершена: {len(valid_products)} корректных записей")
        return valid_products
    
    def handle_excel_read_error(self, error: Exception, file_path: str) -> Dict[str, str]:
        """
        Обрабатывает ошибки чтения Excel файлов и возвращает информативное сообщение.
        
        Args:
            error: Исключение, которое произошло
            file_path: Путь к файлу, который не удалось прочитать
            
        Returns:
            Словарь с информацией об ошибке
        """
        error_info = {
            "file_path": file_path,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if isinstance(error, FileNotFoundError):
            error_info["user_message"] = f"Файл не найден: {file_path}. Убедитесь, что файл существует."
            error_info["error_code"] = "FILE_NOT_FOUND"
        elif isinstance(error, PermissionError):
            error_info["user_message"] = f"Нет доступа к файлу: {file_path}. Проверьте права доступа."
            error_info["error_code"] = "PERMISSION_DENIED"
        elif "BadZipFile" in str(error) or "corrupted" in str(error).lower():
            error_info["user_message"] = f"Файл поврежден или имеет неверный формат: {file_path}"
            error_info["error_code"] = "CORRUPTED_FILE"
        else:
            error_info["user_message"] = f"Ошибка при чтении файла: {error}"
            error_info["error_code"] = "READ_ERROR"
        
        logger.error(f"Ошибка чтения Excel: {error_info}")
        return error_info
    
    def handle_excel_write_error(self, error: Exception, file_path: str) -> Dict[str, str]:
        """
        Обрабатывает ошибки записи Excel файлов и возвращает информативное сообщение.
        
        Args:
            error: Исключение, которое произошло
            file_path: Путь к файлу, который не удалось записать
            
        Returns:
            Словарь с информацией об ошибке
        """
        error_info = {
            "file_path": file_path,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if isinstance(error, PermissionError):
            error_info["user_message"] = f"Нет доступа для записи файла: {file_path}. Возможно, файл открыт в другой программе."
            error_info["error_code"] = "WRITE_PERMISSION_DENIED"
        elif "No space left" in str(error):
            error_info["user_message"] = "Недостаточно места на диске для сохранения файла."
            error_info["error_code"] = "DISK_FULL"
        else:
            error_info["user_message"] = f"Ошибка при записи файла: {error}"
            error_info["error_code"] = "WRITE_ERROR"
        
        logger.error(f"Ошибка записи Excel: {error_info}")
        return error_info
    
    def calculate_advanced_price_delta(self, base_price: Optional[float], 
                                     compare_price: Optional[float],
                                     delta_type: str = "percentage") -> Optional[float]:
        """
        Расширенный расчет разницы между ценами с различными типами дельты.
        
        Args:
            base_price: Базовая цена для сравнения
            compare_price: Цена для сравнения
            delta_type: Тип дельты ("percentage", "absolute", "ratio")
            
        Returns:
            Рассчитанная дельта или None если расчет невозможен
        """
        if not base_price or not compare_price or base_price <= 0 or compare_price <= 0:
            return None
        
        try:
            if delta_type == "percentage":
                return self.calculate_price_delta(base_price, compare_price)
            elif delta_type == "absolute":
                return round(compare_price - base_price, 2)
            elif delta_type == "ratio":
                return round(compare_price / base_price, 3)
            else:
                logger.warning(f"Неизвестный тип дельты: {delta_type}")
                return None
        except (ZeroDivisionError, TypeError) as e:
            logger.warning(f"Ошибка при расчете дельты {delta_type}: {e}")
            return None
    
    def get_processing_statistics(self, original_data: List[Dict[str, Any]], 
                                processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Возвращает статистику обработки данных.
        
        Args:
            original_data: Исходные данные
            processed_data: Обработанные данные
            
        Returns:
            Словарь со статистикой обработки
        """
        stats = {
            "original_count": len(original_data),
            "processed_count": len(processed_data),
            "success_rate": (len(processed_data) / len(original_data) * 100) if original_data else 0,
            "skipped_count": len(original_data) - len(processed_data)
        }
        
        # Подсчитываем записи с ценовыми данными
        records_with_prices = 0
        for item in processed_data:
            if (item.get("Цена позиции\nМП c НДС") and 
                item.get("Цена позиции\nМП c НДС") != ""):
                records_with_prices += 1
        
        stats["records_with_prices"] = records_with_prices
        stats["price_coverage"] = (records_with_prices / len(processed_data) * 100) if processed_data else 0
        
        return stats
    
    def __del__(self):
        """Очистка ресурсов при удалении объекта."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)