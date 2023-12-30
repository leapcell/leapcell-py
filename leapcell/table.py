from leapcell.const import TableFieldType
from leapcell.table_meta import TableMeta
from typing import Dict, Union, Any, List, Tuple, Optional
from leapcell.field_meta import FieldMeta
from leapcell.http_client import HTTPClient
from leapcell.field_item import FieldMgr, BaseItem
from leapcell.record import Record
from functools import reduce
from leapcell.file import LeapcellFile
import json

support_op = [
    "eq",
    "gt",
    "gte",
    "lt",
    "lte",
    "neq",
    "contain",
    "in",
    "not_in",
    "is_null",
    "not_null",
]


def is_list_of_strings(lst):
    return (
        bool(lst)
        and not isinstance(lst, str)
        and all(isinstance(elem, str) for elem in lst)
    )


class LeapcellFilter(object):
    def __init__(self, **args):
        type_ = args.get("type", "eq")
        self.filter = {"filter": {"type": type_}}

        if type_ in support_op:
            self.filter["filter"].update(
                {"field": args["field"], "value": args["value"]}
            )
        elif type_ == "and":
            self.filter["filter"].update({"fields": args["fields"]})
        elif type_ == "or":
            self.filter["filter"].update({"fields": args["fields"]})
        elif type_ == "not":
            self.filter["filter"].update({"fields": args["fields"]})
        else:
            raise KeyError("Filter type: {0} does not exist".format(type_))

    def __and__(self, x):
        if self.filter["filter"]["type"] == "and":
            self.filter["filter"]["fields"].append(x)
            return self
        return LeapcellFilter(type="and", fields=[self, x])

    def __or__(self, x):
        if self.filter["filter"]["type"] == "or":
            self.filter["filter"]["fields"].append(x)
            return self
        return LeapcellFilter(type="or", fields=[self, x])

    def __invert__(self, x):
        if self.filter["filter"]["type"] == "not":
            self.filter["filter"]["fields"].append(x)
            return self
        return LeapcellFilter(type="not", fields=[self, x])

    def __str__(self) -> str:
        return "<filter: {}>".format(self.filter)

    @staticmethod
    def build_filter(filter_obj):
        filter = filter_obj.filter["filter"]
        if filter["type"] in ["and", "or", "not"]:
            filter = filter.copy()  # make a copy so we don't overwrite `fields`
            filter["fields"] = [
                LeapcellFilter.build_filter(f) for f in filter["fields"]
            ]
        return filter


# leapcell tool class
class LeapcellOrder(object):
    def __init__(self, field: str, order: str = "desc") -> None:
        self._field = field
        self._order = order

    def __str__(self) -> str:
        return f"{self._field} {self._order}"

    def __repr__(self) -> str:
        return f"{self._field} {self._order}"

    def get_order(self) -> Tuple[str, str]:
        return (self._field, self._order)


