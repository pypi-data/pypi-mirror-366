"""
Lightning-fast spell corrector with advanced caching
"""

import re
import threading
from typing import Set
from collections import Counter
from functools import lru_cache

class LightningSpellCorrector:
    """Lightning-fast spell corrector with advanced caching and algorithms"""
    
    def __init__(self):
        self.word_freq = Counter()
        self._correction_cache = {}
        self.alphabet = set('abcdefghijklmnopqrstuvwxyz')
        self._lock = threading.Lock()
        self._load_common_words()
    
    def _load_common_words(self):
        """Load most common English words"""
        common_words = [
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
            'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
            'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
            'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
        ]
        
        for word in common_words:
            self.word_freq[word] = 1000
    
    @lru_cache(maxsize=10000)
    def _edits1(self, word: str) -> frozenset:
        """Generate edit distance 1 words with caching"""
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = frozenset(L + R[1:] for L, R in splits if R)
        transposes = frozenset(L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1)
        replaces = frozenset(L + c + R[1:] for L, R in splits if R for c in self.alphabet)
        inserts = frozenset(L + c + R for L, R in splits for c in self.alphabet)
        return deletes | transposes | replaces | inserts
    
    def correct(self, word: str) -> str:
        """Ultra-fast spell correction with multi-level caching"""
        word_lower = word.lower()
        
        # Level 1: Direct cache lookup
        if word_lower in self._correction_cache:
            return self._correction_cache[word_lower]
        
        # Level 2: Word frequency lookup (already correct)
        if word_lower in self.word_freq:
            self._correction_cache[word_lower] = word
            return word
        
        # Level 3: Edit distance 1
        candidates = self._edits1(word_lower) & set(self.word_freq.keys())
        if candidates:
            best = max(candidates, key=self.word_freq.get)
            self._correction_cache[word_lower] = best
            return best
        
        # Level 4: Edit distance 2 (limited)
        candidates = set()
        for edit1 in self._edits1(word_lower):
            if len(candidates) > 100:
                break
            candidates.update(self._edits1(edit1) & set(self.word_freq.keys()))
        
        if candidates:
            best = max(candidates, key=self.word_freq.get)
            self._correction_cache[word_lower] = best
            return best
        
        # Return original if no correction found
        self._correction_cache[word_lower] = word
        return word
    
    def train(self, text: str):
        """Train spell corrector on text corpus"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        with self._lock:
            self.word_freq.update(words)
