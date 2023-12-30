from typing import Dict, Union, Any, Optional
from leapcell.table_meta import TableMeta
from leapcell.http_client import HTTPClient
from leapcell.const import TableFieldType
import json


class Record:
    """Leapcell Record Instance

    Raises:
        KeyError: _description_

    Returns:
        _type_: _description_
    """

    _data: Dict[str, Any]
    _record_id: Optional[str]
    _table_meta: TableMeta
    _field_type: TableFieldType

    def __init__(
        self,
        requester: HTTPClient,
        record_id: Optional[str] = None,
        fields: Optional[Dict[str, Any]] = None,
        create_time: Optional[int] = None,
        update_time: Optional[int] = None,
    ) -> None:
        self._data = {}
        if fields is not None:
            for field, item in fields.items():
                self._data[field] = item
            self._record_id = record_id
        self._new_data: Dict[str, Any] = {}
        self._requester = requester
        self._create_time = create_time
        self._update_time = update_time
        return

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        data = value
        self._data[key] = data
        self._new_data[key] = data

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        del self._new_data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def data(self) -> Dict[str, Any]:
        return self._data

    def updated(self) -> Dict[str, Any]:
        return self._new_data

    @property
    def record_id(self) -> str | None:
        return self._record_id

    @property
    def id(self) -> Union[None, str]:
        return self._record_id

    @property
    def create_time(self) -> int | None:
        return self._create_time

    @property
    def update_time(self) -> int | None:
        return self._update_time

    def __repr__(self) -> str:
        return json.dumps(self.tojson(), ensure_ascii=False)

    def __str__(self) -> str:
        return "<record_id: {}, data: {}, create_time: {}, update_time: {}>".format(
            self._record_id, self._data, self._create_time, self._update_time
        )

    def save(self) -> None:
        update_values = dict()
        for field_name, value in self.updated().items():
            update_values[field_name] = value

        if not self._record_id:
            return

        self._requester.update_record(
            record_id=self._record_id,
            data={
                "fields": update_values,
            },
        )
        return

    def delete(self) -> None:
        self._requester.delete_record(
            record_id=self._record_id,
        )
        return

    def toJSON(self):
        return {
            "record_id": self._record_id,
            "data": self._data,
            "create_time": self._create_time,
            "update_time": self._update_time,
        }

    def tojson(self):
        return self.toJSON()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
