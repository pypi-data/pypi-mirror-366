"""
Configuration module for OLX database.
"""
import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Settings class for OLX database configuration.
    
    Uses environment variables with OLX_ prefix.
    """
    
    DATABASE_URL: str = os.getenv("OLX_DB_URL")
    
    DEFAULT_SENDING_FREQUENCY_MINUTES: int = int(os.getenv("OLX_DEFAULT_SENDING_FREQUENCY_MINUTES", "60"))
    
    DEFAULT_LAST_MINUTES_GETTING: int = int(os.getenv("OLX_DEFAULT_LAST_MINUTES_GETTING", "30"))

    def __init__(self):
        """Initialize settings and validate required values."""
        if not self.DATABASE_URL:
            raise ValueError(
                "OLX_DB_URL environment variable is required. "
                "Please set it to a valid database URL."
            )

settings = Settings()
