from typing import List, Tuple, Dict, Union, Any
from io import BytesIO
from datetime import datetime
from abc import abstractmethod


class BaseItem:
    def __init__(self) -> None:
        self._data: Any = None
        return

    def to_obj(self) -> Any:
        return self._data

    @property
    def data(self) -> Any:
        return self._data

    @abstractmethod
    def from_obj(self, data: Any) -> None:
        return

    @abstractmethod
    def from_val(self, data: Any) -> None:
        return

    def _process_null_data(self, data: Dict) -> bool:
        if "null" in data and data["null"]:
            self._data = data
            return True
        return False


class StrItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, str should be str".format(type(data))
            )

    def from_val(self, data: str) -> None:
        if not isinstance(data, str):
            raise TypeError("invalid type {}, it should be str".format(type(data)))
        self._data = data


class FloatItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, float):
            self._data = data
        elif isinstance(data, int):
            self._data = float(data)
        else:
            raise ValueError(
                "invalid type {}, float should be float".format(type(data))
            )

    def from_val(self, data: float | int) -> None:
        if not isinstance(data, float) and not isinstance(data, int):
            raise TypeError("invalid type {}, it should be float".format(type(data)))
        self._data = float(data)

class IntItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, int):
            self._data = data
        elif isinstance(data, float):
            self._data = int(data)
        else:
            raise ValueError(
                "invalid type {}, int should be int".format(type(data))
            )

    def from_val(self, data: int) -> None:
        if not isinstance(data, int):
            raise TypeError("invalid type {}, it should be int".format(type(data)))
        self._data = data


class LinkItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, link should be str".format(type(data))
            )

    def from_val(self, data: str) -> None:
        if not isinstance(data, str):
            raise TypeError("invalid type {}, it should be str".format(type(data)))
        self._data = data


class LabelItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, label should be str".format(type(data))
            )

    def from_val(self, data: str) -> None:
        if not isinstance(data, str):
            raise TypeError("invalid type {}, it should be str".format(type(data)))
        self._data = data


class LabelsItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, list):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, labels should be list of str".format(type(data))
            )

    def from_val(self, data: List[str]) -> None:
        if not isinstance(data, list):
            raise TypeError("invalid type {}, it should be list".format(type(data)))
        self._data = data


class ImageItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, str):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, image should be str".format(type(data))
            )

    def from_val(self, data: str | BytesIO) -> None:
        if not isinstance(data, str):
            raise TypeError("invalid type {}, it should be str".format(type(data)))
        self._data = data
        return


class ImagesItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, list):
            self._data = data
        else:
            raise ValueError(
                "invalid type {}, images should be list".format(type(data))
            )

    def from_val(self, data: List[str]) -> None:
        if not isinstance(data, list):
            raise TypeError("invalid type {}, it should be list".format(type(data)))
        self._data = data


class TimeItem(BaseItem):
    def __init__(self) -> None:
        super().__init__()

    def from_obj(self, data: Any) -> None:
        if isinstance(data, int): #TODO: datetime?
            self._data = data
            self._raw = data
        else:
            raise ValueError(
                "invalid type {}, time should be int".format(type(data))
            )

    def from_val(self, data: int | datetime) -> None:
        if not isinstance(data, int) and not isinstance(data, datetime):
            raise TypeError("invalid type {}, it should be int".format(type(data)))
        if isinstance(data, int):
            self._data = data
        elif isinstance(data, datetime):
            self._data = datetime.timestamp(data)
        return


class LongTextItem(StrItem):
    def __init__(self) -> None:
        super().__init__()


class FieldMgr:
    def __init__(self) -> None:
        pass

    @staticmethod
    def from_obj(fieldType: str, data: Dict) -> BaseItem:
        if data is None:
            return None
        item = FieldMgr._get_item(fieldType=fieldType)
        item.from_obj(data=data)
        return item

    @staticmethod
    def from_val(fieldType: str, data: Any) -> BaseItem:
        item = FieldMgr._get_item(fieldType=fieldType)
        item.from_val(data=data)
        return item

    @staticmethod
    def _get_item(fieldType: str):
        item: Union[
            None,
            IntItem,
            StrItem,
            FloatItem,
            TimeItem,
            LinkItem,
            LabelItem,
            LabelsItem,
            ImagesItem,
            ImageItem,
            LongTextItem,
        ] = None
        if fieldType == "INT_NUMBER":
            item = IntItem()
        elif fieldType == "STR":
            item = StrItem()
        elif fieldType == "FLOAT_NUMBER":
            item = FloatItem()
        elif fieldType == "TIME":
            item = TimeItem()
        elif fieldType == "LINK":
            item = LinkItem()
        elif fieldType == "LABEL":
            item = LabelItem()
        elif fieldType == "LABELS":
            item = LabelsItem()
        elif fieldType == "IMAGES":
            item = ImagesItem()
        elif fieldType == "IMAGE":
            item = ImageItem()
        elif fieldType == "LONG_TEXT":
            item = LongTextItem()
        else:
            raise KeyError("not found type '{}'".format(fieldType))
        return item
