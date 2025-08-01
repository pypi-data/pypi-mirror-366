import secrets
import random
from typing import Union, List, Optional
from datetime import datetime


class KeyGenerator:
    """A secure key generator with customizable character sets and constraints."""
    
    # Character sets
    NUMBERS = '0123456789'
    UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
    SYMBOLS = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    def __init__(self):
        self._validate_character_sets()
    
    def _validate_character_sets(self):
        """Validate that character sets don't have duplicates."""
        all_chars = set(self.NUMBERS + self.UPPERCASE + self.LOWERCASE + self.SYMBOLS)
        total_chars = len(self.NUMBERS) + len(self.UPPERCASE) + len(self.LOWERCASE) + len(self.SYMBOLS)
        if len(all_chars) != total_chars:
            raise ValueError("Character sets contain duplicate characters")
    
    def generate_key(
        self,
        length: int,
        numbers: Union[bool, int, str] = True,
        uppercase: Union[bool, int, str] = True,
        lowercase: Union[bool, int, str] = True,
        symbols: Union[bool, int, str] = True,
        exclude_similar: bool = True
    ) -> str:
        """
        Generate a secure random key with specified constraints.
        
        Args:
            length: Length of the generated key
            numbers: Include numbers (True/False), exact count (int), or custom string
            uppercase: Include uppercase letters (True/False), exact count (int), or custom string
            lowercase: Include lowercase letters (True/False), exact count (int), or custom string
            symbols: Include symbols (True/False), exact count (int), or custom string
            exclude_similar: Exclude similar looking characters (0, O, 1, l, I)
        
        Returns:
            Generated secure key string
            
        Raises:
            ValueError: If constraints cannot be satisfied
        """
        if length <= 0:
            raise ValueError("Length must be positive")
        
        # Parse character sets and constraints
        char_sets, constraints = self._parse_parameters(numbers, uppercase, lowercase, symbols)
        
        # Validate constraints
        total_required = sum(constraints.values())
        if total_required > length:
            raise ValueError(f"Required characters ({total_required}) exceed key length ({length})")
        
        # Generate key
        return self._generate_key_with_constraints(length, char_sets, constraints, exclude_similar)
    
    def _parse_parameters(
        self,
        numbers: Union[bool, int, str],
        uppercase: Union[bool, int, str],
        lowercase: Union[bool, int, str],
        symbols: Union[bool, int, str]
    ) -> tuple[dict, dict]:
        """Parse and validate input parameters."""
        char_sets = {}
        constraints = {}
        
        # Numbers
        if isinstance(numbers, bool):
            char_sets['numbers'] = self.NUMBERS if numbers else ''
            constraints['numbers'] = 0
        elif isinstance(numbers, int):
            char_sets['numbers'] = self.NUMBERS
            constraints['numbers'] = numbers
        elif isinstance(numbers, str):
            char_sets['numbers'] = numbers
            constraints['numbers'] = 0
        else:
            raise ValueError("numbers parameter must be bool, int, or str")
        
        # Uppercase
        if isinstance(uppercase, bool):
            char_sets['uppercase'] = self.UPPERCASE if uppercase else ''
            constraints['uppercase'] = 0
        elif isinstance(uppercase, int):
            char_sets['uppercase'] = self.UPPERCASE
            constraints['uppercase'] = uppercase
        elif isinstance(uppercase, str):
            char_sets['uppercase'] = uppercase
            constraints['uppercase'] = 0
        else:
            raise ValueError("uppercase parameter must be bool, int, or str")
        
        # Lowercase
        if isinstance(lowercase, bool):
            char_sets['lowercase'] = self.LOWERCASE if lowercase else ''
            constraints['lowercase'] = 0
        elif isinstance(lowercase, int):
            char_sets['lowercase'] = self.LOWERCASE
            constraints['lowercase'] = lowercase
        elif isinstance(lowercase, str):
            char_sets['lowercase'] = lowercase
            constraints['lowercase'] = 0
        else:
            raise ValueError("lowercase parameter must be bool, int, or str")
        
        # Symbols
        if isinstance(symbols, bool):
            char_sets['symbols'] = self.SYMBOLS if symbols else ''
            constraints['symbols'] = 0
        elif isinstance(symbols, int):
            char_sets['symbols'] = self.SYMBOLS
            constraints['symbols'] = symbols
        elif isinstance(symbols, str):
            char_sets['symbols'] = symbols
            constraints['symbols'] = 0
        else:
            raise ValueError("symbols parameter must be bool, int, or str")
        
        return char_sets, constraints
    
    def _generate_key_with_constraints(
        self,
        length: int,
        char_sets: dict,
        constraints: dict,
        exclude_similar: bool
    ) -> str:
        """Generate key with specified constraints."""
        # Filter out similar characters if requested
        if exclude_similar:
            char_sets = self._exclude_similar_characters(char_sets)
        
        # Generate required characters first
        result = []
        remaining_length = length
        
        for char_type, count in constraints.items():
            if count > 0:
                chars = [secrets.choice(char_sets[char_type]) for _ in range(count)]
                result.extend(chars)
                remaining_length -= count
        
        # Generate remaining characters
        all_chars = ''.join(char_sets.values())
        if all_chars and remaining_length > 0:
            remaining_chars = [secrets.choice(all_chars) for _ in range(remaining_length)]
            result.extend(remaining_chars)
        
        # Shuffle the result
        random.shuffle(result)
        return ''.join(result)
    
    def _exclude_similar_characters(self, char_sets: dict) -> dict:
        """Remove similar-looking characters from character sets."""
        similar_chars = {'0', 'O', '1', 'l', 'I', '5', 'S', '2', 'Z', '8', 'B'}
        
        filtered_sets = {}
        for char_type, chars in char_sets.items():
            filtered_chars = ''.join(c for c in chars if c not in similar_chars)
            filtered_sets[char_type] = filtered_chars
        
        return filtered_sets


