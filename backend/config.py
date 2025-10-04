"""
AURA Configuration & Constants
All configuration settings and default values
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API KEYS
# ============================================================================

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'aura-secret-key-change-in-production')

# ============================================================================
# AUDIO SETTINGS
# ============================================================================

SAMPLE_RATE = 16000
AUDIO_FORMAT = "linear16"
AUDIO_CONTAINER = "wav"

# ============================================================================
# DEFAULT VOICES (Deepgram Aura)
# ============================================================================

DEFAULT_VOICES = [
    "aura-asteria-en",   # Female - Warm, friendly (Agent 1)
    "aura-arcas-en",     # Male - Deep, mature (Agent 2)
    "aura-athena-en"     # Female - Professional (Agent 3)
]

# ============================================================================
# LLM SETTINGS
# ============================================================================

CEREBRAS_MODEL = "llama-3.3-70b"
CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1/chat/completions"
MAX_TOKENS = 200
MIN_REQUEST_INTERVAL = 1.0  # Seconds between API calls
MAX_RETRIES = 3

# ============================================================================
# SESSION SETTINGS
# ============================================================================

ALLOWED_DURATIONS = [5, 15]  # Minutes
MAX_CONTEXT_MESSAGES = 6  # Keep last N messages in context

# ============================================================================
# FILE PATHS
# ============================================================================

ROOMS_CONFIG_PATH = "rooms.json"
LOGS_DIR = "logs"

# ============================================================================
# MONGODB (for future use)
# ============================================================================

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = 'aura_database' # <-- ADD THIS LINE

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate required configuration"""
    if not DEEPGRAM_API_KEY:
        raise ValueError("❌ DEEPGRAM_API_KEY not found in .env")
    if not CEREBRAS_API_KEY:
        raise ValueError("❌ CEREBRAS_API_KEY not found in .env")
    print("✅ Configuration validated")