# Keyra - Key Random Access

**Keyra** (key random access) is the successor to **pyness** - a comprehensive Python utility module designed to simplify common development tasks with secure key generation, datetime utilities, and filename management.

## What is Keyra?

Keyra is a simple yet powerful module that covers essential utilities for your projects and work. While the individual functions are straightforward, this module helps you accomplish tasks quickly and reduces code complexity. It's particularly useful for:

- **Secure key generation** with customizable character sets
- **Password and token creation** for authentication systems
- **Filename management** with timestamps and safe naming
- **Date/time utilities** for logging and file organization
- **Auto-incrementing sequences** for batch processing

## Successor to Pyness

This module builds upon the concepts from **pyness** but with significant improvements:
- Enhanced security with better character sets and validation
- More comprehensive datetime utilities
- Improved filename handling and safety
- Better error handling and user experience
- Expanded functionality for modern development needs

## Install

```bash
pip install keyra
```

## Quick Start

### Basic Key Generation
```python
import keyra

# Generate a simple 8-character key
key = keyra.key(8)
print(key)  # e.g., "Kj9#mN2@"

# Generate only numbers
pin = keyra.key(4, number=True, upper=False, lower=False, symbol=False)
print(pin)  # e.g., "8472"
```

### Advanced Key Generation
```python
# Generate with specific character counts
key = keyra.key(10, number=3, upper=4, lower=2, symbol=1)
print(key)  # e.g., "Kj9#mN2@Xy"

# Use custom character sets
key = keyra.key(6, number="123", upper="ABC", lower=False, symbol=False)
print(key)  # e.g., "A1B2C3"
```

### Password and Token Generation
```python
# Generate secure passwords
password = keyra.generate_password(12)  # 12-character secure password
pin = keyra.generate_pin(6)             # 6-digit numeric PIN
token = keyra.generate_token(32)        # 32-character secure token
```

### Datetime & Filename Utilities
```python
# Append timestamps to filenames
base_name = keyra.key(6)
filename = keyra.append_timestamp(base_name)  # e.g., "Kj9#mN_20250731_173025"

# For OpenCV image saving
import cv2
frame = cv2.imread("input.jpg")
filename = keyra.append_timestamp("frame", fmt="%Y%m%d_%H%M%S") + ".jpg"
cv2.imwrite(filename, frame)

# Auto-incrementing sequences
fname1 = keyra.auto_increment_suffix("img", 1)  # img_001
fname2 = keyra.auto_increment_suffix("img", 2)  # img_002

# Safe filenames
safe = keyra.make_filename_safe("my:illegal*file?.jpg")  # my_illegal_file_.jpg
```

## Features

### Core Functions
- **`key()`**: Main key generation with customizable constraints
- **`generate_password()`**: Generate secure passwords
- **`generate_pin()`**: Generate numeric PINs
- **`generate_token()`**: Generate secure tokens

### Datetime Utilities
- **`append_date()`**: Append current date to strings
- **`append_timestamp()`**: Append timestamp to strings
- **`append_datetime()`**: Append datetime with microseconds
- **`get_formatted_date()`**: Get current date string
- **`get_formatted_timestamp()`**: Get current timestamp string

### Filename Utilities
- **`auto_increment_suffix()`**: Auto-incrementing suffix for sequences
- **`make_filename_safe()`**: Directory-safe filenames
- **`add_extension()`**: Extension handler for files

## Use Cases

- **API Key Generation**: Create secure tokens for API authentication
- **Password Management**: Generate strong passwords for user accounts
- **File Organization**: Create timestamped filenames for data processing
- **Batch Processing**: Auto-incrementing filenames for image/video processing
- **Logging**: Timestamped log files and entries
- **Testing**: Generate test data and identifiers

## Update Log
- **Version 1.0.0**: Complete rewrite with improved key generation
- Enhanced security with better character sets
- Added utility functions for common use cases
- Improved error handling and validation
- Added datetime utility functions for filename generation
- Added filename utilities: auto-increment, safe filenames, extension handler

## Contributing

If you encounter any issues, please create an issue on GitHub. This module is designed to be simple and reliable, but we welcome feedback and improvements.

## License

MIT License - feel free to use this module in your projects.