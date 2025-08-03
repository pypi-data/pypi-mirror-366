# HotPayments Python SDK

A modern, async-ready Python SDK for the HotPayments API. This SDK provides an easy-to-use interface for integrating HotPayments services into your Python applications.

## Installation

Install the SDK via pip:

```bash
pip install hotpayments-python-sdk
```

## Quick Start

### Basic Usage

```python
import asyncio
from hotpayments import Hotpayments

# Set your API key
Hotpayments.auth('your-api-key-here')

async def main():
    # Initialize the client
    client = Hotpayments()
    
    # Create a customer
    customer = await client.customers().create({
        'name': 'João Silva',
        'email': 'joao@example.com',
        'phone_number': '11999999999',
        'document': '12345678901'
    })
    
    # Create a PIX QR Code transaction
    transaction = await client.transactions().create_pix_qr_code({
        'amount': 100.50,
        'customer_id': customer.uuid,
        'description': 'Payment for services'
    })
    
    print(f"QR Code: {transaction.qr_code}")
    print(f"Transaction ID: {transaction.transaction_id}")

# Run async code
asyncio.run(main())
```

### Synchronous Usage

You can also use the SDK synchronously:

```python
from hotpayments import Hotpayments

# Set your API key
Hotpayments.auth('your-api-key-here')

# Initialize the client
client = Hotpayments()

# Create a customer (synchronous)
customer = client.customers().create_sync({
    'name': 'João Silva',
    'email': 'joao@example.com',
    'phone_number': '11999999999',
    'document': '12345678901'
})

# Create a PIX QR Code transaction (synchronous)
transaction = client.transactions().create_pix_qr_code_sync({
    'amount': 100.50,
    'customer_id': customer.uuid,
    'description': 'Payment for services'
})
```

## Authentication

The SDK requires an API key for authentication. You can set it globally:

```python
from hotpayments import Hotpayments

# Set API key globally
Hotpayments.auth('your-api-key-here')
```

Or pass it directly to the client:

```python
client = Hotpayments(api_key='your-api-key-here')
```

## API Reference

### Customers Service

#### Create Customer

```python
# Async
customer = await client.customers().create({
    'name': 'João Silva',
    'email': 'joao@example.com',
    'phone_number': '11999999999',
    'document': '12345678901'
})

# Sync
customer = client.customers().create_sync({
    'name': 'João Silva',
    'email': 'joao@example.com',
    'phone_number': '11999999999',
    'document': '12345678901'
})
```

#### List Customers

```python
# Async
customers = await client.customers().list(
    page=1,
    per_page=20,
    search='João'
)

# Sync
customers = client.customers().list_sync(
    page=1,
    per_page=20,
    search='João'
)

print(f"Total customers: {customers.total}")
for customer in customers.data:
    print(f"Customer: {customer.name}")
```

### Transactions Service

#### Create PIX QR Code

```python
# Async
qr_code = await client.transactions().create_pix_qr_code({
    'amount': 150.75,
    'customer_id': 'customer-uuid',
    'description': 'Payment description',
    'expires_at': 3600,  # 1 hour in seconds
    'splits': [
        {
            'slug': 'partner-company',
            'type': 'percentage',
            'value': 10.5
        }
    ]
})

# Sync
qr_code = client.transactions().create_pix_qr_code_sync({
    'amount': 150.75,
    'customer_id': 'customer-uuid',
    'description': 'Payment description'
})
```

#### PIX Cashout

```python
# Async
cashout = await client.transactions().pix_cashout({
    'amount': 100.00,
    'pix_key': 'user@example.com',
    'customer_id': 'customer-uuid',
    'description': 'Cashout request'
})

# Sync
cashout = client.transactions().pix_cashout_sync({
    'amount': 100.00,
    'pix_key': 'user@example.com',
    'customer_id': 'customer-uuid',
    'description': 'Cashout request'
})
```

#### Check Transaction Status

```python
# Async
transaction = await client.transactions().check('transaction-uuid')
print(f"Status: {transaction.status}")

# Sync
transaction = client.transactions().check_sync('transaction-uuid')
print(f"Status: {transaction.status}")
```

### Subscriptions Service

#### Create Subscription

