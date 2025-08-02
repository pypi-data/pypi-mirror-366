"""
UltraNLP - Ultra-fast, comprehensive NLP preprocessing library
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@domain.com"

from .processor import UltraNLPProcessor
from .tokenizer import UltraFastTokenizer, Token  # Import Token from tokenizer
from .utils import TokenType  # Import TokenType from utils
from .cleaner import HyperSpeedCleaner
from .spell_corrector import LightningSpellCorrector

# Main interface - what users will import
__all__ = [
    'UltraNLPProcessor',
    'UltraFastTokenizer', 
    'HyperSpeedCleaner',
    'LightningSpellCorrector',
    'Token',
    'TokenType',
    'preprocess',
    'batch_preprocess'
]

# Global processor instance
_processor = None

def preprocess(text, options=None):
    """Quick preprocessing function"""
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.process(text, options)

def batch_preprocess(texts, options=None, max_workers=4):
    """Quick batch preprocessing function"""
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.batch_process(texts, options, max_workers)
