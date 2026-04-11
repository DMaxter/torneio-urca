from bson import ObjectId
from database import db
from app.error import Error

async def get_entity_or_404(collection_name: str, entity_id: str, label: str) -> dict:
    """"
    Retrieve a MongoDB entity by its string ObjectId, throwing standardized HTTP Exceptions
    if the ID format is invalid or the entity cannot be found.
    """
    try:
        obj_id = ObjectId(entity_id)
    except Exception:
        raise Error.invalid_id(label.lower())
        
    entity = await db.db[collection_name].find_one({"_id": obj_id})
    if not entity:
        raise Error.not_found(label.capitalize())
        
    return entity
