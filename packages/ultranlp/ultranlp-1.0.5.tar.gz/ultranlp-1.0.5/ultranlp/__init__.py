"""
UltraNLP - Ultra-fast, comprehensive NLP preprocessing library
"""

__version__ = "1.0.5"
__author__ = "DUSHYANT"
__email__ = "dushyantkv508@gmail.com"

# Import all classes from core
from .core import (
    UltraNLPProcessor,
    UltraFastTokenizer,
    HyperSpeedCleaner,
    LightningSpellCorrector,
    Token
)
from .utils import TokenType

# Main interface
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

# Global processor instance for convenience functions
_processor = None

def preprocess(text, options=None):
    """
    Quick preprocessing function
    
    Args:
        text (str): Input text to process
        options (dict, optional): Processing options
        
    Returns:
        dict: Processed results with tokens, cleaned_text, etc.
    """
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.process(text, options)

def batch_preprocess(texts, options=None, max_workers=4):
    """
    Quick batch preprocessing function
    
    Args:
        texts (list): List of texts to process
        options (dict, optional): Processing options
        max_workers (int): Number of parallel workers
        
    Returns:
        list: List of processed results
    """
    global _processor
    if _processor is None:
        _processor = UltraNLPProcessor()
    return _processor.batch_process(texts, options, max_workers)
