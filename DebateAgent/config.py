# Configuration file for multi-agent debate system

OLLAMA_NICKNAMES = {
    "gemma3:12b": "gemma3_12b",
    "phi4": "phi4",
    "qwq": "qwq",
    "llama3.3": "llama3_3",
    "phi4-mini": "phi4_mini",
}

# Default configuration values
DEFAULT_MODEL = "phi4:latest"
DEFAULT_TEMP = 0.7
DEFAULT_SEED = 42

# Ollama query parameters
DEFAULT_NUM_CTX = 4096
DEFAULT_TOP_K = 40
DEFAULT_TOP_P = 0.9
DEFAULT_MIN_P = 0.05
DEFAULT_REPEAT_PENALTY = 1.1 