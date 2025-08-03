"""
Конфигурация маркетплейсов для системы сравнения цен.

Содержит настройки для всех поддерживаемых маркетплейсов, включая URL,
селекторы для веб-скрапинга и настройки rate limiting.
"""

from typing import Dict, Optional, List


# Конфигурация всех поддерживаемых маркетплейсов
MARKETPLACE_CONFIGS = {
    "komus.ru": {
        "name": "Комус",
        "display_name": "Комус",
        "base_url": "https://www.komus.ru",
        "search_url": "https://www.komus.ru/search?q={query}",
        "selectors": {
            "price": ".price-current, .price-value, .product-price",
            "availability": ".availability-status, .stock-status, .in-stock",
            "product_link": ".product-item a, .product-card a, .product-link",
            "product_title": ".product-title, .product-name, h3 a",
            "currency": ".currency, .price-currency"
        },
        "rate_limit": 2.0,  # секунды между запросами
        "timeout": 30,  # таймаут запроса в секундах
        "max_retries": 3,  # максимальное количество повторных попыток
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    
    "vseinstrumenti.ru": {
        "name": "ВсеИнструменты",
        "display_name": "ВсеИнструменты",
        "base_url": "https://www.vseinstrumenti.ru",
        "search_url": "https://www.vseinstrumenti.ru/search/?what={query}",
        "selectors": {
            "price": ".price-current, .current-price, .product-price",
            "availability": ".availability, .stock-info, .in-stock-label",
            "product_link": ".product-card a, .item-link, .product-item-link",
            "product_title": ".product-title, .item-title, h3 a",
            "currency": ".currency, .price-currency, .rub"
        },
        "rate_limit": 1.5,  # секунды между запросами
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    
    "ozon.ru": {
        "name": "Озон",
        "display_name": "Озон",
        "base_url": "https://www.ozon.ru",
        "search_url": "https://www.ozon.ru/search/?text={query}",
        "selectors": {
            "price": ".price-current, .c2h5, .price-value",
            "availability": ".availability, .stock-text, .delivery-info",
            "product_link": ".tile-hover-target, .product-card a, a[href*='/product/']",
            "product_title": ".tsHeadline550Medium, .product-title, h3",
            "currency": ".currency, .price-currency"
        },
        "rate_limit": 3.0,  # секунды между запросами (более строгий лимит)
        "timeout": 45,  # увеличенный таймаут для Ozon
        "max_retries": 2,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    
    "wildberries.ru": {
        "name": "Wildberries",
        "display_name": "Wildberries",
        "base_url": "https://www.wildberries.ru",
        "search_url": "https://www.wildberries.ru/catalog/0/search.aspx?search={query}",
        "selectors": {
            "price": ".price-current, .product-card__price, .price",
            "availability": ".availability, .product-card__availability",
            "product_link": ".product-card__link, .j-card-link, a[data-popup-nm-id]",
            "product_title": ".product-card__name, .goods-name",
            "currency": ".currency, .price-currency"
        },
        "rate_limit": 2.5,  # секунды между запросами
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    
    "officemag.ru": {
        "name": "Офисмаг",
        "display_name": "Офисмаг",
        "base_url": "https://www.officemag.ru",
        "search_url": "https://www.officemag.ru/search/?q={query}",
        "selectors": {
            "price": ".price-current, .product-price, .price-value",
            "availability": ".availability-status, .stock-status",
            "product_link": ".product-item a, .product-card-link",
            "product_title": ".product-title, .product-name",
            "currency": ".currency, .price-currency"
        },
        "rate_limit": 2.0,  # секунды между запросами
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}


def get_marketplace_config(marketplace_name: str) -> Optional[Dict]:
    """
    Получает конфигурацию маркетплейса по его названию.
    
    Args:
        marketplace_name: Название маркетплейса (например, "komus.ru" или "Комус")
        
    Returns:
        Optional[Dict]: Конфигурация маркетплейса или None, если не найден
    """
    # Прямой поиск по ключу
    if marketplace_name in MARKETPLACE_CONFIGS:
        return MARKETPLACE_CONFIGS[marketplace_name].copy()
    
    # Поиск по display_name
    for key, config in MARKETPLACE_CONFIGS.items():
        if config.get("display_name", "").lower() == marketplace_name.lower():
            return config.copy()
        if config.get("name", "").lower() == marketplace_name.lower():
            return config.copy()
    
    return None


def get_all_marketplace_names() -> List[str]:
    """
    Возвращает список всех поддерживаемых маркетплейсов.
    
    Returns:
        List[str]: Список названий маркетплейсов
    """
    return list(MARKETPLACE_CONFIGS.keys())


def get_marketplace_display_names() -> Dict[str, str]:
    """
    Возвращает словарь соответствия ключей маркетплейсов и их отображаемых названий.
    
    Returns:
        Dict[str, str]: Словарь {ключ: отображаемое_название}
    """
    return {
        key: config.get("display_name", config.get("name", key))
        for key, config in MARKETPLACE_CONFIGS.items()
    }


def get_marketplace_by_display_name(display_name: str) -> Optional[str]:
    """
    Находит ключ маркетплейса по его отображаемому названию.
    
    Args:
        display_name: Отображаемое название маркетплейса (например, "Комус")
        
    Returns:
        Optional[str]: Ключ маркетплейса или None, если не найден
    """
    for key, config in MARKETPLACE_CONFIGS.items():
        if config.get("display_name", "").lower() == display_name.lower():
            return key
        if config.get("name", "").lower() == display_name.lower():
            return key
    
    return None


def validate_marketplace_config(config: Dict) -> bool:
    """
    Проверяет корректность конфигурации маркетплейса.
    
    Args:
        config: Конфигурация маркетплейса
        
    Returns:
        bool: True, если конфигурация корректна
    """
    required_fields = ["name", "base_url", "search_url", "selectors", "rate_limit"]
    required_selectors = ["price", "availability", "product_link", "product_title"]
    
    # Проверка обязательных полей
    for field in required_fields:
        if field not in config:
            return False
    
    # Проверка селекторов
    selectors = config.get("selectors", {})
    for selector in required_selectors:
        if selector not in selectors:
            return False
    
    # Проверка типов данных
    if not isinstance(config["rate_limit"], (int, float)) or config["rate_limit"] <= 0:
        return False
    
    return True


def get_all_marketplaces() -> List[str]:
    """
    Возвращает список всех поддерживаемых маркетплейсов (алиас для get_all_marketplace_names).
    
    Returns:
        List[str]: Список названий маркетплейсов
    """
    return get_all_marketplace_names()


def get_search_url(marketplace_key: str, query: str) -> Optional[str]:
    """
    Формирует URL для поиска на маркетплейсе.
    
    Args:
        marketplace_key: Ключ маркетплейса
        query: Поисковый запрос
        
    Returns:
        Optional[str]: URL для поиска или None, если маркетплейс не найден
    """
    config = get_marketplace_config(marketplace_key)
    if not config:
        return None
    
    search_url_template = config.get("search_url", "")
    if not search_url_template:
        return None
    
    try:
        return search_url_template.format(query=query)
    except KeyError:
        return None


# Проверка корректности всех конфигураций при импорте модуля
def _validate_all_configs():
    """Проверяет корректность всех конфигураций маркетплейсов."""
    invalid_configs = []
    
    for key, config in MARKETPLACE_CONFIGS.items():
        if not validate_marketplace_config(config):
            invalid_configs.append(key)
    
    if invalid_configs:
        raise ValueError(f"Некорректные конфигурации маркетплейсов: {invalid_configs}")


# Выполняем проверку при импорте
_validate_all_configs()