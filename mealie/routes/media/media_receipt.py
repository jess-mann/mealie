from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.core.config import get_app_dirs

router = APIRouter(prefix="/households/receipts")


@router.get("/{receipt_id}/image/{file_name}")
async def get_receipt_image(receipt_id: UUID4, file_name: str):
    if "/" in file_name or "\\" in file_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    receipt_dir = get_app_dirs().DATA_DIR.joinpath("receipts")
    receipt_image = next(receipt_dir.glob(f"*/*/{receipt_id}/{file_name}"), None)

    if receipt_image is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    resolved = receipt_image.resolve()
    if not resolved.is_relative_to(receipt_dir.resolve()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    return FileResponse(resolved, headers={"X-Content-Type-Options": "nosniff"})
