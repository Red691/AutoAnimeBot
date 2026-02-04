#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2025 Kaif_00z
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/kaif-00z/AutoAnimeBot/blob/main/LICENSE > .

# if you are using this following code then don't forgot to give proper
# credit to t.me/kAiF_00z (github.com/kaif-00z)

import sys

import aiosqlite

from libs.logger import LOGS


class DataBase:
    def __init__(self):
        self.db_path = "anime.db"
        self.db = None

    async def connect(self):
        try:
            LOGS.info("Trying To Link With SQLite")
            self.db = await aiosqlite.connect(self.db_path)
            await self.db.execute(
                "CREATE TABLE IF NOT EXISTS fileInfo (_id TEXT PRIMARY KEY)"
            )
            await self.db.execute(
                "CREATE TABLE IF NOT EXISTS animeChannelInfo (_id TEXT PRIMARY KEY, data TEXT)"
            )
            await self.db.execute(
                "CREATE TABLE IF NOT EXISTS opts (_id TEXT PRIMARY KEY, switch INTEGER)"
            )
            await self.db.execute(
                "CREATE TABLE IF NOT EXISTS fileStore (_id TEXT PRIMARY KEY, data TEXT)"
            )
            await self.db.execute(
                "CREATE TABLE IF NOT EXISTS broadcastInfo (_id TEXT PRIMARY KEY)"
            )
            await self.db.commit()
            LOGS.info("Successfully Linked With SQLite")
        except Exception as error:
            LOGS.critical(str(error))
            sys.exit(1)

    async def add_anime(self, uid):
        await self.db.execute("INSERT OR IGNORE INTO fileInfo (_id) VALUES (?)", (uid,))
        await self.db.commit()

    async def _toggle_opt(self, key, default=False):
        async with self.db.execute(
            "SELECT switch FROM opts WHERE _id=?", (key,)
        ) as cur:
            row = await cur.fetchone()
        new = not (row[0] if row else default)
        await self.db.execute(
            "INSERT OR REPLACE INTO opts (_id, switch) VALUES (?, ?)",
            (key, int(new)),
        )
        await self.db.commit()

    async def _get_opt(self, key, default=False):
        async with self.db.execute(
            "SELECT switch FROM opts WHERE _id=?", (key,)
        ) as cur:
            row = await cur.fetchone()
        return bool(row[0]) if row else default

    async def toggle_separate_channel_upload(self):
        await self._toggle_opt("SEPARATE_CHANNEL_UPLOAD")

    async def is_separate_channel_upload(self):
        return await self._get_opt("SEPARATE_CHANNEL_UPLOAD")

    async def toggle_original_upload(self):
        await self._toggle_opt("OG_UPLOAD")

    async def is_original_upload(self):
        return await self._get_opt("OG_UPLOAD")

    async def toggle_button_upload(self):
        await self._toggle_opt("BUTTON_UPLOAD")

    async def is_button_upload(self):
        return await self._get_opt("BUTTON_UPLOAD")

    async def is_anime_uploaded(self, uid):
        async with self.db.execute("SELECT 1 FROM fileInfo WHERE _id=?", (uid,)) as cur:
            return bool(await cur.fetchone())

    async def add_anime_channel_info(self, title, data):
        await self.db.execute(
            "INSERT OR REPLACE INTO animeChannelInfo (_id, data) VALUES (?, ?)",
            (title, data),
        )
        await self.db.commit()

    async def get_anime_channel_info(self, title):
        async with self.db.execute(
            "SELECT data FROM animeChannelInfo WHERE _id=?", (title,)
        ) as cur:
            row = await cur.fetchone()
        return eval(row[0]) if row else {}

    async def store_items(self, _hash, _list):
        await self.db.execute(
            "INSERT OR REPLACE INTO fileStore (_id, data) VALUES (?, ?)",
            (_hash, _list),
        )
        await self.db.commit()

    async def get_store_items(self, _hash):
        async with self.db.execute(
            "SELECT data FROM fileStore WHERE _id=?", (_hash,)
        ) as cur:
            row = await cur.fetchone()
        return eval(row[0]) if row else []

    async def add_broadcast_user(self, user_id):
        await self.db.execute(
            "INSERT OR IGNORE INTO broadcastInfo (_id) VALUES (?)", (user_id,)
        )
        await self.db.commit()

    async def get_broadcast_user(self):
        async with self.db.execute("SELECT _id FROM broadcastInfo") as cur:
            return [int(row[0]) async for row in cur]

    async def toggle_ss_upload(self):
        await self._toggle_opt("SS_UPLOAD", True)

    async def is_ss_upload(self):
        return await self._get_opt("SS_UPLOAD", True)
