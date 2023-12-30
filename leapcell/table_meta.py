from typing import Dict
from leapcell.field_meta import FieldMeta
from leapcell.http_client import HTTPClient
from leapcell.const import TableFieldType
import json


class TableMeta():
    """Leapcell Table Meta Class
    """
    def __init__(self,
                 resource: str,
                 table_id: str,
                 requster: HTTPClient,
                 field_metas: Dict[str, FieldMeta],
                 field_name_type: TableFieldType) -> None:
        self._requster = requster
        self._resource = resource
        self._table_id = table_id
        self._field_metas = field_metas
        self._display_field_metas = {
            item.name: item for item in field_metas.values()}
        self._field_name_type = field_name_type

    @property
    def requster(self):
        return self._requster

    @property
    def resource(self):
        return self._resource

    @property
    def table_id(self):
        return self._table_id

    @property
    def field_metas(self):
        if self._field_name_type == TableFieldType.ID:
            return self._field_metas
        elif self._field_name_type == TableFieldType.NAME:
            return self._display_field_metas
        return self._field_metas
    
    @property
    def field_id_metas(self):
        return self._field_metas

    @property
    def display_field_metas(self):
        return self._display_field_metas

    @property
    def field_name_type(self):
        return self._field_name_type

    def __str__(self) -> str:
        return "<repo: {}, table: {}>".format(
            self._resource, self.table_id)

    def __repr__(self) -> str:
        return json.dumps(self.toJSON())
    
    def todict(self) -> Dict[str, FieldMeta]:
        return {k:v for k,v in self.field_metas.items()}
    

    def toJSON(self):
        return {
            "resource": self._resource,
            "table_id": self._table_id,
            "fields": self.todict(),
        }
    
    def tojson(self):
        return self.toJSON()