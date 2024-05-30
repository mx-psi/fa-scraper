from enum import Enum
from typing import NamedTuple, NewType
from dataclasses import dataclass
import bs4


class FACategory(Enum):
    """FilmAffinity categories"""

    TVS = "TVS"
    TVMS = "TVMS"
    TV = "TV"

    def __str__(self):
        """Returns category"""
        return self.value


class Lang(Enum):
    """Language codes."""

    ES = "es"
    EN = "en"

    def __str__(self):
        """Returns option code"""
        return self.value


UserId = NewType("UserId", str)
ListId = NewType("ListId", str)
FAList = NamedTuple("FAList", [("id", ListId), ("name", str)])


@dataclass
class Page:
    url: str
    contents: bs4.BeautifulSoup
