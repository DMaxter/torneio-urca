from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from app.db.database import db, USERS_COLLECTION
from app.models.models import User
from app.schemas.schemas import CreateUserDto, UserDto
from app.error import Error

router = APIRouter(prefix="/users", tags=["Users"])


def user_to_dto(user: dict) -> UserDto:
    return UserDto(
        id=str(user["_id"]),
        name=user["name"],
        gender=user["gender"],
        birth_date=user["birth_date"],
        address=user.get("address"),
        place_of_birth=user.get("place_of_birth"),
        fiscal_number=user["fiscal_number"],
        confirmed=user.get("confirmed", False),
        roles=user["roles"],
    )


@router.post("", response_model=UserDto, status_code=201)
async def add_user(user: CreateUserDto):
    user_dict = user.model_dump()
    result = await db[USERS_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    return user_to_dto(user_dict)


@router.get("", response_model=List[UserDto])
async def get_users():
    users = await db[USERS_COLLECTION].find().to_list(1000)
    return [user_to_dto(user) for user in users]


async def get_user(user_id: str) -> dict:
    try:
        user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise Error.invalid_id("user")
    if not user:
        raise Error.not_found("User")
    return user


async def get_player(player_id: str) -> dict:
    from app.models.models import Role

    user = await get_user(player_id)
    if Role.Player not in user.get("roles", []):
        raise Error.user_not_player()
    return user
