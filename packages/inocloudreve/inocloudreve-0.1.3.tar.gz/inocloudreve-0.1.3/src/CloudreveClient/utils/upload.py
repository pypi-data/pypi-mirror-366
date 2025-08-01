import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote

async def upload_parts_via_presigned_urls(
    self,
    upload_urls: list[str],
    parts: list[bytes]
) -> dict:
    """
    Upload each part of a multipart upload using the presigned URLs
    returned by Cloudreve’s create_upload_session.

    Args:
        self: CloudreveClient instance
        upload_urls: list of presigned PUT URLs (one per part)
        parts:       list of byte-chunks (same length as upload_urls)

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str
        }
    """
    last_status = None

    etags = []

    for idx, (url, chunk) in enumerate(zip(upload_urls, parts), start=1):
        try:
            print(f"Uploading part {idx}/{len(parts)} ({len(chunk)} bytes)…")
            headers = {"Content-Length": str(len(chunk))}
            resp = await self.conn.put(url, content=chunk, headers=headers)
            last_status = resp.status_code

            tag = resp.headers.get("ETag")
            etags.append(tag)

        except httpx.RequestError as exc:
            return {
                "success": False,
                "status_code": None,
                "msg": f"Request error: {exc}"
            }
        except httpx.HTTPStatusError as exc:
            return {
                "success": False,
                "status_code": exc.response.status_code,
                "msg": f"Part {idx} failed HTTP {exc.response.status_code}"
            }
        except httpx.ReadTimeout:
            return {
                "success": False,
                "status_code": None,
                "msg": f"Part {idx} timed out"
            }
        except Exception as exc:
            return {
                "success": False,
                "status_code": None,
                "msg": f"Part {idx} error: {exc!r}"
            }


    return {
        "success": True,
        "status_code": last_status,
        "msg": f"Uploaded {len(parts)} parts successfully",
        "etags": etags
    }

async def complete_upload_via_complete_url(
    self,
    complete_url: str,
    etags: list[str],
) -> dict:
    """
    Complete upload with complete url

    Args:
        self: CloudreveClient instance
        complete_url:
        etags:

    Returns:
        {
            "success": bool,
            "status_code": int | None,
            "msg": str
        }
    """
    S3_NS = "http://s3.amazonaws.com/doc/2006-03-01/"
    root = ET.Element("CompleteMultipartUpload", xmlns=S3_NS)

    for idx, tag in enumerate(etags, start=1):
        part = ET.SubElement(root, "Part")
        ET.SubElement(part, "ETag").text = tag
        ET.SubElement(part, "PartNumber").text = str(idx)
    xml_body = ET.tostring(root, encoding="utf-8", xml_declaration=False)

    try:
        resp = await self.conn.post(
            complete_url,
            headers={
                "Content-Type": "application/xml",
                "Content-Length": str(len(xml_body))
            },
            content=xml_body
        )
        resp.raise_for_status()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "status_code": None,
            "msg": f"Request error: {exc}"
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "status_code": exc.response.status_code,
            "msg": f"HTTP error: {exc.response.status_code}"
        }

    try:
        tree = ET.fromstring(resp.text)

        bucket = tree.find(f".//{{{S3_NS}}}Bucket").text
        etag_val = tree.find(f".//{{{S3_NS}}}ETag").text
        key = tree.find(f".//{{{S3_NS}}}Key").text
        location = tree.find(f".//{{{S3_NS}}}Location").text
    except Exception as exc:
        return {
            "success": False,
            "status_code": resp.status_code,
            "msg": f"Failed to parse XML response: {exc}",
            "bucket": "",
            "etag": "",
            "key": "",
            "location": ""
        }

    return {
        "success": True,
        "status_code": resp.status_code,
        "msg": "Upload completed successfully",
        "bucket": bucket,
        "etag": etag_val,
        "key": key,
        "location": location
    }

async def upload_file(
    self,
    local_path: str,
    remote_path: str,
    storage_policy: str
) -> dict:
    """
    Perform a full multipart upload of a local file to Cloudreve.

    Steps:
      1. Read the local file into bytes.
      2. Create an upload session on Cloudreve.
      3. Split the file into chunks.
      4. Upload each chunk via the presigned URLs.
      5. Complete the upload.

    Args:
        self: CloudreveClient instance
        local_path: path to the local file (string)
        remote_path: path under `cloudreve://my/` to save (e.g. "Spark/test/file.zip")
        storage_policy: storage policy ID (string, e.g. "O8cN")

    Returns:
        {
            "success": bool,
            "msg": str,
            "session": dict,        # the create_upload_session data
            "upload_parts": dict    # result of upload_parts_via_presigned_urls
        }
    """

    file_resp = await self.read_file_as_bytes(local_path)
    if not file_resp["success"]:
        return {
            "success": file_resp["success"],
            "msg": f"failed at reading the file",
            "file_resp": file_resp["msg"],
            "session_resp": "",
            "upload_parts_resp": "",
            "complete_upload_resp": "",
            "callback_resp": ""
        }

    total_size = file_resp["size"]
    session_resp = await self.create_upload_session(
        uri= remote_path,
        size=total_size,
        policy_id=storage_policy)
    if not session_resp["success"]:
        return {
            "success": session_resp["success"],
            "msg": "failed at creating the upload session",
            "file_resp": file_resp["msg"],
            "session_resp": session_resp["msg"],
            "upload_parts_resp": "",
            "complete_upload_resp": "",
            "callback_resp": ""
        }

    file_data = file_resp["data"]
    chunk_size = session_resp["chunk_size"]
    file_parts = [
        file_data[offset: min(offset + chunk_size, total_size)]
        for offset in range(0, total_size, chunk_size)
    ]

    upload_urls = session_resp["upload_urls"]
    upload_parts_resp = await self.upload_parts_via_presigned_urls(
        upload_urls=upload_urls,
        parts=file_parts
    )
    if not upload_parts_resp["success"]:
        return {
            "success": upload_parts_resp["success"],
            "msg": "failed at uploading the parts",
            "file_resp": file_resp["msg"],
            "session_resp": session_resp["msg"],
            "upload_parts_resp": upload_parts_resp["msg"],
            "complete_upload_resp": "",
            "callback_resp": ""
        }

    complete_url = session_resp["completeURL"]
    complete_upload_resp = await self.complete_upload_via_complete_url(
        complete_url= complete_url,
        etags=upload_parts_resp["etags"]
    )
    if not complete_upload_resp["success"]:
        return {
            "success": complete_upload_resp["success"],
            "msg": "failed at completing the upload",
            "file_resp": file_resp["msg"],
            "session_resp": session_resp["msg"],
            "upload_parts_resp": upload_parts_resp["msg"],
            "complete_upload_resp": complete_upload_resp["msg"],
            "callback_resp": ""
        }

    callback_resp = await self.complete_s3_upload(
        session_id=session_resp["session_id"],
        key_id=complete_upload_resp["key"],
    )
    if not callback_resp["success"]:
        return {
            "success": False,
            "msg": "Failed at callback",
            "file_resp": file_resp["msg"],
            "session_resp": session_resp["msg"],
            "upload_parts_resp": upload_parts_resp["msg"],
            "complete_upload_resp": complete_upload_resp["msg"],
            "callback_resp": callback_resp["msg"]
        }

    return {
        "success": True,
        "msg": "File uploaded successfully",
        "file_resp": file_resp["msg"],
        "session_resp": session_resp["msg"],
        "upload_parts_resp": upload_parts_resp["msg"],
        "complete_upload_resp": complete_upload_resp["msg"],
        "callback_resp": callback_resp["msg"]
    }