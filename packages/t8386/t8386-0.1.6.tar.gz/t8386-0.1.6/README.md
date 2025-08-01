# t8386

A comprehensive Python utility library with logger, base classes for account processing, and various helper functions for blockchain and web development.

## Installation

```bash
pip install t8386
```

## Quick Start

```python
from t8386 import Logger

# Basic logging
Logger.log_info("This is an info message")
Logger.log_error("This is an error message")
Logger.log_success("This is a success message")
Logger.log_warning("This is a warning message")
Logger.log_debug("This is a debug message")
Logger.log("This is a generic message")
Logger.log_hana("This is a HANA style message")

# Utils
from t8386 import Utils
email_variations = Utils.generate_gmail("john.doe@gmail.com", multiple_dot=True, maximum=50)
```

## Core Components

### 1. Logger
Colored logging utility with timestamps for better debugging and monitoring.

```python
from t8386 import Logger

Logger.log_info("Application started")
Logger.log_success("Operation completed successfully")
Logger.log_error("An error occurred")
Logger.log_warning("This is a warning")
Logger.log_debug("Debug information")
Logger.log("Generic message")
Logger.log_hana("HANA style message")
```

**Log Levels:**
- `log_info()` - Blue colored info messages
- `log_error()` - Red colored error messages  
- `log_success()` - Green colored success messages
- `log_warning()` - Yellow colored warning messages
- `log_debug()` - Cyan colored debug messages
- `log()` - Generic messages without color
- `log_hana()` - Magenta colored HANA style messages

### 2. Base Classes for Account Processing

#### BaseAccount
Abstract base class for managing user accounts with session handling.

```python
from t8386 import BaseAccount

class MyAccount(BaseAccount):
    def __init__(self, wallet_address, wallet_private_key, **kwargs):
        super().__init__(wallet_address, wallet_private_key, **kwargs)
    
    def to_dict(self):
        data = super().to_dict()
        # Add custom fields
        return data

# Usage
account = MyAccount(
    wallet_address="0x123...",
    wallet_private_key="0xabc...",
    x_auth_token="token123",
    proxy="http://proxy:port"
)

# Session management
session = await account.get_session()
await account.close_session()
```

#### BaseProcessor
Abstract base class for processing multiple accounts with threading support.

```python
from t8386 import BaseProcessor, BaseAccount
import asyncio

class MyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(table_name="my_accounts", file_proxy="proxies.txt")
    
    async def process_single_account(self, account: BaseAccount):
        # Implement your account processing logic
        Logger.log_info(f"Processing {account}")
        # Your custom logic here
        await self.save_account(account)

# Usage
processor = MyProcessor()
account = await processor.prepare_account()
await processor.process_single_account(account)
```

#### BaseRest
Base REST client with common HTTP functionality and Twitter integration.

```python
from t8386 import BaseRest, BaseRestConfig, BaseAccount

class MyRestClient(BaseRest):
    def __init__(self):
        config = BaseRestConfig(
            site="https://example.com",
            base_url="https://api.example.com"
        )
        super().__init__(config)
    
    async def get_header_before_request(self, account: BaseAccount):
        return {"Authorization": f"Bearer {account.x_auth_token}"}

# Usage
client = MyRestClient()
session = await client.before_request(account)
response_data = await client.handle_response(response)
```

#### BaseRestConfig
Configuration class for REST clients.

```python
from t8386 import BaseRestConfig

config = BaseRestConfig(
    site="https://example.com",
    base_url="https://api.example.com/v1",
    headers={"User-Agent": "MyApp/1.0"}
)
```

### 3. Utilities

#### Email Generation
Generate Gmail address variations for testing and automation.

```python
from t8386 import Utils

# Generate simple variations
variations = Utils.generate_gmail("john.doe@gmail.com")
# Output: ['j.ohn.doe@gmail.com', 'jo.hn.doe@gmail.com', ...]

# Generate with multiple dots and uppercase
variations = Utils.generate_gmail(
    "john.doe@gmail.com",
    multiple_dot=True,
    allow_uppercase=True,
    maximum=100
)
```

