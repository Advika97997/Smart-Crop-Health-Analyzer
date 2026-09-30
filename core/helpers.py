from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def truncate(text: str, size: int = 40) -> str:
    text = text or ''
    return text if len(text) <= size else text[: size - 3] + '...'


def export_file_name(prefix: str, ext: str) -> str:
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{stamp}.{ext}'


def normalize_path(path: str) -> str:
    return str(Path(path).expanduser().resolve()) if path else ''
