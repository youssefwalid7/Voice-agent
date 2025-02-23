import asyncpg
import os
from typing import Optional
from dotenv import load_dotenv
_pool: Optional[asyncpg.Pool] = None

load_dotenv(dotenv_path=".env")
db_url = os.environ.get("DATABASE_URL")

async def create_pool():
    global _pool
    if not _pool or _pool._closed:
        _pool = await asyncpg.create_pool(
            dsn=db_url,
            min_size=5,
            max_size=20,
            max_inactive_connection_lifetime=300,
            command_timeout=30,
            # ssl="require"  # For production environments
        )
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

def get_pool() -> asyncpg.Pool:
    if not _pool:
        raise RuntimeError("Database pool not initialized. Call create_pool() first.")
    return _pool