class KaithQuery(object):
    """Leapcell Query class

    Args:
        object (_type_): _description_
    """

    def __init__(
        self,
        requester: HTTPClient,
        fields: List[str] = [],
        filter: Optional[LeapcellFilter] = None,
        orders: List[Tuple[str, str]] = [],
        offset: int = 0,
        limit: int = 20,
        aggr: Optional[str] = None,
    ) -> None:
        self.fields = fields
        self._filter = filter
        self._orders = orders
        self._offset = offset
        self._limit = limit
        self._aggr = aggr
        self._requester = requester

    def __str__(self) -> str:
        return "<filter: {}, orders: {}, offset: {}, limit: {}, aggr: {}>".format(
            self._filter,
            self._orders,
            self._offset,
            self._limit,
            self._aggr,
        )

    def where(self, filter: Optional[LeapcellFilter] = None):
        """where condition

        Args:
            filter (Optional[LeapcellFilter], optional): Filter condition. Defaults to None.

        Raises:
            TypeError: filter must be a LeapcellFilter object, you can use bracket to build a filter

        Returns:
            _type_: _description_
        """
        if isinstance(filter, bool):
            raise TypeError(
                "filter must be a LeapcellFilter object, you can use bracket to build a filter"
            )
        if not filter:
            raise TypeError(
                "filter must be a LeapcellFilter object, you can use bracket to build a filter"
            )
        elif self._filter is None:
            self._filter = filter
        else:
            self._filter = filter & self._filter
        return self

    def order_by(
        self,
        orders: List[Tuple[str, str] | LeapcellOrder]
        | LeapcellOrder
        | Tuple[str, str] = [],
    ):
        """order by

        Args:
            orders (List[Tuple[str, str]  |  LeapcellOrder] | LeapcellOrder | Tuple[str, str], optional): _description_. Defaults to [].

        Raises:
           ValueError: order_by must be a list of tuple (name, 'desc') or table[name].desc() or table[name].asc()

        Returns:
            _type_: _description_
        """
        if isinstance(orders, LeapcellOrder):
            self._orders.append(orders.get_order())
            return self
        if isinstance(orders, list) and len(orders) == 0:
            return self
        if (
            isinstance(orders, tuple)
            and len(orders) == 2
            and isinstance(orders[0], str)
            and isinstance(orders[1], str)
        ):
            self._orders.append(orders)
            return self

        for order in orders:
            if isinstance(order, tuple):
                self._orders.append(order)
            elif isinstance(order, LeapcellOrder):
                self._orders.append(order.get_order())
            else:
                raise ValueError(
                    "order_by must be a list of tuple (name, 'desc') or table[name].desc() or table[name].asc()"
                )
        return self

    def limit(self, limit: int = 50):
        """limit

        Args:
            limit (int, optional): _description_. Defaults to 50.

        Returns:
            _type_: _description_
        """
        self._limit = limit
        return self

    def take(self, limit: int = 50):
        return self.limit(limit)

    def skip(self, offset: int = 0):
        return self.offset(offset)

    def offset(self, offset: int = 0):
        """offset

        Args:
            offset (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        self._offset = offset
        return self

    def select(self, fields: List[str] = []):
        """field to select

        Args:
            fields (List[str], optional): _description_. Defaults to [].

        Returns:
            _type_: _description_
        """
        self.fields = fields
        return self

    def search(
        self,
        query: str,
        search_fields: List[str] = [],
        boost_fields: Dict[str, int] = {},
    ) -> List[Record]:
        """search records by keyword

        Args:
            query (str): search keyword
            fields (List[str], optional): search fields. Defaults to [].
            boost_fields (Dict[str, int], optional): boost fields. Defaults to {}.
        """

        resp = self._search(query, search_fields, boost_fields)
        if not resp or not resp["records"]:
            return []
        return [
            Record(
                requester=self._requester,
                record_id=record["record_id"],
                fields=record["fields"],
                create_time=record.get("create_time", None),
                update_time=record.get("update_time", None),
            )
            for record in resp["records"]
        ]

    def query(self):
        """execute query

        Returns:
            _type_: Record instance list
        """
        resp = self._query()
        if resp["records"] is None:
            return []
        return [
            Record(
                requester=self._requester,
                record_id=record["record_id"],
                fields=record["fields"],
                create_time=record.get("create_time", None),
                update_time=record.get("update_time", None),
            )
            for record in resp["records"]
        ]

    def first(self):
        """get the first record

        Returns:
            _type_: _description_
        """
        self._limit = 1
        resp = self._query()
        if resp["records"] is None:
            return None
        if len(resp["records"]) == 0:
            return None

        return Record(
            requester=self._requester,
            record_id=resp["records"][0]["record_id"],
            fields=resp["records"][0]["fields"],
            create_time=resp["records"][0].get("create_time", None),
            update_time=resp["records"][0].get("update_time", None),
        )

    def update(self, values: Dict[str, Any]):
        """execute update

        Args:
            values (Dict[str, Any]): _description_

        Returns:
            _type_: _description_
        """
        return self._update(values)

    def delete(self):
        """execute delete

        Returns:
            _type_: _description_
        """
        return self._delete()

    def count(self):
        """execute count

        Returns:
            _type_: _description_
        """
        return self._count()

    def _get_filter(self, filter: Union[LeapcellFilter, None] = None) -> Dict | None:
        query_filter: Optional[Dict] = None

        def gen_filter(f: Dict[str, Any]):
            op = None
            val = f["value"]
            if f["type"] == "gt":
                op = "gt"
            elif f["type"] == "gte":
                op = "gte"
            elif f["type"] == "lt":
                op = "lt"
            elif f["type"] == "lte":
                op = "lte"
            elif f["type"] == "neq":
                op = "neq"
            elif f["type"] == "eq":
                op = "eq"
            elif f["type"] == "in":
                op = "in"
            elif f["type"] == "not_in":
                op = "not_in"
            elif f["type"] == "not_null":
                op = "not_null"
            elif f["type"] == "is_null":
                op = "is_null"
            elif f["type"] == "contain":
                op = "contain"
            else:
                raise KeyError("Filter type: {0} does not exist".format(f["type"]))
            field = f["field"]
            return {
                "val": val,
                "op": op,
                "field": field,
            }

        if filter is not None and isinstance(filter, LeapcellFilter):
            fs = LeapcellFilter.build_filter(filter)
            if fs["type"] in ["and", "or", "not"]:
                filters = []
                for f in fs["fields"]:
                    fitem = gen_filter(f)

                    filters.append(fitem)
                query_filter = {
                    "filterType": fs["type"],
                    "filters": filters,
                }
            else:
                fitem = gen_filter(fs)
                query_filter = fitem
        elif isinstance(filter, dict):
            ff = self._condition2filter(filter)
            return self._get_filter(ff)

        return query_filter

    def _gen_order(self, orders: List[Tuple[str, str]]) -> List[Dict]:
        sortByCol = []
        if orders is not None:
            for order in orders:
                if not isinstance(order, tuple):
                    raise TypeError("order must be tuple, like [('view_id',)]")
                if len(order) > 2:
                    raise ValueError(
                        "invalid order, is should be like [('xx', 'desc')]"
                    )
                if len(order) == 2 and order[1] not in ["desc", "asc"]:
                    raise ValueError("invalid order type, should in ['desc', 'asc']")
                order_type = "DESC"
                if len(order) == 2 and order[1] == "asc":
                    order_type = "ASC"
                field_id = order[0]
                sortByCol.append({"field": field_id, "sortType": order_type})
        return sortByCol

    def _query(
        self,
    ) -> Dict | None:
        fields = self.fields
        filter = self._filter
        orders = self._orders
        offset = self._offset
        limit = self._limit
        aggr = self._aggr

        query_filter: Optional[Dict] = self._get_filter(filter)
        sortByCol = self._gen_order(orders)

        req: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "filter": query_filter,
        }
        if aggr:
            req["aggr"] = aggr
        if fields:
            req["fields"] = fields
        if sortByCol:
            req["orders"] = sortByCol

        resp = self._requester.get_records(req)

        return resp

    def _update(
        self,
        values: Dict[str, Any],
    ) -> Optional[int]:
        filter = self._filter
        record_values = dict()
        for key, value in values.items():
            record_values[key] = value
        query_filter: Optional[Dict] = self._get_filter(filter)

        resp = self._requester.update_records(
            {
                "filter": query_filter,
                "fields": record_values,  # data transform, like datetime to int
            }
        )

        if not resp:
            return None

        return resp["affect_count"]

    def _search(
        self,
        query: str,
        search_fields: List[str] = [],
        boost_fields: Dict[str, int] = {},
    ) -> Optional[Dict[str, Any]]:
        fields = self.fields
        filter = self._filter
        orders = self._orders
        offset = self._offset
        limit = self._limit

        query_filter: Optional[Dict] = self._get_filter(filter)
        sortByCol = self._gen_order(orders)

        req: Dict[str, Any] = {
            "query": query,
            "search_fields": search_fields,
        }
        if query_filter:
            req["filter"] = query_filter
        if sortByCol:
            req["orders"] = sortByCol
        if fields:
            req["fields"] = fields
        if offset:
            req["offset"] = offset
        if limit:
            req["limit"] = limit
        if boost_fields:
            req["boost_fields"] = boost_fields

        resp = self._requester.search(req)
        if not resp:
            return None

        return resp

    def _delete(
        self,
    ) -> Optional[int]:
        filter = self._filter

        query_filter: Optional[Dict] = self._get_filter(filter)

        resp = self._requester.delete_records(
            {
                "filter": query_filter,
            }
        )

        if not resp:
            return None

        return resp["affect_count"]

    def _count(
        self,
        distinct: Optional[bool] = None,
    ) -> Optional[int]:
        filter = self._filter

        query_filter: Optional[Dict] = self._get_filter(filter)

        params: Dict[str, Any] = {
            "filter": query_filter,
            "metric": {
                "field": "*",
                "aggr": "count",
            },
        }
        if distinct:
            params["metric"]["condition"] = "distinct"
        resp = self._requester.aggr_record(params)

        if not resp or not resp["metric"]:
            return None

        return resp["metric"]["value"]

    def _condition2filter(
        self, conditions: Optional[Dict[str, Any] | LeapcellFilter]
    ) -> Optional[LeapcellFilter]:
        filter: Optional[LeapcellFilter] = None
        if conditions is not None and isinstance(conditions, Dict):
            filters = [LeapcellField(field) == val for field, val in conditions.items()]
            filter = reduce(lambda x, y: x and y, filters)
        elif conditions is not None and isinstance(conditions, LeapcellFilter):
            filter = conditions
        return filter


class LeapcellField(object):
    """Leapcell Field class

    Args:
        object (_type_): _description_
    """

    def __init__(self, field: str):
        self.field = field

    def __eq__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="eq")

    def eq_(self, other):
        return self.__eq__(other)

    def __gt__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="gt")

    def gt_(self, other):
        return self.__gt__(other)

    def __ge__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="gte")

    def ge_(self, other):
        return self.__ge__(other)

    def __lt__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="lt")

    def lt_(self, other):
        return self.__lt__(other)

    def __le__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="lte")

    def le_(self, other):
        return self.__le__(other)

    def __ne__(self, other):
        return LeapcellFilter(field=self.field, value=other, type="neq")

    def neq_(self, other):
        return self.__ne__(other)

    def contain(self, other):
        return LeapcellFilter(field=self.field, value=other, type="contain")

    def __contains__(self, other):
        return self.contain(other)

    def in_(self, value: List[Any]):
        return LeapcellFilter(field=self.field, value=value, type="in")

    def not_in(self, value: List[Any]):
        return LeapcellFilter(field=self.field, value=value, type="not_in")

    def is_null(self):
        return LeapcellFilter(field=self.field, value=None, type="is_null")

    def not_null(self):
        return LeapcellFilter(field=self.field, value=None, type="not_null")

    # TODO: to complete these operations
    def order_by(self, order_type: str = "desc"):
        return LeapcellOrder(field=self.field, order=order_type)

    def desc(self):
        return LeapcellOrder(field=self.field, order="desc")

    def asc(self):
        return LeapcellOrder(field=self.field, order="asc")


class LeapcellTable(object):
    """Leapcell table instance

    Args:
        object (_type_): _description_
        resource (str): leapcell resource name, you can find it in leapcell with format leapcell.io/{username}/{repo_name}, resource all have the same format as {username}/{repo_name}
        token (str): leapcell token
        table_id (str): ltable id, you can find it in leapcell with format leapcell.io/{username}/{repo_name}/table/{table_id}, table_id all have the same format as {username}/{repo_name}/table/{table_id}
        base_url (str): leapcell base url, default is https://api.leapcell.io
        field_type (str): field_type is the type of the field, it can be "id" or "name". Defaults to "name". if it's "id", the field name will be "13145252145", "13145252147" ...; if it's "name", the field name will be "field-0", "field-1", "field-2", ...,
        version (str): leapcell api version, default is v1

    Raises:
        KeyError: if field not found in table, raise KeyError

    Returns:
        LeapcellTable: LeapcellTable instance
    """

    _field_name_type: TableFieldType

    def __init__(
        self,
        repository: str,
        api_key: str,
        table_id: str,
        base_url: str,
        name_type: str = "name",
        version: str = "v1",
    ) -> None:
        if name_type == "name":
            self._field_name_type = TableFieldType.NAME
        else:
            self._field_name_type = TableFieldType.ID
        self._resource = repository
        self._requster = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            resource=repository,
            table_id=table_id,
            version=version,
            name_type=name_type,
        )
        self._table_id = table_id

    def __repr__(self) -> str:
        return "table instance <table: {}, resource: {}>".format(
            self._table_id, self._resource
        )

    def __str__(self) -> str:
        return "table instance <table: {}, resource: {}>".format(
            self._table_id, self._resource
        )

    def _meta(self, table_id: str) -> TableMeta:
        # TODO: catch http bad status
        data = self._requster.table_meta()

        field_metas = {
            field_id: FieldMeta(field_info)
            for field_id, field_info in data["fields"].items()
        }

        return TableMeta(
            table_id=table_id,
            requster=self._requster,
            resource=self._resource,
            field_metas=field_metas,
            field_name_type=self._field_name_type,
        )

    def meta(self) -> TableMeta:
        """get table meta information, like fields

        Returns:
            TableMeta: table meta information
        """
        return self._meta(self._table_id)

    def create(
        self, record: Dict[str, Any], on_conflict: List[str] | str | None = None
    ) -> Record:
        """create single record

        Args:
            record (Dict[str, Any]): record information, key is field name, value is field value
            on_conflict (List[str] | str | None, optional): not create if the field value exist. Default None.

        Returns:
            Record: _description_
        """
        record_values = dict()
        for key, value in record.items():
            record_values[key] = value
        params: Dict[str, Any] = {
            "record": record_values,
        }
        if on_conflict:
            if isinstance(on_conflict, str):
                params["on_conflict"] = [on_conflict]
            elif isinstance(on_conflict, list):
                params["on_conflict"] = on_conflict
            params["action"] = "create_if_not_exists"

        data = self._requster.create_record(
            params,
        )
        new_record_data = data["record"]

        # TODO: add init value
        return Record(
            requester=self._requster,
            record_id=new_record_data["record_id"],
            fields=new_record_data["fields"],
            create_time=new_record_data.get("create_time", None),
            update_time=new_record_data.get("update_time", None),
        )

    def upsert(
        self, record: Dict[str, Any], on_conflict: List[str] | str | None = None
    ) -> Record:
        """upsert single record

        Args:
            record (Dict[str, Any]): record information
            on_conflict (List[str] | str | None, optional): not create if the field value exist. Default None.

        Raises:
            KeyError: field not found

        Returns:
            Record: Record instance
        """

        record_values = dict()
        for key, value in record.items():
            record_values[key] = value
        params: Dict[str, Any] = {
            "record": record_values,
        }
        if on_conflict:
            if isinstance(on_conflict, str):
                params["on_conflict"] = [on_conflict]
            elif isinstance(on_conflict, list):
                params["on_conflict"] = on_conflict
            params["action"] = "upsert"

        data = self._requster.create_record(
            params,
        )
        new_record_data = data["record"]

        # TODO: add init value
        return Record(
            requester=self._requster,
            record_id=new_record_data["record_id"],
            fields=new_record_data["fields"],
            create_time=new_record_data.get("create_time", None),
            update_time=new_record_data.get("update_time", None),
        )

    def bulk_upsert(
        self, records: List[Dict[str, Any]], on_conflict: List[str] | str | None = None
    ) -> Optional[List[Record]]:
        """bulk upsert records

        Args:
            records (List[Dict[str, Any]]): records information
            on_conflict (List[str] | str | None, optional): not create if the field value exist. Default None.

        Returns:
            Optional[List[Record]]: Record instance list
        """
        new_values = []
        for new_record in records:
            record_values = dict()
            for key, value in new_record.items():
                record_values[key] = value
            new_values.append(record_values)

        params: Dict[str, Any] = {
            "records": new_values,
        }
        if on_conflict:
            if isinstance(on_conflict, str):
                params["on_conflict"] = [on_conflict]
            elif is_list_of_strings(on_conflict):
                params["on_conflict"] = on_conflict
        data = self._requster.create_records(
            params,
        )

        if not data or not data["records"]:
            return None

        new_record_datas = data["records"]

        return [
            Record(
                record_id=new_record_data["record_id"],
                fields=new_record_data["fields"],
                requester=self._requster,
                create_time=new_record_data.get("create_time", None),
                update_time=new_record_data.get("update_time", None),
            )
            for new_record_data in new_record_datas
        ]

    def bulk_create(
        self, records: List[Dict[str, Any]], on_conflict: List[str] | str | None = None
    ) -> Optional[List[Record]]:
        """bulk create records

        Args:
            records (List[Dict[str, Any]]): records information
            on_conflict (List[str] | str | None, optional): not create if the field value exist. Default None.

        Raises:
            KeyError: field not found

        Returns:
            Optional[List[Record]]: Record instance list
        """
        new_values = []
        for new_record in records:
            record_values = dict()
            for key, value in new_record.items():
                record_values[key] = value
            new_values.append(record_values)

        params: Dict[str, Any] = {
            "records": new_values,
        }
        if on_conflict:
            if isinstance(on_conflict, str):
                on_conflict = [on_conflict]
            elif isinstance(on_conflict, list):
                params["on_conflict"] = on_conflict
        data = self._requster.create_records(
            params,
        )

        if not data or not data["records"]:
            return None

        new_record_datas = data["records"]

        return [
            Record(
                requester=self._requster,
                record_id=new_record_data["record_id"],
                fields=new_record_data["fields"],
                create_time=new_record_data.get("create_time", None),
                update_time=new_record_data.get("update_time", None),
            )
            for new_record_data in new_record_datas
        ]

    def _table_view2records(self, table_view: Dict[str, Any]) -> List[Record]:
        return [
            Record(
                requester=self._requster,
                record_id=record,
            )
            for record in table_view["records"]
        ]

    def get_by_id(
        self,
        id: str,
    ) -> Optional[Record]:
        """get record by id

        Args:
            id (str): record id

        Returns:
            Optional[Record]: Record instance
        """
        data = self._requster.get_record(
            record_id=id,
        )
        if not data or not data["record"]:
            return None

        return Record(
            requester=self._requster,
            record_id=data["record"]["record_id"],
            fields=data["record"]["fields"],
            create_time=data["record"].get("create_time", None),
            update_time=data["record"].get("update_time", None),
        )

    def get(
        self,
        conditions: Dict[str, Any],
        orders: List[Tuple[str, str]] = [],
    ) -> Optional[Record]:
        """get record by conditions

        Args:
            conditions (Dict[str, Any]): conditions
            orders (List[Tuple[str, str]], optional): order by. Defaults to [].

        Returns:
            Optional[Record]: Record instance list
        """
        where_conditions = [
            LeapcellField(field) == val for field, val in conditions.items()
        ]
        result = KaithQuery(
            self._requster,
            fields=[],
            filter=reduce(lambda x, y: x and y, where_conditions),
            orders=orders,
            limit=1,
        ).query()
        return result[0] if len(result) > 0 else None

    def select(
        self,
        fields: List[str] = [],
    ) -> KaithQuery:
        """get query instance

        Args:
            fields (List[str], optional): fields required. Defaults to [].

        Returns:
            KaithQuery: query instance
        """
        return KaithQuery(self._requster, fields=fields)

    def delete(
        self,
        conditions: Dict[str, Any],
    ) -> int:
        """delete records by conditions

        Args:
            conditions (Dict[str, Any]): conditions

        Returns:
            int: delete count
        """
        filter = KaithQuery(self._requster)._condition2filter(conditions)
        return KaithQuery(self._requster, filter=filter).delete()

    def delete_by_id(
        self,
        id: str,
    ) -> int:
        """delete record by id

        Args:
            id (str): record id

        Returns:
            int: delete count
        """
        data = self._requster.delete_record(
            record_id=id,
        )
        return True

    def count(
        self,
        conditions: Optional[Dict[str, Any] | LeapcellFilter] = None,
    ) -> int:
        """count records by conditions

        Args:
            conditions (Dict[str, Any] | LeapcellFilter, optional): conditions. Defaults to None.

        Returns:
            int: count
        """
        filter = KaithQuery(self._requster)._condition2filter(conditions)
        return KaithQuery(self._requster, filter=filter).count()

    def search(
        self,
        query: str,
        search_fields: List[str] = [],
        fields: List[str] = [],
        boost_fields: Dict[str, int] = {},
        offset: int = 0,
        limit: int = 10,
        conditions: Optional[Dict[str, Any] | LeapcellFilter] = None,
        orders: List[Tuple[str, str]] = [],
    ):
        """_summary_

        Args:
            query (str): the keyword to search
            search_fields (List[str], optional): the fields to search. Defaults to [].
            fields (List[str], optional): the fields to return. Defaults to [].
            boost_fields (Dict[str, int], optional): the fields to boost. Defaults to {}.
            offset (int, optional): offset. Defaults to 0.
            limit (int, optional): limit. Defaults to 10.
            conditions (Optional[Dict[str, Any]  |  LeapcellFilter], optional): conditions. Defaults to None.
            orders (List[Tuple[str, str]], optional): order by. Defaults to [].

        Returns:
            _type_: record instance list
        """
        data = KaithQuery(
            self._requster,
            fields=fields,
            offset=offset,
            limit=limit,
            filter=KaithQuery(self._requster)._condition2filter(conditions),
            orders=orders,
        ).search(query, search_fields, boost_fields)
        return data

    def upload_file(
        self,
        file: bytes,
        filename: Optional[str] = None,
    ) -> LeapcellFile:
        """upload file

        Args:
            file (bytes): file bytes(base64)

        Returns:
            LeapcellFile: file instance
        """
        data = self._requster.upload(
            data=file,
            filename=filename,
        )
        assert isinstance(data, LeapcellFile)
        return data

    def upload_files(
        self,
        files: List[bytes],
    ) -> List[LeapcellFile]:
        """upload files

        Args:
            files (List[bytes]): files bytes(base64), list length must be less than 10

        Returns:
            List[LeapcellFile]: file instance list
        """
        data = self._requster.upload(
            data=files,
        )
        assert isinstance(data, list)
        return data

    def __getitem__(
        self,
        key: str,
    ) -> LeapcellField:
        return LeapcellField(key)

    def toJSON(self):
        meta_info = self.meta()
        return meta_info.toJSON()

    def tojson(self):
        return self.toJSON()
