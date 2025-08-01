"""Utility functions for examples."""

from pathlib import Path

from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env file."""
    # Find .env file starting from examples directory going up
    current_dir = Path(__file__).parent
    env_path = current_dir.parent / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Fallback to load from current environment
        load_dotenv()
