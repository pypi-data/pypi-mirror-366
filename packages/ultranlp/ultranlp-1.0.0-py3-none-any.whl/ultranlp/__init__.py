"""
UltraNLP - Ultra-fast, comprehensive NLP preprocessing library
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@domain.com"

from .processor import UltraNLPProcessor
from .tokenizer import UltraFastTokenizer, Token, TokenType
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
    'preprocess',  # Convenience function
    'batch_preprocess'  # Convenience function
]

# Convenience functions for quick usage
_processor = None

def preprocess(text, **options):
    """
    Quick preprocessing function
    
    Args:
        text (str): Input text to process
        **options: Processing options
        
    Returns:
        dict: Processed results
    """
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.process(text, options)

def batch_preprocess(texts, **options):
    """
    Quick batch preprocessing function
    
    Args:
        texts (list): List of texts to process
        **options: Processing options
        
    Returns:
        list: List of processed results
    """
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.batch_process(texts, options)
