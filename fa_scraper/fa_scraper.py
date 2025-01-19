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

from .types import FACategory, FAList, Lang, ListId, UserId, Page

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

SKIP_BY_LANG = {
    Lang.ES: {
        FACategory.TVS: "Serie",
        FACategory.TVMS: "Miniserie",
        FACategory.TV: "TV",
    },
    Lang.EN: {
        FACategory.TVS: "tv series",
        FACategory.TVMS: "miniseries",
        FACategory.TV: "TV",
    },
}

TITLE_ERROR_TEMPLATE = "Unexpected error while parsing data for title '{title}'"
PAGE_ERROR_TEMPLATE = "Unexpected error while parsing data on page '{page}'"
SKIP_TITLE_TEMPLATE = "Skipping {title} since it is a '{title_type}'"


def get_date(tag: bs4.element.Tag, lang: Lang) -> str:
    """Gets date from tag (format YYYY-MM-DD)"""

    if not tag.string:
        raise ValueError("Missing date on tag {}".format(tag))

    if lang == Lang.ES:
        date_str = tag.string[len("votada ") :].strip()
        fecha = arrow.get(date_str, "D [de] MMMM [de] YYYY", locale="es_ES").date()
    else:
        date_str = tag.string[len("Rated ") :].strip()
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


def should_skip_type(
    title_type: str, lang: Lang, ignore_list: Iterable[FACategory]
) -> bool:
    """Checks if given title type should be skipped."""
    for category in ignore_list:
        if title_type == SKIP_BY_LANG[lang][category]:
            return True
    return False


def pages_from(template: str) -> Iterator[Page]:
    """Yields pages from a given section until one of them fails."""

    eof = False
    n = 1

    while not eof:
        url = template.format(n)
        request = requests.get(url)
        request.encoding = "utf-8"

        yield Page(url=url, contents=bs4.BeautifulSoup(request.text, "lxml"))

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

    FA = (
        FA_ROOT_URL + "userratings.php?user_id={id}&p={{}}&orderby=rating-date&chv=list"
    ).format(lang=lang, id=user_id)

    for page in pages_from(FA):
        try:
            ratings_on_a_date = page.contents.find_all(class_=["fa-content-card"])
            cur_date = None

            for ratings in ratings_on_a_date:

                cur_date = get_date(ratings.find_all(class_="card-header")[0], lang)
                tags = ratings.find_all(class_="row mb-4")
                for tag in tags:
                    try:
                        title = tag.find_all(class_="mc-title")[0].a
                        title_name = title.string.strip()
                        title_type = tag.find_all(class_="types-wrapper")
                        if title_type and should_skip_type(
                            title_type[0].find_all(class_="type")[0].string.strip(),
                            lang,
                            ignore_list,
                        ):
                            print(
                                SKIP_TITLE_TEMPLATE.format(
                                    title=title_name,
                                    title_type=title_type[0]
                                    .find_all(class_="type")[0]
                                    .string.strip(),
                                )
                            )
                            continue

                        yield {
                            "Title": title.string.strip(),
                            "Year": int(
                                tag.find_all(class_="fa-card")[0]
                                .find_all(class_="d-flex")[0]
                                .find_all(class_="mc-year")[0]
                                .string.strip()
                            ),
                            "Directors": get_directors(tag),
                            "WatchedDate": cur_date,
                            "Rating": int(
                                tag.find_all(class_="fa-user-rat-box")[0].string
                            )
                            / 2,
                            "Rating10": tag.find_all(class_="fa-user-rat-box")[
                                0
                            ].string.strip(),
                        }
                    except:
                        print(TITLE_ERROR_TEMPLATE.format(title=title.string.strip()))
                        raise
        except:
            print(PAGE_ERROR_TEMPLATE.format(page=page.url))
            raise


def get_list_data(
    user_id: UserId, list_id: ListId, lang: Lang, ignore_list: Iterable[FACategory]
) -> Iterator[Mapping[str, Any]]:
    """Yields films from list given list id"""

    FA = (
        FA_ROOT_URL + "userlist.php?user_id={user_id}&list_id={list_id}&page={{}}"
    ).format(lang=lang, user_id=user_id, list_id=list_id)

    for page in pages_from(FA):
        try:
            tags = page.contents.find_all(class_=["movie-wrapper"])

            for tag in tags:
                try:
                    title = tag.find_all(class_="mc-title")[0].a
                    title_name = title.string.strip()
                    title_type = tag.find_all(class_="d-flex")[0].find_all(
                        class_="type"
                    )
                    if title_type and should_skip_type(
                        title_type[0].string.strip(), lang, ignore_list
                    ):
                        print(
                            SKIP_TITLE_TEMPLATE.format(
                                title=title_name,
                                title_type=title_type[0].string.strip(),
                            )
                        )
                        continue

                    yield {
                        "Title": title_name,
                        "Year": int(
                            tag.find_all(class_="fa-card")[0]
                            .find_all(class_="d-flex")[0]
                            .find_all(class_="mc-year")[0]
                            .string.strip()
                        ),
                        "Directors": get_directors(tag),
                    }
                except:
                    print(TITLE_ERROR_TEMPLATE.format(title=title_name))
                    raise
        except:
            print(PAGE_ERROR_TEMPLATE.format(page=page.url))
            raise


def get_user_lists(user_id: UserId, lang: Lang) -> Iterator[FAList]:
    """Yields all lists from the given user"""

    FA = (FA_ROOT_URL + "userlists.php?user_id={user_id}&p={{}}").format(
        lang=lang, user_id=user_id
    )

    for page in pages_from(FA):
        try:
            tags = page.contents.find_all(class_=["list-name-wrapper"])
            for tag in tags:
                list_name = tag.text.split("\n")[1]
                list_name = "".join(w for w in list_name if w.isalnum() or w == " ")

                url = tag.a.get("href")
                list_id = ListId(url[url.find("list_id=") + len("list_id=") :])
                yield FAList(list_id, list_name)
        except:
            print(PAGE_ERROR_TEMPLATE.format(page=page.url))
            raise


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
