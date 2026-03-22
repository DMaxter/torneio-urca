import logging
from typing import List
import bcrypt
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, USERS_COLLECTION
from app.schemas.schemas import CreateUserDto, UserDto, ChangePasswordDto
from app.error import Error
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def user_to_dto(user: dict) -> UserDto:
    return UserDto(
        id=str(user["_id"]),
        username=user["username"],
    )


@router.post("", response_model=UserDto, status_code=201)
async def add_user(user: CreateUserDto, current_user=Depends(get_current_user)):
    logger.info(f"[{current_user['username']}] Creating user: {user.username}")
    existing = await db.db[USERS_COLLECTION].find_one({"username": user.username})
    if existing:
        logger.warning(f"User already exists: {user.username}")
        raise Error.conflict("Já existe um utilizador com este nome")
    user_dict = {"username": user.username, "password": hash_password(user.password)}
    result = await db.db[USERS_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    logger.info(f"User created: {user.username}")
    return user_to_dto(user_dict)


@router.get("", response_model=List[UserDto])
async def get_users(current_user=Depends(get_current_user)):
    users = await db.db[USERS_COLLECTION].find().to_list(1000)
    logger.info(f"[{current_user['username']}] Retrieved {len(users)} users")
    return [user_to_dto(user) for user in users]


@router.patch("/{user_id}/password", response_model=UserDto)
async def change_password(
    user_id: str,
    password_data: ChangePasswordDto,
    current_user=Depends(get_current_user),
):
    user = await get_user(user_id)
    logger.info(
        f"[{current_user['username']}] Password change attempt for user: {user['username']}"
    )
    if not verify_password(password_data.current_password, user["password"]):
        logger.warning(f"Invalid current password for user: {user['username']}")
        raise Error.unauthorized("Palavra-passe atual incorreta")
    await db.db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hash_password(password_data.new_password)}},
    )
    logger.info(f"Password changed for user: {user['username']}")
    return user_to_dto(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    user = await get_user(user_id)
    if user["username"] == ADMIN_USERNAME:
        logger.warning(f"[{current_user['username']}] Attempt to delete admin user")
        raise Error.bad_request("Não é possível eliminar o utilizador admin")
    await db.db[USERS_COLLECTION].delete_one({"_id": ObjectId(user_id)})
    logger.info(f"User deleted: {user['username']}")


async def get_user(user_id: str) -> dict:
    try:
        user = await db.db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise Error.invalid_id("user")
    if not user:
        raise Error.not_found("User")
    return user


async def create_default_admin():
    existing = await db.db[USERS_COLLECTION].find_one({"username": ADMIN_USERNAME})
    if not existing:
        await db.db[USERS_COLLECTION].insert_one(
            {"username": ADMIN_USERNAME, "password": hash_password(ADMIN_PASSWORD)}
        )
        logger.info(f"Default admin user '{ADMIN_USERNAME}' created")
    else:
        logger.info(f"Admin user '{ADMIN_USERNAME}' already exists")
