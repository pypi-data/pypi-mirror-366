"""SQLite-based key-value storage.

   Initial concept was inspired by the 'sqlite-dbm' project [1].

Reference:
[1] [sqlite-dbm](https://github.com/imbolc/sqlite_dbm/blob/master)
"""

import json
import pickle
import sqlite3
import zlib
from typing import Any, Iterator

from sqlite_construct import (
    SQLiteDBConnection,
    SQLiteDBColumnDefinition,
    SQLiteDBTableDefinition,
    SQLiteDBDefinition,
    DBReference,
    DB_SCHEME,
)

JSON_ERRORS = (TypeError, ValueError, json.JSONDecodeError)


class SQLiteKVDBError(Exception):
    """Generic SQLiteKVDB error."""

    pass


class DUMPER_TYPE:
    """Data dumper type."""

    PICKLE = "pickle"
    JSON = "json"
    STR = "str"


class SQLiteKVDB:
    """SQLite-based key-value storage."""

    def __init__(
        self,
        db_ref: DBReference,
        auto_commit: bool = True,
        dumper_type: str = DUMPER_TYPE.PICKLE,
        pickle_protocol: int = 5,
        compression_level: int = 9,
        smart_compression: bool = True,
        app_codename: str = "",
        app_version: str = "",
    ) -> None:
        """Initialize a SQLiteKVDB instance.

        :raise: SQLiteKVDBError, if operation fails
        """
        if db_ref.scheme == DB_SCHEME.SQLITE3:
            self.db_location: str = db_ref.dbname
        else:
            raise SQLiteKVDBError(f"Initialize DB: Invalid database reference: scheme != {DB_SCHEME.SQLITE3}: {db_ref}")
        self.auto_commit: bool = auto_commit
        self.dumper_type: str = dumper_type
        self.pickle_protocol: int = pickle_protocol
        self.compression_level: int = compression_level
        self.smart_compression: bool = smart_compression
        self.app_codename: str = app_codename
        self.app_version: str = app_version

        match self.dumper_type:
            case DUMPER_TYPE.PICKLE:
                self.loads = lambda data, *args, **kwargs: pickle.loads(data, *args, encoding="bytes", **kwargs)
                self.dumps = lambda data: pickle.dumps(data, protocol=self.pickle_protocol)
            case DUMPER_TYPE.JSON:
                self.loads = lambda data: json.loads(data.decode("utf-8"))
                self.dumps = lambda data: json.dumps(data).encode("utf-8")
            case DUMPER_TYPE.STR:
                self.loads = lambda data: data.decode("utf-8")
                self.dumps = lambda data: data.encode("utf-8")
                str.encode(self.dumps)
                bytes.decode(self.dumps)
            case _:
                raise SQLiteKVDBError(
                    f"Initialize DB: {self.db_location}: Unknown data dumper type: {self.dumper_type}"
                )

        self.db_definition = SQLiteDBDefinition(
            tables=[
                SQLiteDBTableDefinition(
                    name="meta",
                    columns=[
                        # 'app_codename' - identifies the application operating this DB instance
                        SQLiteDBColumnDefinition(name="app_codename", type="TEXT"),
                        # 'app_version' - specifies version of the application operating this DB instance
                        SQLiteDBColumnDefinition(name="app_version", type="TEXT"),
                        # 'dumper_type' - data dumper type
                        SQLiteDBColumnDefinition(name="dumper_type", type="TEXT"),
                    ],
                ),
                SQLiteDBTableDefinition(
                    name="kv",
                    columns=[
                        SQLiteDBColumnDefinition(name="key", type="TEXT", constraint="PRIMARY KEY"),
                        SQLiteDBColumnDefinition(name="value", type="BLOB"),
                        SQLiteDBColumnDefinition(
                            name="compressed", type="BOOLEAN", constraint="NOT NULL CHECK (compressed IN (0, 1))"
                        ),
                    ],
                ),
            ]
        )

        try:
            # Open a connection to the database
            self.db_conn = sqlite3.connect(self.db_location, factory=SQLiteDBConnection)
            self.db_conn.row_factory = sqlite3.Row
            self.db_cursor = self.db_conn.cursor()
            self._prepare_db()
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Connect to database: {self.db_location}: {type(e).__name__}: {e}")
        except SQLiteKVDBError as e:
            raise SQLiteKVDBError(f"Connect to database: {self.db_location}: {e}") from e

    def _prepare_db(self) -> None:
        """Prepare underlying database for use."""
        if self._db_verified():
            return

        self._db_init()

    def _db_verified(self) -> bool:
        """Verify status of the underlying database.

        :return:    True, if the underlying database is ready for use.
                    False, if the underlying database is to be initialized.
        :raise:     SQLiteKVDBError, if the underlying database is not compatible with current DB controller settings.
        """
        if self.db_definition.db_is_void(db_cursor=self.db_cursor):
            # Signal that DB does not hold any schema objects and requires initialization
            return False

        # Verify database structure
        self.db_definition.db_verify(db_cursor=self.db_cursor)

        # Verify database metadata
        try:
            self.db_cursor.execute("SELECT * FROM meta")
            if db_metadata := self.db_cursor.fetchone():
                for mde_name in ("app_codename", "app_version", "dumper_type"):
                    if db_metadata[mde_name] != getattr(self, mde_name):
                        raise SQLiteKVDBError(
                            f"Verify database metadata: '{mde_name}': Does not match current DB controller settings: "
                            f"{db_metadata[mde_name]} != {getattr(self, mde_name)}"
                        )
            else:
                raise SQLiteKVDBError("Verify database metadata: Metadata not found")
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Verify database metadata: {type(e).__name__}: {e}") from e

        # Signal that DB holds expected schema objects, compatible with current DB controller settings and ready for use
        return True

    def _db_init(self) -> None:
        """Initialize underlying database."""
        self.db_definition.db_init(self.db_cursor)
        self.db_cursor.execute(
            "INSERT INTO meta VALUES (?, ?, ?)", (self.app_codename, self.app_version, self.dumper_type)
        )
        self.db_conn.commit()

    def commit(self) -> None:
        """Commit changes to underlying database."""
        self.db_conn.commit()

    def close(self) -> None:
        """Close underlying database.

        :raise: SQLiteKVDBError, if operation fails
        """
        try:
            self.db_conn.commit()
            self.db_conn.execute("VACUUM")
            self.db_conn.close()
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Close database connection: {self.db_location}: {type(e).__name__}: {e}")

    def __getitem__(self, key: str) -> Any:
        """Get item.

        :param key: item's key (id)
        :return:    item's value
        :raise:     KeyError | SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("SELECT * FROM kv WHERE key = ?", (key,))
            row = self.db_cursor.fetchone()

            if row is None:
                raise KeyError(key)

            if row["compressed"] == 1:
                value_bytes = zlib.decompress(row["value"])
            else:
                value_bytes = row["value"]

            value = self.loads(value_bytes)
        except KeyError as e:
            raise KeyError(f"Database {self.db_location}: {key=}") from e
        except Exception as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Get item: {key=}: {type(e).__name__}: {e}") from e

        return value

    def _prepare_kv_field_values(self, key: str, value: Any) -> tuple[str, bytes, bool]:
        """Create a set of DB row field values ready to be saved to underlying database.

        :param key:     DB item's key (id)
        :param value:   DB item's value
        :return:        set of DB row field values
        """
        dump = self.dumps(value)

        if self.compression_level:
            compressed_dump = zlib.compress(dump)

            if self.smart_compression and len(compressed_dump) >= len(dump):
                field_values = (key, sqlite3.Binary(dump), False)
            else:
                field_values = (key, sqlite3.Binary(compressed_dump), True)
        else:
            field_values = (key, sqlite3.Binary(dump), False)

        return field_values

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item.

        :param key:     item's key (id)
        :param value:   item's value
        :raise:         SQLiteKVDBError, if operation fails
        """
        try:
            field_values = self._prepare_kv_field_values(key, value)

            self.db_cursor.execute("REPLACE INTO kv (key, value, compressed) VALUES (?, ?, ?)", field_values)

            if self.auto_commit:
                self.db_conn.commit()
        except Exception as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Set item: {key=}: {type(e).__name__}: {e}") from e

    def __delitem__(self, key: str) -> None:
        """Delete item.

        :param key: item's key (id)
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("DELETE FROM kv WHERE key=?", (key,))

            if self.auto_commit:
                self.db_conn.commit()
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Delete item: {key=}: {type(e).__name__}: {e}") from e

    def __len__(self) -> int:
        """Discover total number of kv-items in database.

        :return:    total number of kv-items in database
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("SELECT COUNT(*) AS count FROM kv")
            db_len = self.db_cursor.fetchone()["count"]
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Get length: {type(e).__name__}: {e}") from e

        return db_len

    def __iter__(self) -> Iterator[str]:
        """Get (default) iterator over keys.

        :return:    iterator over keys
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("SELECT key FROM kv")
            gen = (row["key"] for row in self.db_cursor.fetchall())
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Get iterator: {type(e).__name__}: {e}") from e

        return gen

    def keys(self) -> Iterator[str]:
        """Get iterator over keys.

        :return:    iterator over keys
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            return iter(self)
        except SQLiteKVDBError as e:
            raise SQLiteKVDBError(f"Keys: {e}") from e

    def values(self) -> Iterator[Any]:
        """Get iterator over values.

        :return:    iterator over values
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("SELECT value, compressed FROM kv")
            gen = (
                self.loads(zlib.decompress(row["value"])) if row["compressed"] == 1 else self.loads(row["value"])
                for row in self.db_cursor.fetchall()
            )
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Values: Database {self.db_location}: Get iterator: {type(e).__name__}: {e}") from e

        return gen

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get iterator over items (key/value pairs).

        :return:    iterator over items
        :raise:     SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("SELECT key, value, compressed FROM kv")
            gen = (
                (
                    row["key"],
                    self.loads(zlib.decompress(row["value"])) if row["compressed"] == 1 else self.loads(row["value"]),
                )
                for row in self.db_cursor.fetchall()
            )
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Items: Database {self.db_location}: Get iterator: {type(e).__name__}: {e}") from e

        return gen

    def get(self, key, default=None) -> Any:
        """Get item.

        :param key:     item's key (id)
        :param default: a value to return, if the key is not found
        :return:        item's value, or the 'default' value
        """
        try:
            return self.__getitem__(key=key)
        except KeyError:
            return default

    def update(self, other: dict[str, Any] = None, **kwargs) -> None:
        """Update the database with key/value pairs from 'other', overwriting existing keys.

        :param other:   a dict object to be used as a data source for the update operation
        :param kwargs:  key/value pairs to be used as a data source for the update operation, if the 'other' argument
                        is not of the dict type
        :raise:         SQLiteKVDBError, if operation fails
        """
        _other = other if isinstance(other, dict) else kwargs
        # 'kv row data' scheme: tuple(<key>:str, <value>:bytes, <compressed>:bool)
        kv_rows_data = [self._prepare_kv_field_values(key, value) for key, value in _other.items()]

        try:
            self.db_cursor.executemany("REPLACE INTO kv (key, value, compressed) VALUES (?, ?, ?)", kv_rows_data)

            if self.auto_commit:
                self.db_conn.commit()
        except Exception as e:
            raise SQLiteKVDBError(
                f"Database {self.db_location}: Update: keys={_other.keys()}: {type(e).__name__}: {e}"
            ) from e

    def erase(self) -> None:
        """Remove all key/value data from the database.

        :raise: SQLiteKVDBError, if operation fails
        """
        try:
            self.db_cursor.execute("DELETE FROM kv")

            if self.auto_commit:
                self.db_conn.commit()
        except sqlite3.Error as e:
            raise SQLiteKVDBError(f"Database {self.db_location}: Erase: {type(e).__name__}: {e}") from e
