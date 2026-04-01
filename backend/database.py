from typing import Any, Optional
from datetime import datetime, date

from pymongo import AsyncMongoClient
from gridfs.asynchronous import AsyncGridFS
from bson import ObjectId

from app.config import get_settings

settings = get_settings()

USERS_COLLECTION = "users"
PLAYERS_COLLECTION = "players"
STAFF_COLLECTION = "staff"
TEAMS_COLLECTION = "teams"
TOURNAMENTS_COLLECTION = "tournaments"
GAMES_COLLECTION = "games"
GAME_CALLS_COLLECTION = "game_calls"
GROUPS_COLLECTION = "groups"
GOALS_COLLECTION = "goals"
CARDS_COLLECTION = "cards"
GAME_DAYS_COLLECTION = "game_days"


class Database:
    _instance: "Database | None" = None
    _client: Optional[AsyncMongoClient] = None
    _db: Optional[Any] = None
    _gridfs: Optional[AsyncGridFS] = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def db(self) -> Any:
        if self._db is None:
            raise RuntimeError(
                "Database not initialized. Did you forget to start the server?"
            )
        return self._db

    @property
    def gridfs(self) -> AsyncGridFS:
        if self._gridfs is None:
            self._gridfs = AsyncGridFS(self._db)
        return self._gridfs

    async def connect(self):
        self._client = AsyncMongoClient(settings.db_connection_string)
        self._db = self._client[settings.database_name]
        await self._create_collections()
        await self._create_indexes()

    async def close(self):
        if self._client:
            await self._client.aclose()

    async def _create_collections(self):
        existing = await self._db.list_collection_names()  # type: ignore[union-attr]
        for coll in [
            USERS_COLLECTION,
            PLAYERS_COLLECTION,
            STAFF_COLLECTION,
            TEAMS_COLLECTION,
            TOURNAMENTS_COLLECTION,
            GAMES_COLLECTION,
            GAME_CALLS_COLLECTION,
            GROUPS_COLLECTION,
            GOALS_COLLECTION,
            CARDS_COLLECTION,
            GAME_DAYS_COLLECTION,
        ]:
            if coll not in existing:
                await self._db.create_collection(coll)  # type: ignore[union-attr]

    async def _create_indexes(self):
        await self._db[CARDS_COLLECTION].create_index(  # type: ignore[index]
            [("tournament", 1), ("player_id", 1), ("team_id", 1), ("game", -1)]
        )
        await self._db[GAMES_COLLECTION].create_index(  # type: ignore[index]
            [("tournament", 1), ("status", 1), ("scheduled_date", -1)]
        )
        await self._db[GAME_CALLS_COLLECTION].create_index([("game", 1), ("team", 1)])  # type: ignore[index]
        await self._db[GOALS_COLLECTION].create_index(  # type: ignore[index]
            [("tournament", 1), ("player", 1)]
        )
        await self._db[GROUPS_COLLECTION].create_index([("tournament", 1)])  # type: ignore[index]
        await self._db[TEAMS_COLLECTION].create_index([("tournament", 1)])  # type: ignore[index]

    async def upload_file(
        self, filename: str, content_type: str, file_data: bytes
    ) -> str:
        file_id = await self.gridfs.put(
            file_data,
            filename=filename,
            content_type=content_type,
            upload_date=datetime.utcnow(),
        )
        return str(file_id)


db = Database()
