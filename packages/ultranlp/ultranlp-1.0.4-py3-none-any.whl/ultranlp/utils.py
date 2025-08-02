"""
Utility functions and constants for UltraNLP
"""

from enum import Enum
from typing import Dict, Any

class TokenType(Enum):
    """Token type enumeration for memory efficiency"""
    WORD = 1
    NUMBER = 2
    EMAIL = 3
    URL = 4
    CURRENCY = 5
    PHONE = 6
    HASHTAG = 7
    MENTION = 8
    EMOJI = 9
    PUNCTUATION = 10
    WHITESPACE = 11
    DATETIME = 12
    CONTRACTION = 13
    HYPHENATED = 14

# Default processing options
DEFAULT_CLEAN_OPTIONS = {
    'lowercase': True,
    'remove_html': True,
    'remove_urls': True,
    'remove_emails': False,
    'remove_phones': False,
    'remove_emojis': True,
    'normalize_whitespace': True,
    'remove_special_chars': False
}

DEFAULT_PROCESS_OPTIONS = {
    'clean': True,
    'tokenize': True,
    'spell_correct': False,
    'preserve_structure': True
}