#### JWT Token Handling
Decode and validate JWT tokens.

```python
from t8386 import Utils

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Check if token is valid
if Utils.jwt_is_valid(token):
    payload = Utils.jwt_to_dict(token)
    Logger.log_success(f"Token valid, expires: {payload.get('exp')}")
else:
    Logger.log_error("Token expired or invalid")

# Alternative validation
is_valid = Utils.check_jwt_token_validity(token)
```

#### File Operations
Read various file formats with error handling.

```python
from t8386 import Utils

# Read text files
lines = Utils.read_file("data.txt")

# Read JSON files
config = Utils.read_file_json("config.json")

# Read CSV files
data = Utils.read_file_csv("users.csv")

# Read proof data with filtering
proof_data = Utils.read_proof_data()  # Reads proof.txt and filters used items

# Append data to file
Utils.append_to_file("log.txt", "New log entry")
```

#### Proxy Management
Handle proxy lists and test connectivity.

```python
from t8386 import Utils

# Load proxy list
proxies = Utils.get_proxy_list("proxies.txt")

# Get working proxy with retries
working_proxy = Utils.retry_get_proxy(proxies, retries=5)

# Test proxy connectivity
if Utils.check_live_proxy("http://user:pass@proxy:port"):
    Logger.log_success("Proxy is working")

# Format proxy string
proxy_str = Utils.proxy_to_str({"host": "proxy.com", "port": 8080})
```

#### Random Generators
Generate various random data for testing.

```python
from t8386 import Utils

# Generate usernames
username = Utils.random_username(length=15)
prefixed_username = Utils.random_username_with_prefix(length=20)

# Generate API credentials
api_key, api_secret = Utils.generate_api_keys()

# Generate unique identifiers
nonce = Utils.generate_nonce(16)
uuid_str = Utils.generate_uuid()
```

#### Cookie and Data Utilities
Extract and process various data formats.

```python
from t8386 import Utils

# Extract cookie values
auth_token = Utils.extract_cookie_value("session=abc; auth_token=xyz", "auth_token")

# Extract auth tokens from files
tokens = Utils.extract_auth_tokens("tokens.json")

# Data type conversions
result = Utils.tuple_to_int((1, 2, 3))
boolean = Utils.tuple_to_bool((True, False))
```

### 4. Wallet Utilities

#### Ethereum Wallet Generation
Generate and manage Ethereum wallets.

```python
from t8386 import Wallet, generate_wallet, personal_sign, recover

# Generate new wallet
wallet = generate_wallet()
print(f"Address: {wallet.address}")
print(f"Private Key: {wallet.private_key}")
print(f"Mnemonic: {wallet.mnemonic}")

# Sign messages
message = "Hello Ethereum!"
signature = personal_sign(message, wallet.private_key)

# Recover signer
recovered_address = recover(message, signature)
print(f"Recovered address: {recovered_address}")
```

#### TRON Wallet Support
Generate and manage TRON wallets.

```python
from t8386 import generate_tron_wallet, tron_sign_message, verify_tron_signature

# Generate TRON wallet
tron_wallet = generate_tron_wallet()
print(f"TRON Address: {tron_wallet.address}")

# Sign TRON messages
signature = tron_sign_message("Hello TRON!", tron_wallet.private_key)

# Verify signature
is_valid = verify_tron_signature("Hello TRON!", signature, tron_wallet.address)
```

### 5. Database Integration

#### Supabase Database
Built-in Supabase integration for data persistence.

