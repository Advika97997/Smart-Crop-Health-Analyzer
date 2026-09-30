from __future__ import annotations

from contextlib import contextmanager

from config.settings import DB_CONFIG

try:
    import mysql.connector  # type: ignore
    from mysql.connector import Error as MySQLError  # type: ignore
except Exception:  # pragma: no cover - handled gracefully for runtime
    mysql = None
    class MySQLError(Exception):
        pass


class DatabaseError(Exception):
    pass


def ensure_driver():
    if mysql is None:
        raise DatabaseError(
            'mysql-connector-python is not installed. Run: pip install mysql-connector-python'
        )


@contextmanager
def get_connection():
    ensure_driver()
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except MySQLError as exc:
        raise DatabaseError(f'MySQL connection failed: {exc}') from exc
    finally:
        if conn and conn.is_connected():
            conn.close()


def fetch_all(query: str, params=None, dictionary: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()


def fetch_one(query: str, params=None, dictionary: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()


def execute(query: str, params=None, many: bool = False, values=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            if many:
                cursor.executemany(query, values or [])
            else:
                cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except MySQLError as exc:
            conn.rollback()
            raise DatabaseError(f'Database write failed: {exc}') from exc
        finally:
            cursor.close()
