import aiomysql
import os

class DatabaseUtils:
    _pool = None

    @staticmethod
    async def init_db() -> None:
        assert DatabaseUtils._pool is None

        DatabaseUtils._pool = await aiomysql.create_pool(
            host = os.getenv("UGS_DB_HOST", "127.0.0.1"),
            port = int(os.getenv("UGS_DB_PORT", "3306")),
            user = os.getenv("UGS_DB_USER", "ugs_user"),
            password = os.getenv("UGS_DB_PASSWORD", ""),
            db = "ugs_db",
            charset = os.getenv("UGS_DB_CHARSET", "utf8"),
            minsize = 10,
            maxsize = 100
        )

    @staticmethod
    async def close_db() -> None:
        assert DatabaseUtils._pool is not None

        DatabaseUtils._pool.close()
        await DatabaseUtils._pool.wait_closed()
        DatabaseUtils._pool = None

    @staticmethod
    async def fetch_object(sql: str, args: tuple[object, ...]) -> tuple[object, ...] | None:
        assert DatabaseUtils._pool is not None

        async with DatabaseUtils._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(sql, args)
                return await cursor.fetchone()

    @staticmethod
    async def fetch_objects(sql: str, args: tuple[object, ...]) -> list[tuple[object, ...]]:
        assert DatabaseUtils._pool is not None

        async with DatabaseUtils._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(sql, args)
                return await cursor.fetchall()

    @staticmethod
    async def execute_sql(sql: str, args: tuple[object, ...]) -> int:
        assert DatabaseUtils._pool is not None

        async with DatabaseUtils._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    await cursor.execute(sql, args)
                    await connection.commit()
                    return cursor.lastrowid
                except Exception:
                    await connection.rollback()
                    raise

    @staticmethod
    async def execute_sqls(sqls: tuple[str, ...], args: tuple[tuple[object, ...], ...]) -> None:
        assert DatabaseUtils._pool is not None

        async with DatabaseUtils._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    for sql, args in zip(sqls, args):
                        await cursor.execute(sql, args)
                    await connection.commit()
                except Exception:
                    await connection.rollback()
                    raise