```python
from t8386 import SupabseDB

# Initialize database
db = SupabseDB(url="your-url", key="your-key")

# Or use environment variables
# db = SupabseDB()  # Uses SUPABASE_URL and SUPABASE_KEY

# Database operations
data = db.get_data("accounts")
db.insert_data("accounts", {"wallet_address": "0x123...", "balance": 100})
db.update_data("accounts", {"id": 1, "balance": 200}, key_eq="id")
db.delete_data("accounts", "id", "1")

# Bulk operations
db.insert_data_bulk("accounts", [
    {"wallet_address": "0x123...", "balance": 100},
    {"wallet_address": "0x456...", "balance": 200}
])
```

## Complete Example

Here's a complete example showing how to use the library components together:

```python
import asyncio
from t8386 import (
    BaseProcessor, BaseAccount, BaseRest, BaseRestConfig, 
    Logger, Utils, generate_wallet
)

class MyAccount(BaseAccount):
    def __init__(self, wallet_address, wallet_private_key, **kwargs):
        super().__init__(wallet_address, wallet_private_key, **kwargs)
        self.email = kwargs.get('email')
        self.username = kwargs.get('username')
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'email': self.email,
            'username': self.username
        })
        return data

class MyRestClient(BaseRest):
    def __init__(self):
        config = BaseRestConfig(
            site="https://example.com",
            base_url="https://api.example.com/v1"
        )
        super().__init__(config)
    
    async def get_header_before_request(self, account: BaseAccount):
        return {"Authorization": f"Bearer {account.x_auth_token}"}

class MyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(table_name="my_accounts", file_proxy="proxies.txt")
        self.rest = MyRestClient()
    
    async def process_single_account(self, account: MyAccount):
        Logger.log_info(f"Processing account: {account}")
        
        # Get session with proxy
        session = await self.rest.before_request(account)
        
        # Make API calls
        async with session.get("/user/profile") as response:
            result = await self.rest.handle_response(response)
            if result:
                Logger.log_success(f"Profile retrieved for {account}")
        
        # Save to database
        await self.save_account(account)
    
    async def create_new_account(self):
        # Generate wallet
        wallet = generate_wallet()
        
        # Generate account details
        email_variations = Utils.generate_gmail("test@gmail.com", maximum=1)
        username = Utils.random_username()
        
        # Create account
        account = MyAccount(
            wallet_address=wallet.address,
            wallet_private_key=wallet.private_key,
            email=email_variations[0] if email_variations else None,
            username=username,
            proxy=self.prepare_proxy()
        )
        
        return account

async def main():
    processor = MyProcessor()
    
    # Create and process new account
    account = await processor.create_new_account()
    await processor.process_single_account(account)
    
    Logger.log_success("Processing completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Files

### proxies.txt
```
ip1:port1:user1:pass1
ip2:port2:user2:pass2
ip3:port3
```

### Environment Variables
Create a `.env` file:
```bash
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## API Reference

### Logger Methods
| Method | Description | Color |
|--------|-------------|-------|
| `log_info(message)` | Info messages | Blue |
| `log_error(message)` | Error messages | Red |
| `log_success(message)` | Success messages | Green |
| `log_warning(message)` | Warning messages | Yellow |
| `log_debug(message)` | Debug messages | Cyan |
| `log(message)` | Generic messages | Default |
| `log_hana(message)` | HANA style messages | Magenta |

### Utils Methods
| Category | Method | Description |
|----------|--------|-------------|
| **Email** | `generate_gmail(email, multiple_dot, allow_uppercase, maximum)` | Generate Gmail variations |
| **JWT** | `jwt_to_dict(token)`, `jwt_is_valid(token)`, `check_jwt_token_validity(token)` | JWT handling |
| **Files** | `read_file(path)`, `read_file_json(path)`, `read_file_csv(path)`, `append_to_file(path, data)` | File operations |
| **Proxy** | `get_proxy_list(path)`, `check_live_proxy(proxy)`, `retry_get_proxy(proxies, retries)`, `proxy_to_str(proxy)` | Proxy management |
| **Random** | `random_username(length)`, `random_username_with_prefix(length)`, `generate_uuid()`, `generate_nonce(length)`, `generate_api_keys()` | Random generators |
| **Data** | `read_proof_data()`, `extract_auth_tokens(path)`, `extract_cookie_value(cookie_str, key)`, `tuple_to_int(tup)`, `tuple_to_bool(tup)` | Data processing |

