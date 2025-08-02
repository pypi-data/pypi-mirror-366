"""
Hyper-speed text cleaner with advanced optimization
"""

import re
from typing import Dict, List, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

class HyperSpeedCleaner:
    """Hyper-optimized text cleaner using compiled patterns and efficient algorithms"""
    
    def __init__(self):
        # Pre-compile all patterns for maximum speed
        self._url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+', 
            re.IGNORECASE | re.MULTILINE
        )
        self._email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
            re.IGNORECASE
        )
        self._phone_pattern = re.compile(
            r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        )
        self._emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
            r'\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF'
            r'\U0001F018-\U0001F270\U00002700-\U000027bf]+'
        )
        self._whitespace_pattern = re.compile(r'\s+')
        self._html_pattern = re.compile(r'<[^>]+>')
        self._special_chars_pattern = re.compile(r'[^\w\s.,!?;:-]')
        
        # HTML entity mapping for fast decoding
        self._html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&apos;': "'", '&nbsp;': ' ', '&#39;': "'", '&#x27;': "'",
            '&#x2F;': '/', '&#x60;': '`', '&#x3D;': '='
        }
    
    @lru_cache(maxsize=50000)
    def _clean_cached(self, text: str, options_hash: int) -> str:
        """Cached cleaning for repeated text patterns"""
        return self._clean_internal(text, options_hash)
    
    def _clean_internal(self, text: str, options_hash: int) -> str:
        """Internal cleaning method"""
        # Decode options from hash
        lowercase = bool(options_hash & 1)
        remove_html = bool(options_hash & 2)
        remove_urls = bool(options_hash & 4)
        remove_emails = bool(options_hash & 8)
        remove_phones = bool(options_hash & 16)
        remove_emojis = bool(options_hash & 32)
        normalize_whitespace = bool(options_hash & 64)
        remove_special_chars = bool(options_hash & 128)
        
        # Fast HTML entity decoding
        for entity, replacement in self._html_entities.items():
            if entity in text:
                text = text.replace(entity, replacement)
        
        # Apply cleaning operations
        if remove_html:
            text = self._html_pattern.sub(' ', text)
        if remove_urls:
            text = self._url_pattern.sub('', text)
        if remove_emails:
            text = self._email_pattern.sub('', text)
        if remove_phones:
            text = self._phone_pattern.sub('', text)
        if remove_emojis:
            text = self._emoji_pattern.sub('', text)
        if remove_special_chars:
            text = self._special_chars_pattern.sub('', text)
        if normalize_whitespace:
            text = self._whitespace_pattern.sub(' ', text).strip()
        if lowercase:
            text = text.lower()
        
        return text
    
    def clean(self, text: str, options: Optional[Dict] = None) -> str:
        """Ultra-fast text cleaning with caching"""
        if not text:
            return ""
        
        if options is None:
            from .utils import DEFAULT_CLEAN_OPTIONS
            options = DEFAULT_CLEAN_OPTIONS
        
        # Create hash from options for caching
        options_hash = (
            int(options.get('lowercase', True)) |
            (int(options.get('remove_html', True)) << 1) |
            (int(options.get('remove_urls', True)) << 2) |
            (int(options.get('remove_emails', False)) << 3) |
            (int(options.get('remove_phones', False)) << 4) |
            (int(options.get('remove_emojis', True)) << 5) |
            (int(options.get('normalize_whitespace', True)) << 6) |
            (int(options.get('remove_special_chars', False)) << 7)
        )
        
        return self._clean_cached(text, options_hash)
    
    def batch_clean(self, texts: List[str], options: Optional[Dict] = None, max_workers: int = 4) -> List[str]:
        """Parallel batch cleaning for maximum throughput"""
        if len(texts) < 50:
            return [self.clean(text, options) for text in texts]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(lambda text: self.clean(text, options), texts))
