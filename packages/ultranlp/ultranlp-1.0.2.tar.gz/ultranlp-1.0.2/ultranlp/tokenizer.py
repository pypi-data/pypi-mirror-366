"""
Ultra-fast tokenizer with advanced pattern recognition
"""

import re
import threading
from typing import List, Tuple
from functools import lru_cache

from .utils import Token, TokenType

class UltraFastTokenizer:
    """Ultra-optimized tokenizer using compiled patterns and efficient algorithms"""
    
    def __init__(self):
        self._patterns = self._compile_patterns()
        self._local = threading.local()
        
    def _compile_patterns(self) -> List[Tuple[re.Pattern, TokenType]]:
        """Compile all regex patterns with optimizations"""
        patterns = [
            # Email (optimized pattern)
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE), TokenType.EMAIL),
            
            # URLs (comprehensive but fast)
            (re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE), TokenType.URL),
            
            # Currency patterns (optimized for speed)
            (re.compile(r'(?:\$|€|£|¥|₹|₽)\d+(?:\.\d{1,4})?(?:[KMBkmb])?|\d+(?:\.\d{1,4})?(?:USD|EUR|GBP|JPY|INR|RUB|Rs)\b', re.IGNORECASE), TokenType.CURRENCY),
            
            # Phone numbers (efficient pattern)
            (re.compile(r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'), TokenType.PHONE),
            
            # Date/Time patterns (optimized)
            (re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?:\s?[AaPp][Mm])?)\b'), TokenType.DATETIME),
            
            # Social media (hashtags and mentions)
            (re.compile(r'#\w+'), TokenType.HASHTAG),
            (re.compile(r'@\w+'), TokenType.MENTION),
            
            # Contractions and hyphenated words
            (re.compile(r"\b\w+(?:'\w+)+\b"), TokenType.CONTRACTION),
            (re.compile(r'\b\w+(?:-\w+)+\b'), TokenType.HYPHENATED),
            
            # Emojis (optimized Unicode ranges)
            (re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]+'), TokenType.EMOJI),
            
            # Numbers (including decimals and scientific notation)
            (re.compile(r'\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b'), TokenType.NUMBER),
            
            # Words (Unicode-aware)
            (re.compile(r'\b\w+\b'), TokenType.WORD),
            
            # Punctuation
            (re.compile(r'[^\w\s]'), TokenType.PUNCTUATION),
        ]
        return patterns
    
    def tokenize(self, text: str) -> List[Token]:
        """Ultra-fast tokenization using optimized algorithms"""
        if not text:
            return []
        
        tokens = []
        text_len = len(text)
        processed = [False] * text_len
        
        # Use compiled patterns in order of specificity
        for pattern, token_type in self._patterns:
            for match in pattern.finditer(text):
                start, end = match.span()
                
                # Skip if any position in range is already processed
                if any(processed[i] for i in range(start, end)):
                    continue
                
                # Mark positions as processed
                for i in range(start, end):
                    processed[i] = True
                
                tokens.append(Token(
                    text=match.group(),
                    start=start,
                    end=end,
                    token_type=token_type
                ))
        
        # Sort by position
        tokens.sort(key=lambda x: x.start)
        return tokens
