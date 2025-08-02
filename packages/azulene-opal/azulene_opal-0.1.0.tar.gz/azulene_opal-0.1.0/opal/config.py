# Local token storage

import os
import json
import time
from pathlib import Path
from typing import Optional
from opal import auth

class NotLoggedInException(Exception):
    pass

class TokenExpiredException(Exception):
    pass

CONFIG_DIR = Path.home() / ".opal"
CONFIG_PATH = CONFIG_DIR / "config.json"

def ensure_config_dir():
    """Ensure that the ~/.opal directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_tokens(access_token: str, refresh_token: str, expires_in: int):
    """
    Save tokens to local config file.
    
    Args:
        access_token: JWT token
        refresh_token: Refresh token
        expires_in: Token expiration in seconds
    """
    ensure_config_dir()
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)

def load_tokens() -> Optional[dict]:
    """Load tokens from the local config file."""
    if not CONFIG_PATH.exists(): 
        return None # File doesn't exist
    with open(CONFIG_PATH, "r") as f:
        content = f.read()
        if not content.strip():
            return None  # Config file is empty

        try:
            return json.loads(content)  # File exists, not empty, try parsing
        except json.JSONDecodeError:
            return None  # File content is not valid JSON

def clear_tokens():
    """Delete the local config file (logout)."""
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()

def is_token_expired() -> bool:
    """Check if the current access token is expired."""
    tokens = load_tokens()
    if not tokens:
        return True
    return time.time() >= tokens.get("expires_at", 0)

def get_access_token(allow_expired=False) -> str:
    """
    Return the stored access token.
    
    Args:
        allow_expired: If True, returns the token even if expired.
    
    Raises:
        Exception if not logged in or token expired (unless allow_expired=True)
    """
    tokens = load_tokens()
    if not tokens:
         raise NotLoggedInException("You are not logged in. Please run `opal login`.")

    if is_token_expired() and not allow_expired:
         raise TokenExpiredException("Access token expired. Please run `opal login`.")

    return tokens["access_token"]

def get_refresh_token() -> str:
    """Return the stored refresh token."""
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        raise Exception("Refresh token not available. Please login again.")
    return tokens["refresh_token"]