# Global instance for convenience
_generator = KeyGenerator()


def key(
    size: int,
    number: Union[bool, int, str] = True,
    upper: Union[bool, int, str] = True,
    symbol: Union[bool, int, str] = True,
    lower: Union[bool, int, str] = True,
    exclude_similar: bool = True
) -> str:
    """
    Generate a secure random key.
    
    Args:
        size: Length of the generated key
        number: Include numbers (True/False), exact count (int), or custom string
        upper: Include uppercase letters (True/False), exact count (int), or custom string
        symbol: Include symbols (True/False), exact count (int), or custom string
        lower: Include lowercase letters (True/False), exact count (int), or custom string
        exclude_similar: Exclude similar looking characters
    
    Returns:
        Generated secure key string
    """
    return _generator.generate_key(
        length=size,
        numbers=number,
        uppercase=upper,
        symbols=symbol,
        lowercase=lower,
        exclude_similar=exclude_similar
    )


# Additional utility functions
def generate_password(length: int = 12, exclude_similar: bool = True) -> str:
    """Generate a secure password with default settings."""
    return key(length, exclude_similar=exclude_similar)


def generate_pin(length: int = 4) -> str:
    """Generate a numeric PIN."""
    return key(length, number=True, upper=False, symbol=False, lower=False)


def generate_token(length: int = 32) -> str:
    """Generate a secure token for API keys, etc."""
    return key(length, exclude_similar=False)


# Datetime utility functions
def append_date(base_string: str, fmt: str = "%Y%m%d", separator: str = "_") -> str:
    """
    Append current date to a string.
    
    Args:
        base_string: The base string to append date to
        fmt: Date format string (default: "%Y%m%d")
        separator: Separator between base string and date (default: "_")
    
    Returns:
        String with appended date
        
    Example:
        >>> append_date("abcxyz")
        'abcxyz_20250731'
    """
    current_date = datetime.now().strftime(fmt)
    return f"{base_string}{separator}{current_date}"


