from pymongo import AsyncMongoClient

from app.config import get_settings

settings = get_settings()

client: AsyncMongoClient = None
db = None

USERS_COLLECTION = "users"
TEAMS_COLLECTION = "teams"
TOURNAMENTS_COLLECTION = "tournaments"
GAMES_COLLECTION = "games"
GAME_CALLS_COLLECTION = "game_calls"
GROUPS_COLLECTION = "groups"
GOALS_COLLECTION = "goals"
CARDS_COLLECTION = "cards"


async def connect_db():
    global client, db
    client = AsyncMongoClient(settings.db_connection_string)
    db = client[settings.database_name]
    await create_collections()
    await create_indexes()


async def close_db():
    global client
    if client:
        await client.aclose()


async def create_collections():
    for coll in [
        USERS_COLLECTION,
        TEAMS_COLLECTION,
        TOURNAMENTS_COLLECTION,
        GAMES_COLLECTION,
        GAME_CALLS_COLLECTION,
        GROUPS_COLLECTION,
        GOALS_COLLECTION,
        CARDS_COLLECTION,
    ]:
        await db.create_collection(coll)


async def create_indexes():
    await db[CARDS_COLLECTION].create_index(
        [("tournament", 1), ("player_id", 1), ("team_id", 1), ("game", -1)]
    )
    await db[GAMES_COLLECTION].create_index(
        [("tournament", 1), ("status", 1), ("scheduled_date", -1)]
    )
    await db[GAME_CALLS_COLLECTION].create_index([("game", 1), ("team", 1)])
    await db[GOALS_COLLECTION].create_index([("tournament", 1), ("player", 1)])
    await db[GROUPS_COLLECTION].create_index([("tournament", 1)])
    await db[TEAMS_COLLECTION].create_index([("tournament", 1)])
