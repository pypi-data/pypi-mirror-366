import os
import httpx
import aiofiles

async def save_url_as_file(
    self,
    url: str,
    save_dir: str,
    filename: str,
    extension: str,
    overwrite: bool = True
) -> dict:
    """
    Download a file from `url` and save it to `save_dir/filename+extension`.

    Args:
        self: CloudreveClient instance
        url: the download URL (string)
        save_dir: directory path to save the file (string)
        filename: base name for the saved file (string)
        extension: file extension including the dot, e.g. ".zip" or ".png" (string)
        overwrite: if False and file exists, abort with error (bool, default True)

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str,
            "code": int | None,
            "path": str  # full path to the saved file
        }
    """

    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{filename}{extension}")

    if not overwrite and os.path.exists(file_path):
        return {
            "success": False,
            "status_code": None,
            "code": None,
            "msg": f"File already exists at {file_path}",
            "path": file_path
        }

    try:
        resp = await self.conn.get(url)
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}",
            "path": ""
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}",
            "path": ""
        }

    content = resp.content
    if not content:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": "Empty response body",
            "path": ""
        }

    ct = resp.headers.get("Content-Type", "")
    if not ct.startswith("application/") and not ct.startswith("image/") and not ct.startswith(
            "application/octet-stream"):
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": f"Unexpected content-type: {ct}",
            "path": ""
        }

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(resp.content)
    except OSError as exc:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": f"File write error: {exc}",
            "path": ""
        }

    return {
        "success": True,
        "status_code": resp.status_code,
        "msg": "",
        "path": file_path
    }


async def read_file_as_bytes(self, path: str) -> dict:
    """
    Read a file from disk and return its bytes and size.

    Args:
        self: CloudreveClient instance
        path: path to the file as a string

    Returns:
        {
            "success": bool,
            "msg": str,
            "data": bytes,
            "size": int
        }
    """
    try:
        async with aiofiles.open(path, "rb") as f:
            data = await f.read()
        return {
            "success": True,
            "msg": "",
            "data": data,
            "size": len(data),
        }
    except Exception as exc:
        return {
            "success": False,
            "msg": f"Error reading file: {exc}",
            "data": b"",
            "size": 0,
        }
