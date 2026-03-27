import logging
import traceback
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from database import db
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router, create_default_admin
from app.routes.player import router as player_router
from app.routes.tournament import router as tournament_router
from app.routes.team import router as team_router
from app.routes.group import router as group_router
from app.routes.game import router as game_router
from app.routes.goal import router as goal_router
from app.routes.card import router as card_router
from app.routes.file import router as file_router
from app.utils import REQUEST_ID, get_logger

LOGGING_FORMAT = (
    "%(asctime)s | %(levelname)s | [%(request_id)s] %(funcName)s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        REQUEST_ID.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await db.connect()
    await create_default_admin()
    logger.info("Startup complete")
    yield
    await db.close()
    logger.info("Shutdown complete")


app = FastAPI(title="URCA Tournament API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = FastAPI()
api_router.add_middleware(RequestIDMiddleware)


@api_router.exception_handler(HTTPException)
async def api_http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(detail)})


@api_router.exception_handler(RequestValidationError)
async def api_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": str(exc.errors())},
    )


@api_router.exception_handler(Exception)
async def api_general_exception_handler(request: Request, exc: Exception):
    log = get_logger()
    log.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Erro interno"},
    )


api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(player_router)
api_router.include_router(tournament_router)
api_router.include_router(team_router)
api_router.include_router(group_router)
api_router.include_router(game_router)
api_router.include_router(goal_router)
api_router.include_router(card_router)
api_router.include_router(file_router)

app.mount("/api", api_router)


@app.get("/")
async def root():
    return {"message": "PM Tournament API"}
