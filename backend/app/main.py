from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import connect_db, close_db
from app.routes.user import router as user_router
from app.routes.tournament import router as tournament_router
from app.routes.team import router as team_router
from app.routes.group import router as group_router
from app.routes.game import router as game_router
from app.routes.goal import router as goal_router
from app.routes.card import router as card_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="PM Tournament API", lifespan=lifespan)

app.include_router(user_router)
app.include_router(tournament_router)
app.include_router(team_router)
app.include_router(group_router)
app.include_router(game_router)
app.include_router(goal_router)
app.include_router(card_router)


@app.get("/")
async def root():
    return {"message": "PM Tournament API"}
