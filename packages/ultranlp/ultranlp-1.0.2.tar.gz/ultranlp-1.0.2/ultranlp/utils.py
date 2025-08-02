"""
Utility functions and constants for UltraNLP
"""

from enum import Enum
from dataclasses import dataclass
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

@dataclass(slots=True)
class Token:
    """Optimized token representation"""
    text: str
    start: int
    end: int
    token_type: TokenType
    
    def __hash__(self):
        return hash((self.text, self.token_type))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary"""
        return {
            'text': self.text,
            'start': self.start,
            'end': self.end,
            'type': self.token_type.name
        }

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
