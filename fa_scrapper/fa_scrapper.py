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

from datetime import datetime
import platform
import locale

import requests
import bs4


# FilmAffinity root URL
FA_ROOT_URL = "https://www.filmaffinity.com/{lang}/"


def set_locale(lang):
    """Attempts to set locale."""

    if platform.system() in {"Linux", "Darwin"}:
        loc = "es_ES.utf8" if lang == "es" else "en_US.utf8"
    elif platform.system() == "Windows":
        loc = "es-ES" if lang == "es" else "en-US"
    else:
        raise locale.Error()

    locale.setlocale(locale.LC_ALL, loc)


def get_date(tag, lang):
    """Gets date from tag (format YYYY-MM-DD)"""

    if lang == "es":
        date_str = tag.string[len("Votada el día: ") :].strip()
        fecha = datetime.strptime(date_str, "%d de %B de %Y").date()
    else:
        date_str = tag.string[len("Rated on ") :].strip()
        fecha = datetime.strptime(date_str, "%B %d, %Y").date()

    return fecha.strftime("%Y-%m-%d")


def get_directors(tag):
    """Gets directors from a film"""

    def sanitize_director_tag(d):
        """Sanitizes director tag into director name."""
        director = d.a["title"]
        return director[:-10] if director.endswith("(Creator)") else director

    return ", ".join(
        sanitize_director_tag(d)
        for d in tag.find_all(class_="mc-director")[0].find_all(class_="nb")
    )


def is_film(tag, lang):
    """Checks if given tag is a film"""

    title = tag.find_all(class_="mc-title")[0].a.string.strip()

    if lang == "es":
        skip = ["(Serie de TV)", "(Miniserie de TV)", "(TV)", "(C)"]
    else:
        skip = ["(TV Series)", "(TV Miniseries)", "(TV)", "(S)"]

    return not any(title.endswith(suffix) for suffix in skip)


def pages_from(template):
    """Yields pages from a given section until one of them fails."""

    eof = False
    n = 1

    while not eof:
        request = requests.get(template.format(n))
        request.encoding = "utf-8"
        yield bs4.BeautifulSoup(request.text, "lxml")

        eof = request.status_code != 200
        if not eof:
            print("Página {n}".format(n=n), end="\r")
        else:
            print("Página {n}. Download complete!".format(n=n - 1))
        n += 1


def get_profile_data(user_id, lang):
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
            elif is_film(tag, lang):
                title = tag.find_all(class_="mc-title")[0].a
                yield {
                    "Title": title.string.strip(),
                    "Year": title.next_sibling.strip()[1:-1],
                    "Directors": get_directors(tag),
                    "WatchedDate": cur_date,
                    "Rating": int(tag.find_all(class_="ur-mr-rat")[0].string) / 2,
                    "Rating10": tag.find_all(class_="ur-mr-rat")[0].string,
                }


def get_list_data(user_id, list_id, lang):
    """Yields films from list given list id"""

    FA = (
        FA_ROOT_URL + "userlist.php?user_id={user_id}&list_id={list_id}&page={{}}"
    ).format(lang=lang, user_id=user_id, list_id=list_id)

    for page in pages_from(FA):
        tags = page.find_all(class_=["movie-wrapper"])

        for tag in tags:
            title = tag.find_all(class_="mc-title")[0].a
            yield {
                "Title": title.string.strip(),
                "Year": title.next_sibling.strip()[1:-1],
                "Directors": get_directors(tag),
            }


def save_to_csv(films, filename):
    """Saves films in a csv file"""

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(next(films)))

        for film in films:
            writer.writerow(list(film.values()))
