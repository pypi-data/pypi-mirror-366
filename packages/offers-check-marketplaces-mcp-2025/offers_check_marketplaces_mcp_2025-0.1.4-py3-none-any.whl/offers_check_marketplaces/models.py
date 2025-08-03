"""
Модели данных для системы сравнения цен на маркетплейсах.

Содержит dataclass модели для продуктов, результатов поиска и статистики.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class Product:
    """
    Модель продукта с полной структурой полей из Excel.
    
    Соответствует структуре данных из входного Excel файла с точными названиями полей,
    включая символы переноса строк.
    """
    code: float  # Код\nмодели
    model_name: str  # Название модели товара
    category: str  # Категория
    unit: str  # Единица измерения
    priority_1_source: str  # Приоритет \n1 Источники
    priority_2_source: str  # Приоритет \n2 Источники
    mp_price_with_vat: Optional[float] = None  # Цена позиции\nМП c НДС
    b2c_price_with_vat: Optional[float] = None  # Цена позиции\nB2C c НДС
    delta_percent: Optional[float] = None  # Дельта в процентах
    source_link: Optional[str] = None  # Ссылка на источник
    second_b2c_price_with_vat: Optional[float] = None  # Цена 2 позиции\nB2C c НДС

    @classmethod
    def from_excel_dict(cls, data: dict) -> 'Product':
        """
        Создает экземпляр Product из словаря Excel данных.
        
        Args:
            data: Словарь с данными из Excel файла
            
        Returns:
            Product: Экземпляр продукта
        """
        return cls(
            code=data.get("Код\nмодели", 0.0),
            model_name=data.get("model_name", ""),
            category=data.get("Категория", ""),
            unit=data.get("Единица измерения", ""),
            priority_1_source=data.get("Приоритет \n1 Источники", ""),
            priority_2_source=data.get("Приоритет \n2 Источники", ""),
            mp_price_with_vat=data.get("Цена позиции\nМП c НДС") or None,
            b2c_price_with_vat=data.get("Цена позиции\nB2C c НДС") or None,
            delta_percent=data.get("Дельта в процентах") or None,
            source_link=data.get("Ссылка на источник") or None,
            second_b2c_price_with_vat=data.get("Цена 2 позиции\nB2C c НДС") or None
        )

    def to_excel_dict(self) -> dict:
        """
        Преобразует Product в словарь для записи в Excel.
        
        Returns:
            dict: Словарь с данными для Excel файла
        """
        return {
            "Код\nмодели": self.code,
            "model_name": self.model_name,
            "Категория": self.category,
            "Единица измерения": self.unit,
            "Приоритет \n1 Источники": self.priority_1_source,
            "Приоритет \n2 Источники": self.priority_2_source,
            "Цена позиции\nМП c НДС": self.mp_price_with_vat or "",
            "Цена позиции\nB2C c НДС": self.b2c_price_with_vat or "",
            "Дельта в процентах": self.delta_percent or "",
            "Ссылка на источник": self.source_link or "",
            "Цена 2 позиции\nB2C c НДС": self.second_b2c_price_with_vat or ""
        }


@dataclass
class SearchResult:
    """
    Результат поиска товара на маркетплейсе.
    
    Содержит информацию о найденном товаре, включая цену, наличие и ссылку.
    """
    marketplace: str  # Название маркетплейса
    product_found: bool  # Найден ли товар
    price: Optional[float]  # Цена товара
    currency: str  # Валюта цены
    availability: str  # Статус наличия
    product_url: Optional[str]  # Ссылка на товар
    error_message: Optional[str] = None  # Сообщение об ошибке
    search_timestamp: datetime = None  # Время поиска

    def __post_init__(self):
        """Устанавливает текущее время, если не указано."""
        if self.search_timestamp is None:
            self.search_timestamp = datetime.now()


@dataclass
class Statistics:
    """
    Агрегированная статистика по обработанным товарам.
    
    Содержит метрики о количестве товаров, ценах и покрытии маркетплейсов.
    """
    total_products: int  # Общее количество товаров
    products_with_prices: int  # Товары с найденными ценами
    average_delta_percent: float  # Средняя процентная дельта цен
    category_breakdown: Dict[str, int]  # Разбивка по категориям
    marketplace_coverage: Dict[str, int]  # Покрытие маркетплейсов
    processing_timestamp: datetime = None  # Время обработки

    def __post_init__(self):
        """Устанавливает текущее время, если не указано."""
        if self.processing_timestamp is None:
            self.processing_timestamp = datetime.now()

    @property
    def success_rate(self) -> float:
        """
        Вычисляет процент успешных поисков.
        
        Returns:
            float: Процент товаров с найденными ценами
        """
        if self.total_products == 0:
            return 0.0
        return (self.products_with_prices / self.total_products) * 100.0

    def get_top_categories(self, limit: int = 5) -> Dict[str, int]:
        """
        Возвращает топ категорий по количеству товаров.
        
        Args:
            limit: Максимальное количество категорий
            
        Returns:
            Dict[str, int]: Словарь с топ категориями
        """
        sorted_categories = sorted(
            self.category_breakdown.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_categories[:limit])

    def get_marketplace_coverage_percent(self) -> Dict[str, float]:
        """
        Возвращает процентное покрытие для каждого маркетплейса.
        
        Returns:
            Dict[str, float]: Процентное покрытие маркетплейсов
        """
        if self.total_products == 0:
            return {}
        
        return {
            marketplace: (count / self.total_products) * 100.0
            for marketplace, count in self.marketplace_coverage.items()
        }