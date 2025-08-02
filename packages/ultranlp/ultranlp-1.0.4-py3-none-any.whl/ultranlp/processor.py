"""
Main processor class with optimized pipeline
"""

from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .tokenizer import UltraFastTokenizer, Token
from .utils import TokenType, DEFAULT_PROCESS_OPTIONS

from .cleaner import HyperSpeedCleaner
from .spell_corrector import LightningSpellCorrector

class UltraNLPProcessor:
    """Main processor class with optimized pipeline"""
    
    def __init__(self):
        self.tokenizer = UltraFastTokenizer()
        self.cleaner = HyperSpeedCleaner()
        self.spell_corrector = LightningSpellCorrector()
        
        # Performance monitoring
        self._stats = {
            'documents_processed': 0,
            'total_tokens': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def process(self, text: str, options: Optional[Dict] = None) -> Dict:
        """Lightning-fast complete NLP preprocessing"""
        if not text:
            return {'tokens': [], 'cleaned_text': '', 'original_text': text}
        
        if options is None:
            options = DEFAULT_PROCESS_OPTIONS.copy()
        
        # Step 1: Clean text (with caching)
        cleaned_text = self.cleaner.clean(text, options.get('clean_options'))
        
        # Step 2: Tokenize (ultra-fast)
        tokens = self.tokenizer.tokenize(cleaned_text)
        
        # Step 3: Spell correction (optional, for WORD tokens only)
        if options.get('spell_correct', False):
            for token in tokens:
                if token.token_type == TokenType.WORD:
                    token.text = self.spell_corrector.correct(token.text)
        
        # Update stats
        self._stats['documents_processed'] += 1
        self._stats['total_tokens'] += len(tokens)
        
        return {
            'original_text': text,
            'cleaned_text': cleaned_text,
            'tokens': [token.text for token in tokens],
            'token_objects': tokens,
            'token_count': len(tokens),
            'processing_stats': self._stats.copy()
        }
    
    def batch_process(self, texts: List[str], options: Optional[Dict] = None, max_workers: int = 4) -> List[Dict]:
        """Ultra-fast batch processing with parallel execution"""
        if len(texts) < 20:
            return [self.process(text, options) for text in texts]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(lambda text: self.process(text, options), texts))
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return self._stats.copy()
