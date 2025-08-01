from contextlib import contextmanager
import sqlite3
import threading
import time
from typing import List, Optional, Union

ValueType = Union[str, int, float]


class EKV:
    def __init__(self, database: str):
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.db_lock = threading.Lock()
        self._create_tables()

    def _create_tables(self):
        with self.transaction() as cur:
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.executescript("""
            CREATE TABLE IF NOT EXISTS key_meta (
                namespace   TEXT NOT NULL,
                key         TEXT NOT NULL,
                type        TEXT NOT NULL,
                expires_at  INTEGER,
                PRIMARY KEY (namespace, key)
            );
            CREATE TABLE IF NOT EXISTS kv_store (
                namespace   TEXT NOT NULL,
                key         TEXT NOT NULL,
                field       TEXT NOT NULL,
                value       TEXT NOT NULL,
                PRIMARY KEY (namespace, key, field),
                FOREIGN KEY (namespace, key) 
                    REFERENCES key_meta(namespace, key) 
                    ON DELETE CASCADE
            );
            """)

    @contextmanager
    def transaction(self):
        with self.db_lock:
            cursor = self.db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            try:
                yield cursor
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            finally:
                cursor.close()

    def _get_current_time_ms(self) -> int:
        return int(time.time() * 1000)

    def _check_and_expire_key(
        self, cur: sqlite3.Cursor, namespace: str, key: str
    ) -> bool:
        cur.execute(
            "SELECT expires_at FROM key_meta WHERE namespace = ? AND key = ?",
            (namespace, key),
        )
        row = cur.fetchone()
        if row and row[0] is not None:
            if self._get_current_time_ms() >= row[0]:
                cur.execute(
                    "DELETE FROM key_meta WHERE namespace = ? AND key = ?",
                    (namespace, key),
                )
                return True
        return False

    def _check_key_type(
        self, cur: sqlite3.Cursor, namespace: str, key: str, expected_type: str
    ):
        if self._check_and_expire_key(cur, namespace, key):
            raise KeyError(f"Key '{key}' not found")

        cur.execute(
            "SELECT type FROM key_meta WHERE namespace = ? AND key = ?",
            (namespace, key),
        )
        row = cur.fetchone()
        if not row:
            return False

        if row[0] != expected_type:
            raise TypeError(
                f"Wrong type for key '{key}'. Expected '{expected_type}', but found '{row[0]}'."
            )

        return True

    def _create_or_update_meta(
        self,
        cur: sqlite3.Cursor,
        namespace: str,
        key: str,
        expected_type: str,
        exp: Optional[int] = None,
    ):
        expires_at = (self._get_current_time_ms() + exp) if exp is not None else None

        cur.execute(
            "SELECT type FROM key_meta WHERE namespace = ? AND key = ?",
            (namespace, key),
        )
        row = cur.fetchone()

        if row:
            if row[0] != expected_type:
                raise TypeError(
                    f"Wrong type for key '{key}'. Expected '{expected_type}', but found '{row[0]}'."
                )
            if exp is not None:
                cur.execute(
                    "UPDATE key_meta SET expires_at = ? WHERE namespace = ? AND key = ?",
                    (expires_at, namespace, key),
                )
        else:
            cur.execute(
                "INSERT INTO key_meta (namespace, key, type, expires_at) VALUES (?, ?, ?, ?)",
                (namespace, key, expected_type, expires_at),
            )

    def set(
        self,
        key: str,
        value: ValueType,
        namespace: str = "default",
        exp: Optional[int] = None,
    ):
        with self.transaction() as cur:
            self._check_and_expire_key(cur, namespace, key)
            self._create_or_update_meta(cur, namespace, key, "string", exp)
            cur.execute(
                "REPLACE INTO kv_store (namespace, key, field, value) VALUES (?, ?, '', ?)",
                (namespace, key, str(value)),
            )

    def get(self, key: str, namespace: str = "default") -> Optional[str]:
        with self.transaction() as cur:
            self._check_key_type(cur, namespace, key, "string")

            cur.execute(
                "SELECT value FROM kv_store WHERE namespace = ? AND key = ? AND field = ''",
                (namespace, key),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def incr(
        self,
        key: str,
        amount: int = 1,
        namespace: str = "default",
        exp: Optional[int] = None,
    ) -> int:
        with self.transaction() as cur:
            self._check_and_expire_key(cur, namespace, key)

            cur.execute(
                "SELECT type FROM key_meta WHERE namespace = ? AND key = ?",
                (namespace, key),
            )
            row = cur.fetchone()
            expires_at = (
                (self._get_current_time_ms() + exp) if exp is not None else None
            )

            if row:
                if row[0] != "string":
                    raise TypeError(
                        f"Wrong type for key '{key}'. Expected 'string', but found '{row[0]}'."
                    )
                if exp is not None:
                    cur.execute(
                        "UPDATE key_meta SET expires_at = ? WHERE namespace = ? AND key = ?",
                        (expires_at, namespace, key),
                    )

                cur.execute(
                    "SELECT value FROM kv_store WHERE namespace = ? AND key = ? AND field = ''",
                    (namespace, key),
                )
                existing_row = cur.fetchone()
                current_val_str = existing_row[0] if existing_row else "0"

                if not current_val_str.lstrip("-").isdigit():
                    raise ValueError(f"Value at key '{key}' is not a valid integer.")

                new_value = int(current_val_str) + amount
                cur.execute(
                    "UPDATE kv_store SET value = ? WHERE namespace = ? AND key = ? AND field = ''",
                    (str(new_value), namespace, key),
                )
            else:
                new_value = amount
                cur.execute(
                    "INSERT INTO key_meta (namespace, key, type, expires_at) VALUES (?, ?, ?, ?)",
                    (namespace, key, "string", expires_at),
                )
                cur.execute(
                    "INSERT INTO kv_store (namespace, key, field, value) VALUES (?, ?, '', ?)",
                    (namespace, key, str(new_value)),
                )
            return new_value

    def decr(
        self,
        key: str,
        amount: int = 1,
        namespace: str = "default",
        exp: Optional[int] = None,
    ) -> int:
        return self.incr(key, -amount, namespace, exp)

    def hset(
        self,
        key: str,
        field: str,
        value: ValueType,
        namespace: str = "default",
        exp: Optional[int] = None,
    ):
        with self.transaction() as cur:
            self._check_and_expire_key(cur, namespace, key)
            self._create_or_update_meta(cur, namespace, key, "hash", exp)
            cur.execute(
                "REPLACE INTO kv_store (namespace, key, field, value) VALUES (?, ?, ?, ?)",
                (namespace, key, field, str(value)),
            )

    def hget(self, key: str, field: str, namespace: str = "default") -> Optional[str]:
        with self.transaction() as cur:
            self._check_key_type(cur, namespace, key, "hash")

            cur.execute(
                "SELECT value FROM kv_store WHERE namespace = ? AND key = ? AND field = ?",
                (namespace, key, field),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def dictset(
        self,
        key: str,
        mapping: dict[str, ValueType],
        namespace: str = "default",
        exp: Optional[int] = None,
    ):
        with self.transaction() as cur:
            self._check_and_expire_key(cur, namespace, key)
            self._create_or_update_meta(cur, namespace, key, "hash", exp)
            for field, value in mapping.items():
                cur.execute(
                    "REPLACE INTO kv_store (namespace, key, field, value) VALUES (?, ?, ?, ?)",
                    (namespace, key, field, str(value)),
                )

    def dictget(
        self, key: str, fields: Optional[list[str]] = None, namespace: str = "default"
    ) -> dict[str, Optional[str]]:
        with self.transaction() as cur:
            self._check_key_type(cur, namespace, key, "hash")

            if fields is None:
                cur.execute(
                    "SELECT field, value FROM kv_store WHERE namespace = ? AND key = ?",
                    (namespace, key),
                )
            else:
                placeholders = ", ".join("?" for _ in fields)
                cur.execute(
                    f"""
                    SELECT field, value FROM kv_store
                    WHERE namespace = ? AND key = ? AND field IN ({placeholders})
                    """,
                    (namespace, key, *fields),
                )

            return dict(cur.fetchall())

    def lpush(
        self,
        key: str,
        value: ValueType,
        namespace: str = "default",
        exp: Optional[int] = None,
    ):
        with self.transaction() as cur:
            self._check_and_expire_key(cur, namespace, key)
            self._create_or_update_meta(cur, namespace, key, "list", exp)

            cur.execute(
                "SELECT MIN(CAST(field AS INTEGER)) FROM kv_store WHERE namespace = ? AND key = ?",
                (namespace, key),
            )
            min_index = cur.fetchone()[0]
            new_index = (min_index - 1) if min_index is not None else 0

            cur.execute(
                "INSERT INTO kv_store (namespace, key, field, value) VALUES (?, ?, ?, ?)",
                (namespace, key, str(new_index), str(value)),
            )

    def lrange(
        self, key: str, start: int, end: int, namespace: str = "default"
    ) -> List[str]:
        with self.transaction() as cur:
            self._check_key_type(cur, namespace, key, "list")

            cur.execute(
                "SELECT value FROM kv_store WHERE namespace = ? AND key = ? ORDER BY CAST(field AS INTEGER) ASC",
                (namespace, key),
            )
            all_elements = [row[0] for row in cur.fetchall()]
            list_len = len(all_elements)

            if start < 0:
                start = list_len + start
            if end < 0:
                end = list_len + end
            if start < 0:
                start = 0
            if start > end or start >= list_len:
                return []

            return all_elements[start : end + 1]

    def lget(self, key: str, namespace: str = "default") -> List[str]:
        return self.lrange(key, 0, -1, namespace)

    def ttl(self, key: str, namespace: str = "default") -> int:
        with self.transaction() as cur:
            if self._check_and_expire_key(cur, namespace, key):
                return -2
            cur.execute(
                "SELECT expires_at FROM key_meta WHERE namespace = ? AND key = ?",
                (namespace, key),
            )
            row = cur.fetchone()
            if not row:
                return -2
            expires_at = row[0]
            if expires_at is None:
                return -1
            return max(0, expires_at - self._get_current_time_ms())

    def type(self, key: str, namespace: str = "default") -> Optional[str]:
        with self.transaction() as cur:
            if self._check_and_expire_key(cur, namespace, key):
                return None
            cur.execute(
                "SELECT type FROM key_meta WHERE namespace = ? AND key = ?",
                (namespace, key),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def cleanup(self) -> int:
        with self.transaction() as cur:
            current_time = self._get_current_time_ms()
            cur.execute(
                "DELETE FROM key_meta WHERE expires_at IS NOT NULL AND expires_at < ?",
                (current_time,),
            )
            return cur.rowcount

    def close(self):
        self.db.close()
