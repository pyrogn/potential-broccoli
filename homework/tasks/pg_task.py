from dataclasses import dataclass

import asyncpg


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:
        """
        Создайте таблицу items со следующими колонками:
         item_id (int) - обязательное поле, значения должны быть уникальными
         user_id (int) - обязательное поле
         title (str) - обязательное поле
         description (str) - обязательное поле
        """
        # In production environment we will use migration tool
        # like https://github.com/pressly/goose
        await self._pool.execute(
            """CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
            )"""
        )

    async def save_items(self, items: list[ItemEntry]) -> None:
        """
        Напишите код для вставки записей в таблицу items одним запросом, цикл
        использовать нельзя.
        """
        # Don't use str-formatting, query args should be escaped to avoid
        # sql injections https://habr.com/ru/articles/148151/.
        if not items:
            return

        # # version 1
        # await self._pool.executemany(
        #     """INSERT INTO items (item_id, user_id, title, description)
        #     VALUES
        #     ($1, $2, $3, $4)""",
        #     [
        #         (item.item_id, item.user_id, item.title, item.description)
        #         for item in items
        #     ],
        # )

        # version 2, all rows in one query
        # and avoiding string formatting at all costs
        values_insert_sql = ",".join(
            f"(${4 * i + 1}, ${4 * i + 2}, ${4 * i + 3}, ${4 * i + 4})"
            for i in range(len(items))
        )

        query = f"""
        INSERT INTO items (item_id, user_id, title, description) 
        VALUES {values_insert_sql}
        """

        params = [
            value
            for item in items
            for value in (item.item_id, item.user_id, item.title, item.description)
        ]

        await self._pool.execute(query, *params)

    async def find_similar_items(
        self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:
        """
        Напишите код для поиска записей, имеющих указанные user_id, title и description.
        """
        records = await self._pool.fetch(
            """SELECT item_id, user_id, title, description
            FROM items
            WHERE 1=1
                AND user_id = $1
                AND title = $2
                AND description = $3""",
            user_id,
            title,
            description,
        )
        return [ItemEntry(**record) for record in records]
