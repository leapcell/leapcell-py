from typing import List, Tuple, Dict, Union, Any
import base64
from leapcell.version import VERSION
import urllib.parse
from functools import reduce
from leapcell.utils import multi_urljoin, build_header
import json

FILE_UPLOAD_TIMEOUT = 600
FILE_UPLOAD_MAX_SIZE = 1024 * 1024 * 5



class LeapcellFile(object):
    def __init__(self, obj: Dict[str, Any]) -> None:
        id = obj.get("id", "")
        self._id = id
        link = obj.get("link", "")
        self._link = link
        meta = obj.get("meta", {})
        self._meta = meta

    def id(self) -> str:
        return self._id

    def link(self) -> str:
        return self._link

    def width(self) -> int:
        return self._meta.get("width", 0)

    def height(self) -> int:
        return self._meta.get("height", 0)

    def __getitem__(self, __name: str) -> Any:
        if __name == "id":
            return self.id()
        elif __name == "link":
            return self.link()
        elif __name == "width":
            return self.width()
        elif __name == "height":
            return self.height()
        else:
            raise KeyError("invalid key {}".format(__name))
        
    def __str__(self) -> str:
        return "LeapcellFile(id={}, link={}, width={}, height={})".format(
            self.id(), self.link(), self.width(), self.height()
        )

    def __repr__(self) -> str:
        return json.dumps(self.tojson(), ensure_ascii=False)

    def tojson(self):
        return {
            "id": self._id,
            "link":self._link,
            "meta": {
                "width": self._meta.get("width", 0),
                "height": self._meta.get("height", 0),
            }
        }