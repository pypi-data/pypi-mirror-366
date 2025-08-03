# Offers Check Marketplaces MCP Server

[![PyPI version](https://badge.fury.io/py/offers-check-marketplaces.svg)](https://badge.fury.io/py/offers-check-marketplaces)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful MCP (Model Context Protocol) server for automated product search and price comparison across multiple marketplaces with integrated license management.

## Features

- 🔍 **Multi-marketplace Search**: Search products across multiple e-commerce platforms
- 💰 **Price Comparison**: Automated price comparison and analysis
- 📊 **Statistics & Analytics**: Comprehensive reporting and data analysis
- 🗄️ **Database Management**: SQLite-based data storage with async operations
- 🔐 **License Management**: Integrated license verification system
- 🌐 **Web Scraping**: Playwright-based web scraping capabilities
- 📈 **Excel Integration**: Import/export data from Excel files
- 🚀 **High Performance**: Async/await architecture for optimal performance

## Supported Marketplaces

- **Komus** (komus.ru) - Office supplies and stationery
- **VseInstrumenti** (vseinstrumenti.ru) - Tools and equipment
- **Ozon** (ozon.ru) - Universal marketplace
- **Wildberries** (wildberries.ru) - Consumer goods
- **OfficeMag** (officemag.ru) - Office supplies

## Installation

### From PyPI

```bash
pip install offers-check-marketplaces
```

### From Source

```bash
git clone https://github.com/yourusername/offers-check-marketplaces-mcp.git
cd offers-check-marketplaces-mcp
pip install -e .
```

## Quick Start

### 1. Basic Usage

```bash
# Run in STDIO mode (for MCP clients)
offers-check-marketplaces

# Run in SSE mode (web server)
offers-check-marketplaces --sse --host 0.0.0.0 --port 8000
```

### 2. MCP Configuration

Add to your MCP client configuration (e.g., `.cursor/mcp.json` or `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "offers_check_marketplaces": {
      "command": "offers-check-marketplaces",
      "env": {
        "LICENSE_KEY": "your-license-key-here"
      }
    }
  }
}
```

### 3. Environment Variables

```bash
# Set license key
export LICENSE_KEY="your-license-key-here"

# Optional: Set custom API endpoint
export API_BASE_URL="https://your-api-endpoint.com"
```

## MCP Tools

The server provides the following MCP tools:

### Core Tools

- **`get_product_details`** - Get detailed product information and prices
- **`get_product_list`** - List all products from database
- **`get_statistics`** - Generate comprehensive statistics

### Data Management Tools

- **`save_product_prices`** - Save found prices to database

### License Management Tools

- **`check_license_status`** - Check current license status
- **`set_license_key`** - Set new license key

### Excel Tools

- **`parse_excel_file`** - Parse Excel file and return structured data
- **`get_excel_info`** - Get information about Excel file structure without reading all data
- **`export_to_excel`** - Export data to Excel file with formatting
- **`filter_excel_data`** - Filter Excel data by specified criteria
- **`transform_excel_data`** - Transform Excel data according to specified rules

## Usage Examples

### Search Products

```python
# Using MCP client

```

### Get Product Details

```python
# Get detailed information about a product
result = await mcp_client.call_tool("get_product_details", {
    "product_code": 195385.0
})
```

### Generate Statistics

```python
# Get comprehensive statistics
result = await mcp_client.call_tool("get_statistics", {})
```

### Parse Excel File

```python
# Parse Excel file with specific parameters
result = await mcp_client.call_tool("parse_excel_file", {
    "file_path": "data/input.xlsx",
    "sheet_name": "Данные",
    "header_row": 0,
    "max_rows": 100
})
```

### Export Data to Excel

```python
# Export processed data to Excel with formatting
result = await mcp_client.call_tool("export_to_excel", {
    "data": processed_data,
    "file_path": "data/output.xlsx",
    "sheet_name": "Результаты",
    "apply_formatting": True,
    "auto_adjust_columns": True
})
```

### Filter Excel Data

```python
# Filter data by multiple criteria
result = await mcp_client.call_tool("filter_excel_data", {
    "data": excel_data,
    "filters": {
        "Категория": "Хозтовары и посуда",
        "Цена позиции\nМП c НДС": {
            "greater_than": 1000,
            "less_than": 5000
        }
    }
})
```

## Configuration

### License Configuration

The system requires a valid license key. You can provide it through:

1. **Environment variable**: `LICENSE_KEY=your-key`
2. **MCP configuration**: Set in the `env` section of your MCP config
3. **Configuration file**: `data/.license_config.json`

### Data Directory

The system automatically creates user data directories following OS standards:

- **Windows**: `%APPDATA%\offers-check-marketplaces\`
- **macOS**: `~/Library/Application Support/offers-check-marketplaces/`
- **Linux**: `~/.local/share/offers-check-marketplaces/` (XDG compliant)

Contains:

- SQLite database (`database/products.db`)
- License cache (`cache/.license_cache.json`)
- Excel files for import/export
- Application logs (`logs/`)

#### Data Migration

The system automatically migrates data from the legacy `./data` directory to the new standard location. During migration:

- Files are safely copied (not moved) to preserve originals
- Migration is skipped if files are currently in use (e.g., Excel files are open)
- The old directory is renamed to `data.migrated` after successful migration

#### Environment Variables

- **`OFFERS_CHECK_DATA_DIR`** - Override default data directory location
- **`OFFERS_CHECK_DISABLE_MIGRATION`** - Set to `true` to disable automatic migration

#### Migration Control

```bash
# Disable automatic migration
export OFFERS_CHECK_DISABLE_MIGRATION=true

# Use custom data directory
export OFFERS_CHECK_DATA_DIR=/path/to/custom/location

# Windows examples
set OFFERS_CHECK_DISABLE_MIGRATION=true
set OFFERS_CHECK_DATA_DIR=C:\MyData\offers-check
```

For detailed migration information, see [Data Migration Guide](docs/guides/DATA_MIGRATION_GUIDE.md).

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/offers-check-marketplaces-mcp.git
cd offers-check-marketplaces-mcp

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
python test_license_integration.py
python test_mcp_license_tools.py
python test_final_integration.py
```

### Building Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Architecture

### Components

- **Server** (`server.py`) - Main MCP server with tool implementations
- **License Manager** (`license_manager.py`) - License verification and management
- **Database Manager** (`database_manager.py`) - SQLite database operations
- **Search Engine** (`search_engine.py`) - Multi-marketplace search coordination
- **Data Processor** (`data_processor.py`) - Excel file processing
- **Statistics Generator** (`statistics.py`) - Analytics and reporting
- **Error Handling** (`error_handling.py`) - Comprehensive error management

### Data Flow

1. **Input**: Excel files with product specifications
2. **Processing**: Search products across marketplaces
3. **Storage**: Save results to SQLite database
4. **Analysis**: Generate statistics and comparisons
5. **Output**: Updated Excel files with prices and analysis

## API Reference

### Get Product Details

```python
get_product_details(product_code: float) -> dict
```

Get detailed information about a specific product.

**Parameters:**

- `product_code` (float): Unique product code from database

**Returns:**

- Dictionary with product details and price analysis

## Error Handling

The system includes comprehensive error handling:

- **License Errors**: Invalid or missing license keys
- **Network Errors**: Marketplace connectivity issues
- **Database Errors**: SQLite operation failures
- **Validation Errors**: Invalid input parameters

All errors are logged and return user-friendly messages.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [GitHub Repository](https://github.com/yourusername/offers-check-marketplaces-mcp)
- **Issues**: [Bug Tracker](https://github.com/yourusername/offers-check-marketplaces-mcp/issues)
- **License**: Contact support for license-related questions

## Changelog

### v0.1.0

- Initial release
- Multi-marketplace product search
- Price comparison and analysis
- Integrated license management
- MCP server implementation
- Excel data processing
- SQLite database storage
- Comprehensive error handling

---

Made with ❤️ for automated marketplace analysis
