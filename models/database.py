import os
import asyncio
import aiosqlite


class DataBase:
    @classmethod
    async def get_db_obj(cls, loop=None):
        file_path = './db_files/dialog.db'
        connector = await aiosqlite.connect(file_path)
        return cls(connector=connector, loop=loop)

    def __init__(self, connector, loop=None):
        self.con = connector
        self.cur = None
        self.loop = loop

    async def create_tables(self):
        self.cur = await self.con.executescript("""
                    CREATE TABLE IF NOT EXISTS dialog_table (
                        ID INTEGER PRIMARY KEY,
                        question VARCHAR(255) NOT NULL,
                        answer VARCHAR(1020) NOT NULL,
                        UNIQUE(question)
                    );
                    CREATE TABLE IF NOT EXISTS clients (
                        user_id INTEGER PRIMARY KEY,
                        username VARCHAR(255) NOT NULL,
                        fullname VARCHAR(255) NOT NULL
                    );
                """)
        await self.con.commit()

    async def fill_dialog_table(self, question_answer: dict) -> None:
        self.cur = await self.con.executemany("INSERT OR IGNORE INTO dialog_table VALUES(NULL, ?, ?)",
                                              list(question_answer.items()))
        await self.con.commit()

    async def select_all_question_dict(self) -> dict:
        self.cur = await self.con.execute('SELECT id, question FROM dialog_table')
        fetch_result = await self.cur.fetchall()
        return dict(fetch_result) if fetch_result else {}

    async def select_question_dict_like_tag_list(self, tag_list: list) -> dict:
        tag_count = len(tag_list)
        select_like = "SELECT ID, question FROM dialog_table WHERE question LIKE ?"
        select_like += ((' UNION ' + select_like) * (tag_count-1))
        self.cur = await self.con.execute(select_like,
                                          tuple(map(lambda x: '%'+x+'%', tag_list)))
        fetch_result = await self.cur.fetchall()
        return dict(fetch_result) if fetch_result else {}

    async def select_answer_by_question(self, question: str) -> str | None:
        select_answer = "SELECT answer FROM dialog_table WHERE question = ?"
        self.cur = await self.con.execute(select_answer, (question,))
        fetch_result = await self.cur.fetchone()
        return str(tuple(fetch_result)[0]) if fetch_result else None

    async def select_answer_by_id(self, item_id: int) -> str | None:
        self.cur = await self.con.execute('SELECT answer FROM dialog_table WHERE id = ?', (item_id,))
        fetch_result = await self.cur.fetchone()
        return str(tuple(fetch_result)[0]) if fetch_result else None

    async def check_user_by_id(self, user_id: int) -> bool:
        self.cur = await self.con.execute('SELECT * FROM clients WHERE user_id = ?', (user_id,))
        fetch_result = await self.cur.fetchone()
        return fetch_result is not None

    async def add_user(self, user_data) -> None:
        self.cur = await self.con.execute(
          """
            INSERT OR IGNORE INTO clients (user_id, username, fullname) VALUES (:user_id, :username, :fullname);
          """, user_data)
        await self.con.commit()

    def __del__(self):
        if not self.loop:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        if self.cur:
            self.loop.run_until_complete(self.cur.close())
        if self.con:
            self.loop.run_until_complete(self.con.close())
        self.loop.close()
