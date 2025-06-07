"""Configuration settings for the simulated press conference."""

from ollama_utils import OLLAMA_NICKNAMES

# Default model settings
DEFAULT_MODEL = "phi4"
DEFAULT_TEMP = 0.7
DEFAULT_NUM_JOURNALISTS = 4
DEFAULT_SEED = 42
DEFAULT_OUTPUT = "press_log.jsonl"

# Export the OLLAMA_NICKNAMES for use by other modules
__all__ = ['OLLAMA_NICKNAMES', 'DEFAULT_MODEL', 'DEFAULT_TEMP', 'DEFAULT_NUM_JOURNALISTS', 'DEFAULT_SEED', 'DEFAULT_OUTPUT'] 