def append_timestamp(base_string: str, fmt: str = "%Y%m%d_%H%M%S", separator: str = "_") -> str:
    """
    Append current timestamp to a string.
    
    Args:
        base_string: The base string to append timestamp to
        fmt: Timestamp format string (default: "%Y%m%d_%H%M%S")
        separator: Separator between base string and timestamp (default: "_")
    
    Returns:
        String with appended timestamp
        
    Example:
        >>> append_timestamp("abcxyz")
        'abcxyz_20250731_173025'
    """
    current_timestamp = datetime.now().strftime(fmt)
    return f"{base_string}{separator}{current_timestamp}"


def append_datetime(base_string: str, fmt: str = "%Y%m%d_%H%M%S_%f", separator: str = "_") -> str:
    """
    Append current datetime with microseconds to a string.
    
    Args:
        base_string: The base string to append datetime to
        fmt: Datetime format string (default: "%Y%m%d_%H%M%S_%f")
        separator: Separator between base string and datetime (default: "_")
    
    Returns:
        String with appended datetime
        
    Example:
        >>> append_datetime("abcxyz")
        'abcxyz_20250731_173025_123456'
    """
    current_datetime = datetime.now().strftime(fmt)
    return f"{base_string}{separator}{current_datetime}"


def get_formatted_date(fmt: str = "%Y%m%d") -> str:
    """
    Get current date in specified format.
    
    Args:
        fmt: Date format string (default: "%Y%m%d")
    
    Returns:
        Formatted date string
        
    Example:
        >>> get_formatted_date()
        '20250731'
    """
    return datetime.now().strftime(fmt)


def get_formatted_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp in specified format.
    
    Args:
        fmt: Timestamp format string (default: "%Y%m%d_%H%M%S")
    
    Returns:
        Formatted timestamp string
        
    Example:
        >>> get_formatted_timestamp()
        '20250731_173025'
    """
    return datetime.now().strftime(fmt)


def auto_increment_suffix(base: str, idx: int, width: int = 3, separator: str = '_') -> str:
    """
    Append an auto-incrementing, zero-padded suffix to a base string.
    Example: auto_increment_suffix('img', 2) -> 'img_002'
    Args:
        base: The base string (e.g., 'img')
        idx: The index to append (e.g., 2)
        width: Zero-padding width (default 3)
        separator: Separator between base and number (default '_')
    Returns:
        String with incremented suffix
    """
    return f"{base}{separator}{idx:0{width}d}"


def make_filename_safe(name: str, replacement: str = '_') -> str:
    """
    Make a string safe for use as a filename on all major OSes by removing/replacing invalid characters.
    Args:
        name: The original filename string
        replacement: Replacement for invalid characters (default '_')
    Returns:
        Safe filename string
    """
    import re
    # Windows: \\ / : * ? " < > |, Unix: /
    invalid = r'[\\/:*?"<>|]'
    # Remove control characters (ASCII 0-31)
    name = re.sub(r'[\x00-\x1f]', replacement, name)
    # Remove invalid filename characters
    name = re.sub(invalid, replacement, name)
    # Remove trailing dots and spaces (Windows)
    name = name.rstrip('. ')
    return name


def add_extension(filename: str, ext: str) -> str:
    """
    Add an extension to a filename, handling the dot automatically.
    Args:
        filename: The base filename (without extension)
        ext: The extension (with or without leading dot)
    Returns:
        Filename with extension
    Example:
        add_extension('frame_20250731', 'jpg') -> 'frame_20250731.jpg'
        add_extension('frame_20250731', '.mp4') -> 'frame_20250731.mp4'
    """
    ext = ext if ext.startswith('.') else f'.{ext}'
    # Remove existing extension if present
    import os
    filename, _ = os.path.splitext(filename)
    return f"{filename}{ext}"

