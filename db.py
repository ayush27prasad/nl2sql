from contextlib import asynccontextmanager
from typing import List
import asyncpg

class Database:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    @asynccontextmanager
    async def lifespan(self, app):
        """Handles startup/shutdown of DB pool for FastAPI lifespan."""
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn,
            min_size=1,
            max_size=5,
            command_timeout=60,
        )
        try:
            yield
        finally:
            await self.pool.close()

    async def fetch_all(self, query: str, *args) -> List[asyncpg.Record]:
        """Run a SELECT query and return all rows."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetch_one(self, query: str, *args) -> asyncpg.Record | None:
        """Run a SELECT query and return a single row."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
