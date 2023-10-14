import aiosqlite as sql


class Database:
    async def init_table() -> None:
        async with sql.connect("database.sqlite") as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS Data (
                    ChatID INTEGER NOT NULL,
                    History STRING
                )
                """
            )
            await db.commit()

    async def get_history(chat_id: int) -> list:
        async with sql.connect("database.sqlite") as db:
            cur = await db.execute("SELECT History FROM Data WHERE ChatID = ?", (chat_id,))
            return await cur.fetchall()

    async def execute(*args, **kwargs):
        async with sql.connect("database.sqlite") as db:
            await db.execute(*args, **kwargs)
            await db.commit()
