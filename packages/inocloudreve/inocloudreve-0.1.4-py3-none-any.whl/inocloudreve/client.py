import httpx

from .site import ping as _ping

from .session import password_sign_in as _password_sign_in
from .session import refresh_token as _refresh_token
from .session import generate_token as _generate_token
from .session import decode_token as _decode_token

from .file import get_file_info as _get_file_info
from .file import create_download_url as _create_download_url
from .file import get_download_url as _get_download_url
from .file import update_file_content as _update_file_content
from .file import list_files as _list_files

from .file import delete_file as _delete_file
from .file import force_unlock as _force_unlock
from .file import get_last_folder_or_file as _get_last_folder_or_file

from .upload import create_upload_session as _create_upload_session
from .upload import delete_upload_session as _delete_upload_session

from .callback import complete_s3_upload as _complete_s3_upload

from .utils import is_token_valid as _is_token_valid
from .utils import validate_token as _validate_token
from .utils import save_url_as_file as _save_url_as_file
from .utils import read_file_as_bytes as _read_file_as_bytes
from .utils import get_headers as _get_headers

from .utils import upload_parts_via_presigned_urls as _upload_parts_via_presigned_urls
from .utils import complete_upload_via_complete_url as _complete_upload_via_complete_url
from .utils import upload_file as _upload_file

class CloudreveClient:
    def __init__(self):
        self.base_url = None
        self.conn = None
        self.timeout = httpx.Timeout(600, read=600, write=600)
        self.email = None
        self.password = None
        self.user_info= None
        self.token = None
        self.b2_access_key_id = None
        self.b2_access_key_secret = None
        self.b2_region = None
        self.b2_bucket_name = None

    def init(self, base_url: str, b2_access_key_id: str = "", b2_access_key_secret: str = "", b2_region: str = "us-west-004", b2_bucket_name: str = "InoDrive"):
        self.base_url = base_url.rstrip('/')
        self.conn = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        self.b2_access_key_id = b2_access_key_id
        self.b2_access_key_secret = b2_access_key_secret
        self.b2_region = b2_region
        self.b2_bucket_name = b2_bucket_name

    ping = _ping

    password_sign_in = _password_sign_in
    refresh_token = _refresh_token
    generate_token = _generate_token
    decode_token = _decode_token

    list_files = _list_files
    get_file_info = _get_file_info
    create_download_url = _create_download_url
    get_download_url = _get_download_url
    update_file_content = _update_file_content
    delete_file = _delete_file
    force_unlock = _force_unlock
    get_last_folder_or_file = _get_last_folder_or_file

    create_upload_session = _create_upload_session
    delete_upload_session = _delete_upload_session

    complete_s3_upload = _complete_s3_upload

    is_token_valid = _is_token_valid
    validate_token = _validate_token
    save_url_as_file = _save_url_as_file
    read_file_as_bytes = _read_file_as_bytes
    get_headers = _get_headers

    upload_parts_via_presigned_urls = _upload_parts_via_presigned_urls
    complete_upload_via_complete_url = _complete_upload_via_complete_url
    upload_file = _upload_file

    async def close(self):
        await self.conn.aclose()