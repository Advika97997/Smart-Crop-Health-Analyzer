from __future__ import annotations

from pathlib import Path

ALLOWED_SUFFIXES = {'.png', '.jpg', '.jpeg', '.bmp'}


def validate_required(value: str, label: str) -> str:
    if not value or not value.strip():
        return f'{label} is required.'
    return ''


def validate_alpha_space(value: str, label: str, min_len: int = 2, allow_dot: bool = False, allow_comma: bool = False) -> str:
    value = (value or '').strip()
    if not value:
        return f'{label} is required.'
    if len(value) < min_len:
        return f'{label} must be at least {min_len} characters.'
    for ch in value:
        if ch.isalpha() or ch.isspace():
            continue
        if allow_dot and ch == '.':
            continue
        if allow_comma and ch == ',':
            continue
        return f'{label} has invalid characters.'
    return ''


def validate_phone(value: str) -> str:
    value = (value or '').strip()
    if not value:
        return 'Phone number is required.'
    if not value.isdigit() or len(value) != 10:
        return 'Phone number must be exactly 10 digits.'
    return ''


def validate_positive_number(value: str, label: str) -> str:
    value = (value or '').strip()
    if not value:
        return f'{label} is required.'
    try:
        if float(value) <= 0:
            return f'{label} must be greater than 0.'
    except ValueError:
        return f'{label} must be numeric.'
    return ''


def validate_image_file(path: str) -> str:
    if not path:
        return 'Please upload an image first.'
    suffix = Path(path).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        return 'Only PNG, JPG, JPEG, and BMP images are supported.'
    return ''


def validate_notes(text: str, max_len: int = 255) -> str:
    if len((text or '').strip()) > max_len:
        return f'Notes must be at most {max_len} characters.'
    return ''
