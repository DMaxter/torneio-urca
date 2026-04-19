from typing import List
import bcrypt
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, USERS_COLLECTION
from app.schemas.schemas import (
    CreateUserDto,
    UserDto,
    ChangePasswordDto,
    UpdateUserRolesDto,
    AssignUserGamesDto,
    AssignUserGamesForCallsDto,
    UserRoles,
)
from app.error import Error
from app.utils.auth import get_current_user, get_admin_user, ADMIN_USERNAME
from app.utils import get_logger

router = APIRouter(prefix="/users", tags=["Users"])

ADMIN_PASSWORD = "admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def user_to_dto(user: dict) -> UserDto:
    return UserDto(
        id=str(user["_id"]),
        username=user["username"],
        roles=user.get("roles", []),
        assigned_games=user.get("assigned_games", []),
        assigned_games_for_calls=user.get("assigned_games_for_calls", []),
    )


@router.post("", response_model=UserDto, status_code=201)
async def add_user(user: CreateUserDto, current_user=Depends(get_admin_user)):
    get_logger().info(f"[{current_user['username']}] Creating user '{user.username}'")
    existing = await db.db[USERS_COLLECTION].find_one({"username": user.username})
    if existing:
        get_logger().warning(f"User '{user.username}' already exists")
        raise Error.conflict("Já existe um utilizador com este nome")
    user_dict = {"username": user.username, "password": hash_password(user.password)}
    result = await db.db[USERS_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    get_logger().info(
        f"[{current_user['username']}] User '{user.username}' created successfully"
    )
    return user_to_dto(user_dict)


@router.get("", response_model=List[UserDto])
async def get_users(current_user=Depends(get_current_user)):
    get_logger().info(f"[{current_user['username']}] Retrieving all users")
    users = await db.db[USERS_COLLECTION].find().to_list(1000)
    get_logger().info(f"[{current_user['username']}] Retrieved {len(users)} users")
    return [user_to_dto(user) for user in users]


@router.patch("/{user_id}/password", response_model=UserDto)
async def change_password(
    user_id: str,
    password_data: ChangePasswordDto,
    current_user=Depends(get_current_user),
):
    user = await get_user(user_id)
    get_logger().info(
        f"[{current_user['username']}] Changing password for user '{user['username']}'"
    )
    if not verify_password(password_data.current_password, user["password"]):
        get_logger().warning(f"Invalid current password for user '{user['username']}'")
        raise Error.unauthorized("Palavra-passe atual incorreta")
    await db.db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hash_password(password_data.new_password)}},
    )
    get_logger().info(f"Password changed successfully for user '{user['username']}'")
    return user_to_dto(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, current_user=Depends(get_admin_user)):
    user = await get_user(user_id)
    get_logger().info(
        f"[{current_user['username']}] Deleting user '{user['username']}'"
    )
    await db.db[USERS_COLLECTION].delete_one({"_id": ObjectId(user_id)})
    get_logger().info(f"User '{user['username']}' deleted successfully")


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
            {
                "username": ADMIN_USERNAME,
                "password": hash_password(ADMIN_PASSWORD),
                "roles": UserRoles.ALL,
                "assigned_games": [],
            }
        )
        get_logger().info(f"Default admin user '{ADMIN_USERNAME}' created")
    else:
        get_logger().info(f"Admin user '{ADMIN_USERNAME}' already exists")


@router.patch("/{user_id}/roles", response_model=UserDto)
async def update_user_roles(
    user_id: str,
    roles_data: UpdateUserRolesDto,
    current_user=Depends(get_admin_user),
):
    user = await get_user(user_id)
    get_logger().info(
        f"[{current_user['username']}] Updating roles for user '{user['username']}'"
    )

    for role in roles_data.roles:
        if role not in UserRoles.ALL:
            raise Error.bad_request(f"Função inválida: {role}")

    await db.db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"roles": roles_data.roles}},
    )
    updated_user = await get_user(user_id)
    get_logger().info(f"Roles updated successfully for user '{user['username']}'")
    return user_to_dto(updated_user)


@router.patch("/{user_id}/games", response_model=UserDto)
async def assign_user_games(
    user_id: str,
    games_data: AssignUserGamesDto,
    current_user=Depends(get_admin_user),
):
    user = await get_user(user_id)
    get_logger().info(
        f"[{current_user['username']}] Assigning games to user '{user['username']}'"
    )

    await db.db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"assigned_games": games_data.assigned_games}},
    )
    updated_user = await get_user(user_id)
    get_logger().info(f"Games assigned successfully for user '{user['username']}'")
    return user_to_dto(updated_user)


@router.patch("/{user_id}/games/calls", response_model=UserDto)
async def assign_user_games_for_calls(
    user_id: str,
    games_data: AssignUserGamesForCallsDto,
    current_user=Depends(get_admin_user),
):
    user = await get_user(user_id)
    get_logger().info(
        f"[{current_user['username']}] Assigning games for calls to user '{user['username']}'"
    )

    await db.db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"assigned_games_for_calls": games_data.assigned_games_for_calls}},
    )
    updated_user = await get_user(user_id)
    get_logger().info(
        f"Games for calls assigned successfully for user '{user['username']}'"
    )
    return user_to_dto(updated_user)
