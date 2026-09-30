from __future__ import annotations

from core.helpers import hash_password
from database.db import execute


def seed_default_user():
    execute(
        '''INSERT IGNORE INTO users (username, password_hash, full_name, role)
           VALUES (%s, %s, %s, %s)''',
        ('admin', hash_password('admin123'), 'System Administrator', 'admin'),
    )


def seed_default_crops():
    values = [
        ('Rice', 'Oryza sativa'),
        ('Wheat', 'Triticum aestivum'),
        ('Tomato', 'Solanum lycopersicum'),
        ('Maize', 'Zea mays'),
        ('Cotton', 'Gossypium hirsutum'),
        ('Sugarcane', 'Saccharum officinarum'),
        ('Potato', 'Solanum tuberosum'),
        ('Banana', 'Musa acuminata'),
    ]
    for crop_name, species in values:
        execute(
            'INSERT IGNORE INTO crops (crop_name, species) VALUES (%s, %s)',
            (crop_name, species),
        )