### Base Classes

#### BaseAccount
- `__init__(wallet_address, wallet_private_key, **kwargs)`
- `get_session(headers=None, timeout=120)` - Get HTTP session
- `close_session()` - Close HTTP session
- `to_dict()` - Convert to dictionary (abstract method)

#### BaseProcessor
- `__init__(table_name=None, file_proxy=None)` - Initialize processor
- `prepare_account(proxy=None)` - Create new account
- `prepare_proxy()` - Get proxy from list
- `process_single_account(account)` - Process account (abstract)
- `save_account(account)` - Save to database
- `run_account_thread(account, func_name, **kwargs)` - Run in thread
- `after_process(account)` - Cleanup after processing

#### BaseRest
- `__init__(config)` - Initialize with config
- `before_request(account)` - Prepare session
- `handle_response(response)` - Handle HTTP response
- `get_header_before_request(account)` - Get headers (abstract)
- `get_code_x_connect(account, config)` - Twitter integration

#### BaseRestConfig
- `__init__(site, base_url, headers=None)` - Initialize configuration
- `update_headers(token)` - Update headers with token

### Wallet Functions
- `generate_wallet()` - Generate Ethereum wallet
- `personal_sign(message, private_key)` - Sign message
- `recover(message, signature)` - Recover signer address
- `generate_tron_wallet()` - Generate TRON wallet
- `tron_sign_message(message, private_key)` - Sign TRON message
- `verify_tron_signature(message, signature, address)` - Verify TRON signature

### Database (SupabseDB)
- `__init__(url=None, key=None)` - Initialize with credentials
- `get_data(table_name, columns="*", **filters)` - Get data
- `insert_data(table_name, data)` - Insert single record
- `insert_data_bulk(table_name, data_list)` - Insert multiple records
- `update_data(table_name, data, key_eq, key_value=None)` - Update records
- `delete_data(table_name, key, value)` - Delete records

## Requirements

- Python 3.7+
- aiohttp
- colorama
- supabase
- faker
- requests
- web3
- eth-account
- mnemonic
- tronpy

## Installation Options

```bash
# Basic installation
pip install t8386

# Install with development dependencies
pip install t8386[dev]

# Install from source
git clone https://github.com/tyluu/t8386.git
cd t8386
pip install -e .
```

## Error Handling

The library includes comprehensive error handling:

```python
from t8386 import Logger, Utils

try:
    data = Utils.read_file_json("config.json")
except Exception as e:
    Logger.log_error(f"Failed to read config: {str(e)}")

# Proxy handling with retries
proxy = Utils.retry_get_proxy(proxies, retries=3)
if not proxy:
    Logger.log_warning("No working proxy found")
```

## Best Practices

1. **Use async/await** for better performance:
   ```python
   async def process_accounts():
       for account in accounts:
           await processor.process_single_account(account)
   ```

2. **Handle sessions properly**:
   ```python
   try:
       session = await account.get_session()
       # Use session
   finally:
       await account.close_session()
   ```

3. **Log appropriately**:
   ```python
   Logger.log_info("Starting process")
   Logger.log_success("Process completed")
   Logger.log_error("Process failed")
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### v0.1.6
- Initial release
- Logger class with colored output
- Base classes for account processing
- Utils class with comprehensive utility functions
- Wallet utilities for Ethereum and TRON
- Supabase database integration
- Support for email generation, JWT handling, file operations, and proxy management

## License

MIT License

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/tyluu/t8386) or contact the maintainers.

## Acknowledgments

- Built with modern Python async/await patterns
- Integrates with popular blockchain libraries
- Designed for scalable account processing workflows