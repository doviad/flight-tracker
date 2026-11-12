"""Application configuration loaded from environment variables."""

import os
from pathlib import Path


def load_dotenv() -> None:
    """Load simple KEY=VALUE entries from a local .env file without dependencies."""
    env_file = Path(".env")
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def get_api_key() -> str | None:
    value = os.getenv("AVIATIONSTACK_API_KEY", "").strip()
    return value or None


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", "data/flights.db"))


def get_api_timeout() -> int:
    try:
        return max(1, int(os.getenv("API_TIMEOUT", "20")))
    except ValueError:
        return 20
