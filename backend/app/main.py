from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from app.routes.user import router as user_router
from app.routes.player import router as player_router
from app.routes.tournament import router as tournament_router
from app.routes.team import router as team_router
from app.routes.group import router as group_router
from app.routes.game import router as game_router
from app.routes.goal import router as goal_router
from app.routes.card import router as card_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.close()


app = FastAPI(title="URCA Tournament API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = FastAPI()

api_router.include_router(user_router)
api_router.include_router(player_router)
api_router.include_router(tournament_router)
api_router.include_router(team_router)
api_router.include_router(group_router)
api_router.include_router(game_router)
api_router.include_router(goal_router)
api_router.include_router(card_router)

app.mount("/api", api_router)


@app.get("/")
async def root():
    return {"message": "PM Tournament API"}
