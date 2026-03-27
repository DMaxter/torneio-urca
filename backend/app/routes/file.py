from bson import ObjectId
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from database import db
from app.error import Error
from app.utils import get_logger

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{file_id}")
async def get_file(file_id: str):
    """Download a file by its ID."""
    get_logger().info(f"Downloading file '{file_id}'")
    if not file_id or file_id == "null" or file_id == "undefined":
        get_logger().error(f"Invalid file_id received: '{file_id}'")
        raise Error.invalid_id("ficheiro")
    try:
        file_obj = await db.gridfs.get(ObjectId(file_id))
    except Exception as e:
        get_logger().error(f"Failed to download file '{file_id}': {e}")
        raise Error.invalid_id("ficheiro")
    if not file_obj:
        raise Error.not_found("Ficheiro")

    async def file_iterator():
        while True:
            chunk = await file_obj.read(4096)
            if not chunk:
                break
            yield chunk

    content_type = file_obj.content_type or "application/octet-stream"
    filename = file_obj.filename or "file"

    return StreamingResponse(
        file_iterator(),
        media_type=content_type,
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )
