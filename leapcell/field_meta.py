from typing import Dict


class FieldMeta:
    def __init__(self, obj: Dict) -> None:
        self._id: str = obj["id"]
        self._type: str = obj["type"]
        self._name: str = obj["name"]
        pass

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def __str__(self) -> str:
        return "<field id: {} name: {}, type: {}>".format(
            self.id,
            self.name,
            self.type,
        )

    def __repr__(self) -> str:
        return self.__str__()
    
    def todict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }
    
    def toJSON(self):
        return self.todict()
