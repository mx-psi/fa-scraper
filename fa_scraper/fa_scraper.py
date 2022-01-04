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
from typing import Any, Iterable, Iterator, List, Mapping, Sequence

import arrow
import bs4
import requests

from .types import FACategory, FAList, Lang, ListId, UserId

# FilmAffinity root URL
FA_ROOT_URL = "https://www.filmaffinity.com/{lang}/"

FILM_FIELDNAMES = (
    "Title",
    "Year",
    "Directors",
    "WatchedDate",
    "Rating",
    "Rating10",
)

LIST_FIELDNAMES = (
    "Title",
    "Year",
    "Directors",
)


def get_date(tag: bs4.element.Tag, lang: Lang) -> str:
    """Gets date from tag (format YYYY-MM-DD)"""

    if not tag.string:
        raise ValueError("Missing date on tag {}".format(tag))

    if lang == Lang.ES:
        date_str = tag.string[len("Votada el día: ") :].strip()
        fecha = arrow.get(date_str, "D [de] MMMM [de] YYYY", locale="es_ES").date()
    else:
        date_str = tag.string[len("Rated on ") :].strip()
        fecha = arrow.get(date_str, "MMMM D, YYYY", locale="en_US").date()

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
    tag: bs4.element.Tag, lang: Lang, ignore_list: Iterable[FACategory]
) -> bool:
    """Checks if given tag is within the chosen categories"""

    title = tag.find_all(class_="mc-title")[0].a.string.strip()

    if lang == Lang.ES:
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
    user_id: UserId, lang: Lang, ignore_list: Iterable[FACategory]
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
    user_id: UserId, list_id: ListId, lang: Lang, ignore_list: Iterable[FACategory]
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


def get_user_lists(user_id: UserId, lang: Lang) -> Iterator[FAList]:
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
            list_id = ListId(url[url.find("list_id=") + len("list_id=") :])
            yield FAList(list_id, list_name)


def save_lists_to_csv(
    user_id: UserId, lang: Lang, pattern: str, ignore_list: Iterable[FACategory]
):
    """Extracts all lists from a user and saves them independently"""

    for user_list in get_user_lists(user_id, lang):
        films = get_list_data(user_id, user_list.id, lang, ignore_list)
        save_to_csv(films, LIST_FIELDNAMES, pattern.format(user_list.name))


def save_to_csv(
    dicts: Iterator[Mapping[str, Any]], fieldnames: Sequence[str], filename: str
):
    """Saves films in a csv file"""

    # Set to UTF-8 to work around Windows error
    # "'charmap' codec can't encode character".
    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for d in dicts:
            writer.writerow(d)
