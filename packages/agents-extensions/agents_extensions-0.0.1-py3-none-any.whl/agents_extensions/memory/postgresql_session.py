from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import asyncpg

if TYPE_CHECKING:
    from agents.items import TResponseInputItem

from agents.memory.session import SessionABC


class PostgreSQLSession(SessionABC):
    """PostgreSQL-based implementation of session storage."""

    def __init__(
        self,
        session_id: str,
        dsn: str,
        sessions_table: str = "agent_sessions",
        messages_table: str = "agent_messages",
    ) -> None:
        self.session_id = session_id
        self.dsn = dsn
        self.sessions_table = sessions_table
        self.messages_table = messages_table
        self._pool: asyncpg.Pool | None = None
        # Kick off pool creation and schema init
        self._init_lock = asyncio.Lock()
        self._ready: asyncio.Event = asyncio.Event()

    async def _ensure_ready(self) -> None:
        """Lazily create pool and initialize schema once."""
        async with self._init_lock:
            if not self._ready.is_set():
                self._pool = await asyncpg.create_pool(dsn=self.dsn)
                async with self._pool.acquire() as conn:
                    await conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.sessions_table} (
                            session_id TEXT PRIMARY KEY,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS {self.messages_table} (
                            id SERIAL PRIMARY KEY,
                            session_id TEXT NOT NULL REFERENCES {self.sessions_table}(session_id) ON DELETE CASCADE,
                            message_data JSONB NOT NULL,
                            created_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        CREATE INDEX IF NOT EXISTS idx_{self.messages_table}_session
                            ON {self.messages_table}(session_id, created_at);
                    """)
                self._ready.set()

    async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
        await self._ensure_ready()
        pool_err_msg = "PostgreSQL connection pool not initialized"
        if self._pool is None:
            raise RuntimeError(pool_err_msg)
        sql = f"""
            SELECT message_data
              FROM {self.messages_table}
             WHERE session_id = $1
          ORDER BY created_at {"DESC" if limit else "ASC"}
            {"LIMIT $2" if limit else ""}
        """  # noqa: S608 - Possible SQL injection vector through string-based query construction
        # Only library-controlled table names are interpolated (per OpenAI pattern)
        # All user data goes through parameterized queries
        # i.e. this is safe :)
        params = (self.session_id, limit) if limit else (self.session_id,)
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        items = [json.loads(r["message_data"]) for r in rows]
        return list(reversed(items)) if limit else items

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        if not items:
            return
        await self._ensure_ready()
        pool_err_msg = "PostgreSQL connection pool not initialized"
        if self._pool is None:
            raise RuntimeError(pool_err_msg)
        async with self._pool.acquire() as conn, conn.transaction():
            # Upsert session row
            await conn.execute(
                f"""
                    INSERT INTO {self.sessions_table}(session_id)
                    VALUES($1)
                    ON CONFLICT (session_id) DO NOTHING
                    """,
                self.session_id,
            )
            # Bulk insert messages
            await conn.executemany(
                f"""
                    INSERT INTO {self.messages_table}(session_id, message_data)
                    VALUES($1, $2::jsonb)
                    """,
                [(self.session_id, json.dumps(item)) for item in items],
            )
            # Touch updated_at
            await conn.execute(
                f"""
                    UPDATE {self.sessions_table}
                       SET updated_at = NOW()
                     WHERE session_id = $1
                    """,  # noqa: S608
                # See explanation in async def get_items() function
                self.session_id,
            )

    async def pop_item(self) -> TResponseInputItem | None:
        await self._ensure_ready()
        pool_err_msg = "PostgreSQL connection pool not initialized"
        if self._pool is None:
            raise RuntimeError(pool_err_msg)
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                DELETE FROM {self.messages_table}
                 WHERE id = (
                     SELECT id
                       FROM {self.messages_table}
                      WHERE session_id = $1
                   ORDER BY created_at DESC
                      LIMIT 1
                 )
                RETURNING message_data
                """,  # noqa: S608
                # See explanation in async def get_items() function
                self.session_id,
            )
        if row and row["message_data"]:
            return json.loads(row["message_data"])
        return None

    async def clear_session(self) -> None:
        await self._ensure_ready()
        pool_err_msg = "PostgreSQL connection pool not initialized"
        if self._pool is None:
            raise RuntimeError(pool_err_msg)
        async with self._pool.acquire() as conn, conn.transaction():
            await conn.execute(
                f"DELETE FROM {self.messages_table} WHERE session_id = $1",  # noqa: S608 - See explanation in async def get_items() function
                self.session_id,
            )
            await conn.execute(
                f"DELETE FROM {self.sessions_table} WHERE session_id = $1",  # noqa: S608 - See explanation in async def get_items() function
                self.session_id,
            )

    async def close(self) -> None:
        """Shut down the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
