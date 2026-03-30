from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
import httpx

from open_webui.utils.auth import get_current_user
from open_webui.env import GENOMAIN_KLARTEXT_DOWNLOAD_BASEURL, GENOMAIN_KLARTEXT_API_KEY

router = APIRouter()


@router.get("/files/{document_id}/download")
async def proxy_klartext_download(
    document_id: int,
    request: Request,
):
    auth_header = request.headers.get("Authorization")
    headers = {
        "x-data-platform-application-key": GENOMAIN_KLARTEXT_API_KEY,
    }
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{GENOMAIN_KLARTEXT_DOWNLOAD_BASEURL}/files/{document_id}/download",
            headers=headers,
        )
        resp.raise_for_status()

    return StreamingResponse(
        resp.aiter_bytes(),
        media_type=resp.headers.get("content-type", "application/octet-stream"),
        headers={
            "content-disposition": resp.headers.get("content-disposition", "attachment"),
            "Access-Control-Expose-Headers": "content-disposition",
        },
    )
