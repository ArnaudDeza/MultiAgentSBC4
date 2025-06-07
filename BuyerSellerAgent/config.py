"""Configuration settings for the buyer-seller negotiation demo."""

from ollama_utils import OLLAMA_NICKNAMES

# Default model settings
DEFAULT_MODEL = "phi4"
DEFAULT_TEMP = 0.7

# Negotiation parameters
MIN_PRICE = 50
MAX_PRICE = 200
MAX_ROUNDS = 5
CONVERGENCE_THRESHOLD = 0.05  # 5%

# Other defaults
DEFAULT_SEED = 42
DEFAULT_OUTPUT = "negotiation_log.jsonl"

# Export all configuration constants
__all__ = [
    'OLLAMA_NICKNAMES', 'DEFAULT_MODEL', 'DEFAULT_TEMP', 
    'MIN_PRICE', 'MAX_PRICE', 'MAX_ROUNDS', 'CONVERGENCE_THRESHOLD',
    'DEFAULT_SEED', 'DEFAULT_OUTPUT'
] 