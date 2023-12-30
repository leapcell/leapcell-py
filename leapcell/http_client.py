from typing import Dict, Any, Union, List, Optional, Tuple
import os
from leapcell.exp import LeapcellException
from leapcell.version import VERSION
import urllib.parse
from functools import reduce
from leapcell.utils import multi_urljoin, build_header
from leapcell.file import LeapcellFile
from io import BytesIO
import urllib3
import json

try:
    from urllib.parse import urlparse, ParseResult
except ImportError:
    from urlparse import urlparse, ParseResult  # type: ignore

MAX_CONNECTION_RETRIES = 2
TIMEOUT_SECS = 600
FILE_UPLOAD_TIMEOUT = 600
FILE_UPLOAD_MAX_SIZE = 1024 * 1024 * 3


def endpoint(resource: str, table_id: str, version="v1", name_type="id") -> str:
    return multi_urljoin("/api/", version + "/", resource + "/", "/table/", table_id)


class HTTPClient(object):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        resource: str,
        table_id: str,
        version="v1",
        name_type="id",
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._url_prefix = endpoint(
            resource, table_id, version=version, name_type=name_type
        )
        self._table_id = table_id
        self._name_type = name_type

    def _request(
        self,
        url_path: str,
        method: str,
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[
            Dict[str, Tuple[str, BytesIO]] | List[Tuple[str, BytesIO]]
        ] = None,
    ) -> Any:
        # use urllib3 instead of requests to avoid requests dependency
        client = urllib3.PoolManager()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        url = urllib.parse.urljoin(self._base_url, url_path)
        if params is not None:
            query_string = urllib.parse.urlencode(params)
            url = url + "?" + query_string

        fields = None
        if isinstance(files, dict):
            fields = {
                "file": (files["file"][0], files["file"][1].getbuffer().tobytes()),
            }
        elif isinstance(files, list):
            fields = [("files", (f[0], f[1].getbuffer().tobytes())) for f in files]

        body = None
        if data is not None:
            body = json.dumps(data)

        headers = build_header(self._api_key)
        for k, v in build_header(self._api_key).items():
            headers[k] = v
        headers["Accept-Encoding"] = "gzip"

        try:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                timeout=TIMEOUT_SECS,
                retries=urllib3.Retry(MAX_CONNECTION_RETRIES, redirect=2),
                fields=fields,
                body=body,
            )
        except urllib3.exceptions.HTTPError as e:
            raise LeapcellException("http error, http error: {}".format(e))
        except urllib3.exceptions.TimeoutError as e:
            raise LeapcellException("timeout error, error: {}".format(e))
        except urllib3.exceptions.ConnectionError as e:
            raise LeapcellException("connection error, error: {}".format(e))
        except Exception as e:
            raise LeapcellException("unknown error, error: {}".format(e))

        try:
            body_json = json.loads(response.data)
        except ValueError:
            raise LeapcellException(
                "bad response, body is not json, http code {}, body: {}".format(
                    response.status, response.data
                )
            )
        if response.status != 200:
            raise LeapcellException(
                "bad request, http code {}, please check apitoken and params, error code: {}, hint: {}".format(
                    response.status,
                    body_json.get("code", ""),
                    body_json.get("error", ""),
                )
            )

        if "data" not in body_json:
            raise LeapcellException(
                "bad request, http code {}, please check apitoken and params, error code: {}, hint: {}".format(
                    response.status,
                    body_json.get("code", ""),
                    body_json.get("error", ""),
                )
            )
        return body_json["data"]

    def table_meta(self) -> Any:
        name_type = self._name_type
        return self._request(
            url_path="{}".format(self._url_prefix),
            method="GET",
            params={
                "name_type": name_type,
            },
        )

    def create_record(self, data: Dict) -> Dict[str, Any]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def create_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="GET",
            params={
                "name_type": self._name_type,
            },
        )

    def get_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/query".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def update_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="PUT",
            data=data,
        )

    def update_record(
        self, record_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="PUT",
            data=data,
        )

    def delete_records(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record".format(self._url_prefix),
            method="DELETE",
            data=data,
        )

    def delete_record(self, record_id) -> Optional[Dict[str, Any]]:
        return self._request(
            url_path="{}/record/{}".format(self._url_prefix, record_id),
            method="DELETE",
        )

    def aggr_record(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/metrics".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def search(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["name_type"] = self._name_type
        return self._request(
            url_path="{}/record/search".format(self._url_prefix),
            method="POST",
            data=data,
        )

    def upload(
        self, data: bytes | List[bytes], filename: Optional[str] = None
    ) -> LeapcellFile | List[LeapcellFile]:
        if isinstance(data, bytes):
            return self._upload(BytesIO(data), filename)
        elif isinstance(data, list):
            return self._upload_multi([BytesIO(d) for d in data])
        else:
            raise TypeError("invalid data {}, which should be byteIO".format(data))

    def _upload(self, file: BytesIO, filename: Optional[str]) -> LeapcellFile:
        if file.getbuffer().nbytes > FILE_UPLOAD_MAX_SIZE:
            raise LeapcellException("file is too large, file should be less than 5KB")
        if filename is not None:
            files = {"file": (filename, file)}
        else:
            files = {"file": ("file", file)}
        r = self._request(
            url_path="{}/{}".format(self._url_prefix, "upload"),
            method="POST",
            files=files,
        )
        response = r
        image_item = LeapcellFile(response.get("file", {}))
        return image_item

    def _upload_multi(self, files: List[BytesIO]) -> List[LeapcellFile]:
        upload_files = []
        for f in files:
            if f.getbuffer().nbytes > FILE_UPLOAD_MAX_SIZE:
                raise LeapcellException(
                    "file is too large, file should be less than 5KB"
                )
            upload_files.append(("files", (f)))
        r = self._request(
            url_path="{}/{}".format(self._url_prefix, "upload_multi"),
            method="POST",
            files=upload_files,
        )
        response = r
        image_item = [LeapcellFile(item) for item in response.get("files", [])]
        return image_item
