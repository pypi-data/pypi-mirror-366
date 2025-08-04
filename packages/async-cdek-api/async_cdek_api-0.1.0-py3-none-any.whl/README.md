# CDEK Python SDK

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-GNU-green.svg)

An asynchronous Python client library for the CDEK API. This SDK provides easy integration with CDEK delivery services, supporting all major API endpoints with type-safe models and comprehensive error handling.

## Features

- **Fully Asynchronous**: Built with `aiohttp` for non-blocking operations
- **Type Safety**: Complete Pydantic models for all API requests and responses
- **Auto Authentication**: Automatic OAuth token management with caching
- **Comprehensive Coverage**: Support for all major CDEK API endpoints:
  - Order management (create, track, update)
  - Tariff calculation and comparison
  - Location and delivery point lookup
  - Courier services
  - Label and document printing
  - Webhook management
- **Error Handling**: Robust error handling with detailed logging
- **Easy Integration**: Simple, intuitive API design

## Requirements

- Python 3.9+
- aiohttp
- pydantic
- loguru

## Installation

```bash
pip install pycdek
```

Or install from source:

```bash
git clone https://github.com/avoidedabsence/pycdek.git
cd pycdek
pip install -e .
```

## Quick Start

```python
import asyncio
from cdek import CDEKAPIClient
from cdek.models import OrderRequest, OrderPackage, OrderSender, OrderRecipient, Location, Money
from cdek.enums import TariffCode

async def main():
    # Initialize the client with your credentials
    client = CDEKAPIClient(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )
    
    # Calculate delivery cost
    from cdek.models import TariffRequest
    tariff_request = TariffRequest(
        type=1,  # Online store
        from_location=Location(code=270),  # Moscow
        to_location=Location(code=44),     # Ekaterinburg
        packages=[{
            "weight": 1000,  # 1kg
            "length": 30,
            "width": 20,
            "height": 10
        }]
    )
    
    tariff = await client.calculate_tariff(tariff_request)
    print(f"Delivery cost: {tariff.delivery_sum} RUB")
    
    # Create an order
    order = OrderRequest(
        type=1,  # Online store
        number="ORDER-001",
        tariff_code=TariffCode.EXPRESS_DOOR_TO_DOOR,
        sender=OrderSender(
            name="John Doe",
            phones=["+7123456789"]
        ),
        recipient=OrderRecipient(
            name="Jane Smith",
            phones=["+7987654321"]
        ),
        from_location=Location(code=270),
        to_location=Location(code=44),
        packages=[OrderPackage(
            number="PKG-001",
            weight=1000
        )]
    )
    
    result = await client.create_order(order)
    print(f"Order created: {result.entity.uuid}")

if __name__ == "__main__":
    asyncio.run(main())
```

## License

This project is licensed under the GNU v3.0 License - see the [LICENSE](LICENSE) file for details.

## Links

- [CDEK API Documentation](https://api.cdek.ru/)
- [PyPI Package](https://pypi.org/project/pycdek/)

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/avoidedabsence/pycdek/issues) page
2. Create a new issue with detailed description
3. Include code examples and error messages
