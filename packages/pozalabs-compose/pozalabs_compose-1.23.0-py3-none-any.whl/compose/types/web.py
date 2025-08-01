import urllib.parse
from typing import Self


class ContentDisposition(str):
    @classmethod
    def attachment(cls, filename: str) -> Self:
        return cls(f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}")
