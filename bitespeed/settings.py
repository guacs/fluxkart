from __future__ import annotations

import sys
from os import environ
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent


_env_path = ROOT_DIR / ".test.env" if "pytest" in sys.modules else ROOT_DIR / ".env"


load_dotenv(_env_path)


DB_URL: Final[str] = environ["BITESPEED_DB_URL"]
