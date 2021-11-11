#! /usr/bin/python3
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import csv
import locale
import platform
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Iterator, List, Mapping

import bs4
import requests


class FACategory(Enum):
    """FilmAffinity categories"""

    TVS = "TVS"
    TVMS = "TVMS"
    TV = "TV"
    S = "S"

    def __str__(self):
        """Returns category"""
        return self.value


# FilmAffinity root URL
FA_ROOT_URL = "https://www.filmaffinity.com/{lang}/"


def set_locale(lang: str):
    """Attempts to set locale."""

    if platform.system() == "Linux":
        loc = "es_ES.utf8" if lang == "es" else "en_US.utf8"
    elif platform.system() == "Darwin":
        loc = "es_ES.UTF-8" if lang == "es" else "en_US.UTF-8"
    elif platform.system() == "Windows":
        loc = "es_ES" if lang == "es" else "en_US"
    else:
        raise locale.Error()

    locale.setlocale(locale.LC_ALL, loc)


def get_date(tag: bs4.element.Tag, lang: str) -> str:
    """Gets date from tag (format YYYY-MM-DD)"""

    if not tag.string:
        raise ValueError("Missing date on tag {}".format(tag))

    if lang == "es":
        date_str = tag.string[len("Votada el día: ") :].strip()
        fecha = datetime.strptime(date_str, "%d de %B de %Y").date()
    else:
        date_str = tag.string[len("Rated on ") :].strip()
        fecha = datetime.strptime(date_str, "%B %d, %Y").date()

    return fecha.strftime("%Y-%m-%d")


def get_directors(tag: bs4.element.Tag) -> str:
    """Gets directors from a film"""

    def sanitize_director_tag(d: bs4.element.Tag) -> str:
        """Sanitizes director tag into director name."""
        if not d.a:
            # No director, skip
            return ""

        director = d.a["title"]
        if isinstance(director, list):
            director = " ".join(director)

        return director[:-10] if director.endswith("(Creator)") else director

    return ", ".join(
        sanitize_director_tag(d)
        for d in tag.find_all(class_="mc-director")[0].find_all(class_="nb")
    )


def is_chosen_category(
    tag: bs4.element.Tag, lang: str, ignore_list: Iterable[FACategory]
) -> bool:
    """Checks if given tag is within the chosen categories"""

    title = tag.find_all(class_="mc-title")[0].a.string.strip()

    if lang == "es":
        skipdct = {
            FACategory.TVS: "(Serie de TV)",
            FACategory.TVMS: "(Miniserie de TV)",
            FACategory.TV: "(TV)",
            FACategory.S: "(C)",
        }
    else:
        skipdct = {
            FACategory.TVS: "(TV Series)",
            FACategory.TVMS: "(TV Miniseries)",
            FACategory.TV: "(TV)",
            FACategory.S: "(S)",
        }

    skip = map(skipdct.get, ignore_list)

    return not any(title.endswith(suffix) for suffix in skip)


def pages_from(template: str) -> Iterator[bs4.BeautifulSoup]:
    """Yields pages from a given section until one of them fails."""

    eof = False
    n = 1

    while not eof:
        request = requests.get(template.format(n))
        request.encoding = "utf-8"

        yield bs4.BeautifulSoup(request.text, "lxml")

        eof = request.status_code != 200
        if not eof:
            print("Page {n}".format(n=n), end="\r")
        else:
            print("Page {n}. Download complete!".format(n=n - 1))
        n += 1


def get_profile_data(
    user_id: str, lang: str, ignore_list: Iterable[FACategory]
) -> Iterator[Mapping[str, Any]]:
    """Yields films rated by user given user id"""

    FA = (FA_ROOT_URL + "userratings.php?user_id={id}&p={{}}&orderby=4").format(
        lang=lang, id=user_id
    )

    for page in pages_from(FA):
        tags = page.find_all(class_=["user-ratings-header", "user-ratings-movie"])
        cur_date = None

        for tag in tags:
            if tag["class"] == ["user-ratings-header"]:
                cur_date = get_date(tag, lang)
            elif is_chosen_category(tag, lang, ignore_list):
                title = tag.find_all(class_="mc-title")[0].a
                yield {
                    "Title": title.string.strip(),
                    "Year": title.next_sibling.strip()[1:-1],
                    "Directors": get_directors(tag),
                    "WatchedDate": cur_date,
                    "Rating": int(tag.find_all(class_="ur-mr-rat")[0].string) / 2,
                    "Rating10": tag.find_all(class_="ur-mr-rat")[0].string,
                }


def get_list_data(
    user_id: str, list_id: str, lang: str, ignore_list: Iterable[FACategory]
) -> Iterator[Mapping[str, str]]:
    """Yields films from list given list id"""

    FA = (
        FA_ROOT_URL + "userlist.php?user_id={user_id}&list_id={list_id}&page={{}}"
    ).format(lang=lang, user_id=user_id, list_id=list_id)

    for page in pages_from(FA):
        tags = page.find_all(class_=["movie-wrapper"])

        for tag in tags:
            if is_chosen_category(tag, lang, ignore_list):
                title = tag.find_all(class_="mc-title")[0].a
                yield {
                    "Title": title.string.strip(),
                    "Year": title.next_sibling.strip()[1:-1],
                    "Directors": get_directors(tag),
                }


def get_user_lists(user_id: str, lang: str) -> Iterator[List[str]]:
    """Yields all lists from the given user"""

    FA = (FA_ROOT_URL + "userlists.php?user_id={user_id}&p={{}}").format(
        lang=lang, user_id=user_id
    )

    for page in pages_from(FA):
        tags = page.find_all(class_=["list-name-wrapper"])
        for tag in tags:
            list_name = tag.text.split("\n")[1]
            list_name = "".join(w for w in list_name if w.isalnum() or w == " ")

            url = tag.a.get("href")
            list_id = url[url.find("list_id=") + len("list_id=") :]
            yield [list_id, list_name]


def save_lists_to_csv(
    user_id: str, lang: str, pattern: str, ignore_list: Iterable[FACategory]
):
    """Extracts all lists from a user and saves them independently"""

    for user_list in get_user_lists(user_id, lang):
        films = get_list_data(user_id, user_list[0], lang, ignore_list)
        save_to_csv(films, pattern.format(user_list[1]))


def save_to_csv(films: Iterator[Mapping[str, Any]], filename: str):
    """Saves films in a csv file"""

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(next(films)))

        for film in films:
            writer.writerow(list(film.values()))
