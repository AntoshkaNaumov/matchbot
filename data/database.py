import aiosqlite
import io
from typing import Optional, Dict


class DataBase:

    def __init__(self, name: str, table: str) -> None:
        self.name = f"data/{name}"
        self.table = table

    async def create_table(self) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()

            # Создание таблицы users
            query_users = """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name VARCHAR(50),
                name VARCHAR(20),
                age VARCHAR(40),
                city VARCHAR(255),
                sex VARCHAR(20),
                look_for VARCHAR(40),
                about TEXT(500),
                photo BLOB,
                photo_file_id VARCHAR(255),
                likes INTEGER DEFAULT 0,       -- новый столбец для подсчета лайков
                dislikes INTEGER DEFAULT 0     -- новый столбец для подсчета дизлайков
            )
            """
            await cursor.executescript(query_users)

            # Создание таблицы likes
            query_likes = """
            CREATE TABLE IF NOT EXISTS likes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username VARCHAR(50),
                receiver_username VARCHAR(50),
                FOREIGN KEY(sender_username) REFERENCES users(user_name),
                FOREIGN KEY(receiver_username) REFERENCES users(user_name)
            )
            """
            await cursor.executescript(query_likes)

            await db.commit()

            # Вывод информации о таблицах в базе данных
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = await cursor.fetchall()
            print("Таблицы в базе данных:")
            for table in tables:
                print(table[0])

    async def insert(self, user_name, data, photo_data, photo_file_id):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """
                INSERT INTO users(
                user_name,
                name,
                age,
                city,
                sex,
                look_for,
                about,
                photo,
                photo_file_id,
                likes,
                dislikes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_name,) + tuple(data) + (photo_data, photo_file_id, 0, 0)
                # 0 - начальное количество лайков и дизлайков
            )
            await db.commit()

            x = await cursor.execute("SELECT * FROM users")
            y = await x.fetchall()
            for i in y:
                print(i)

    async def get_user_data(self, user_name: Optional[str]) -> Optional[Dict]:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                f"SELECT * FROM users WHERE user_name = ?",
                (user_name,)
            )
            user_data = await cursor.fetchone()
            if user_data:
                return {
                    'user_name': user_data[1],
                    'name': user_data[2],
                    'age': user_data[3],
                    'city': user_data[4],
                    'sex': user_data[5],
                    'look_for': user_data[6],
                    'about': user_data[7],
                    'photo': io.BytesIO(user_data[8]),  # Преобразуем байтовые данные в BytesIO объект
                    'photo_file_id': user_data[9],  # Возвращаем также photo_file_id
                    'likes': user_data[10],  # Возвращаем количество лайков
                    'dislikes': user_data[11]  # Возвращаем количество дизлайков
                }
            else:
                return None

    async def delete_user_data(self, user_name: Optional[str]):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """
                DELETE FROM users
                WHERE user_name = ?
                """,
                (user_name,)
            )
            await db.commit()

    async def get_all_profiles_by_gender(self, user_sex: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            opposite_sex = "Девушка" if user_sex == "Парень" else "Парень"
            await cursor.execute("SELECT * FROM users WHERE sex = ?", (opposite_sex,))
            profiles = await cursor.fetchall()
            return profiles

    async def get_all_profiles(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM users")
            profiles = await cursor.fetchall()
            return profiles

    async def get_author_by_name(self, user_name: Optional[str]):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                f"SELECT * FROM users WHERE user_name = ?",
                (user_name,)
            )
            author_data = await cursor.fetchone()
            if author_data:
                return {
                    'user_name': author_data[1],
                    'name': author_data[2],
                    'age': author_data[3],
                    'city': author_data[4],
                    'sex': author_data[5],
                    'look_for': author_data[6],
                    'about': author_data[7],
                    'photo': io.BytesIO(author_data[8]),  # Преобразуем байтовые данные в BytesIO объект
                    'photo_file_id': author_data[9]  # Возвращаем также photo_file_id
                }
            else:
                return None

    async def increment_likes(self, user_name: Optional[str]):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            # Увеличиваем количество лайков для пользователя с заданным идентификатором на 1
            await cursor.execute(
                """
                UPDATE users
                SET likes = likes + 1
                WHERE user_name = ?
                """,
                (user_name,)
            )
            await db.commit()

    async def insert_like(self, sender_username: str, receiver_username: str) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """
                INSERT INTO likes(sender_username, receiver_username) VALUES (?, ?)
                """,
                (sender_username, receiver_username)
            )
            await db.commit()

    async def get_sent_likes(self, sender_username: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """
                SELECT receiver_username, receiver_username
                FROM likes
                WHERE sender_username = ?
                """,
                (sender_username,)
            )
            likes = await cursor.fetchall()
            return likes
