__all__ = ("Attachment",)


class Attachment:
    def __init__(self, name: str,  mime_type: str, data: bytes) -> None:
        assert isinstance(data, bytes)
        self._name = name
        self._data = data
        self._mime_type = mime_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def mime_type(self) -> str:
        return self._mime_type

    def __repr__(self) -> str:
        size = len(self._data)
        return f"{self.__class__.__name__}<{self._name!r}, {self._mime_type!r}, size={size}>"