```python
# Async
subscription_data = await client.subscriptions().create({
    'customer_id': 'customer-uuid',
    'plan_id': 'plan-uuid',
    'payment_method': 'pix'
})

# Sync
subscription_data = client.subscriptions().create_sync({
    'customer_id': 'customer-uuid',
    'plan_id': 'plan-uuid',
    'payment_method': 'pix'
})
```

#### Get Subscription Details

```python
# Async
subscription = await client.subscriptions().show('subscription-uuid')

# Sync
subscription = client.subscriptions().show_sync('subscription-uuid')
```

#### Cancel Subscription

```python
# Async
subscription = await client.subscriptions().cancel('subscription-uuid', {
    'reason': 'Customer requested cancellation'
})

# Sync
subscription = client.subscriptions().cancel_sync('subscription-uuid', {
    'reason': 'Customer requested cancellation'
})
```

#### Suspend Subscription

```python
# Async
subscription = await client.subscriptions().suspend('subscription-uuid', {
    'reason': 'Payment failure'
})

# Sync
subscription = client.subscriptions().suspend_sync('subscription-uuid', {
    'reason': 'Payment failure'
})
```

#### Reactivate Subscription

```python
# Async
subscription = await client.subscriptions().reactivate('subscription-uuid')

# Sync
subscription = client.subscriptions().reactivate_sync('subscription-uuid')
```

### Subscription Plans Service

#### List Subscription Plans

```python
# Async
plans = await client.subscription_plans().list(
    page=1,
    per_page=20,
    currency='BRL'
)

# Sync
plans = client.subscription_plans().list_sync(
    page=1,
    per_page=20,
    currency='BRL'
)

print(f"Total plans: {plans.total}")
for plan in plans.data:
    print(f"Plan: {plan.name} - Price: {plan.price}")
```

#### Get All Plans

```python
# Async
all_plans = await client.subscription_plans().all(currency='BRL')

# Sync
all_plans = client.subscription_plans().all_sync(currency='BRL')
```

## Type Safety with Pydantic

The SDK uses Pydantic models for type safety and validation:

```python
from hotpayments import CreateCustomerRequest, CreateQrCodeRequest

# Type-safe customer creation
customer_data = CreateCustomerRequest(
    name='João Silva',
    email='joao@example.com',
    phone_number='11999999999',
    document='12345678901'
)

customer = await client.customers().create(customer_data)

# Type-safe QR code creation
qr_data = CreateQrCodeRequest(
    amount=100.50,
    customer_id=customer.uuid,
    description='Payment for order #123'
)

transaction = await client.transactions().create_pix_qr_code(qr_data)
```

## Error Handling

The SDK provides a simple exception class for API errors:

```python
from hotpayments import Hotpayments, HotpaymentsException

try:
    customer = await client.customers().create({
        'name': 'João Silva',
        'email': 'invalid-email',
    })
except HotpaymentsException as e:
    print(f"API Error: {e}")
    if e.status_code:
        print(f"Status Code: {e.status_code}")
```

## Async vs Sync

The SDK supports both asynchronous and synchronous operations:

- **Async methods**: Use `await` with methods like `create()`, `list()`, `show()`, etc.
- **Sync methods**: Use methods ending with `_sync` like `create_sync()`, `list_sync()`, `show_sync()`, etc.

Choose async for better performance in I/O-bound applications, and sync for simpler integration in traditional synchronous codebases.

## Configuration

### Custom Base URL

```python
client = Hotpayments(
    api_key='your-api-key',
    base_url='https://api.hotpayments.com',  # Custom base URL
    timeout=60.0  # Custom timeout in seconds
)
```

### Environment Variables

You can also set the API key using environment variables:

```bash
export HOTPAYMENTS_API_KEY=your-api-key-here
```

## Requirements

- Python 3.8 or higher
- httpx (for HTTP requests)
- pydantic (for data validation and serialization)

## Development

### Installing for Development

```bash
git clone https://github.com/hotpayments/python-sdk.git
cd python-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
isort src tests
```

### Type Checking

```bash
mypy src
```

## Support

For support, please contact [contato@hotpayments.net](mailto:contato@hotpayments.net) or visit our documentation.

## License

This package is open-sourced software licensed under the [MIT license](LICENSE).