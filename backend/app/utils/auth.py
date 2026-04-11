import logging
from fastapi import HTTPException, status, Request
from app.utils import decode_token
from app.config import get_settings
from app.schemas.schemas import UserRoles
from database import db, USERS_COLLECTION

logger = logging.getLogger()
settings = get_settings()
ADMIN_USERNAME = "admin"
COOKIE_NAME = "auth_token"


def get_user_from_token(token: str) -> dict | None:
    payload = decode_token(token, settings.jwt_secret)
    if not payload:
        return None
    return {"username": payload.get("sub"), "user_id": payload.get("user_id")}


async def get_user_from_db(username: str) -> dict | None:
    user = await db.db[USERS_COLLECTION].find_one({"username": username})
    if not user:
        return None
    return {
        "username": user.get("username"),
        "roles": user.get("roles", []),
        "assigned_games": user.get("assigned_games", []),
        "assigned_games_for_calls": user.get("assigned_games_for_calls", []),
    }


async def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Não autenticado"},
        )

    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token inválido ou expirado"},
        )

    logger.info(f"[{user['username']}] Authenticated")
    return user


async def get_admin_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Não autenticado"},
        )

    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token inválido ou expirado"},
        )

    logger.info(f"[{user['username']}] Admin authentication attempt")
    if user["username"] != ADMIN_USERNAME:
        logger.warning(f"[{user['username']}] Admin access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Apenas administradores podem executar esta ação"},
        )
    return user


def require_auth(request: Request):
    return get_current_user


async def require_role(role: str, request: Request):
    user = await get_current_user(request)
    if user["username"] == ADMIN_USERNAME:
        return user

    db_user = await get_user_from_db(user["username"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Utilizador não encontrado"},
        )

    if role in db_user.get("roles", []):
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": f"Sem permissão para esta ação. Função requerida: {role}"},
    )


async def require_manage_players(request: Request):
    return await require_role(UserRoles.MANAGE_PLAYERS, request)


async def require_manage_games(request: Request):
    return await require_role(UserRoles.MANAGE_GAMES, request)


async def require_manage_game_events(request: Request):
    return await require_role(UserRoles.MANAGE_GAME_EVENTS, request)


async def require_game_access(game_id: str, request: Request):
    user = await get_current_user(request)
    if user["username"] == ADMIN_USERNAME:
        return user

    db_user = await get_user_from_db(user["username"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Utilizador não encontrado"},
        )

    if UserRoles.MANAGE_GAME_EVENTS not in db_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Sem permissão para gerir eventos de jogos"},
        )

    if game_id in db_user.get("assigned_games", []):
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "Não tem acesso a este jogo"},
    )


async def require_call_access(game_id: str, request: Request):
    """Require fill_game_calls role AND game in assigned_games_for_calls"""
    user = await get_current_user(request)
    if user["username"] == ADMIN_USERNAME:
        return user

    db_user = await get_user_from_db(user["username"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Utilizador não encontrado"},
        )

    if UserRoles.FILL_GAME_CALLS not in db_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Sem permissão para gerir chamadas de jogos"},
        )

    if game_id in db_user.get("assigned_games_for_calls", []):
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "Não tem acesso a este jogo"},
    )


async def require_start_game(request: Request):
    """Require manage_games OR manage_game_events role"""
    user = await get_current_user(request)
    if user["username"] == ADMIN_USERNAME:
        return user

    db_user = await get_user_from_db(user["username"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Utilizador não encontrado"},
        )

    user_roles = db_user.get("roles", [])
    if (
        UserRoles.MANAGE_GAMES in user_roles
        or UserRoles.MANAGE_GAME_EVENTS in user_roles
    ):
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": "Sem permissão para iniciar jogos"},
    )
