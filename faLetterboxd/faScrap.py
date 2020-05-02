#! /usr/bin/python3
# Author: Pablo Baeyens
# Usage:
#   ./faScrap.py -h
# for usage info and options

import argparse
import csv
import sys
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates Letterboxd-compatible csv from Filmaffinity user data."
    )
    parser.add_argument("id", help="User id")
    parser.add_argument("--list", help="List id", metavar="LIST")
    parser.add_argument("--csv", nargs=1, help="Name of export FILE", metavar="FILE")
    parser.add_argument(
        "--lang",
        nargs=1,
        help="Language for exporting",
        metavar="LANG",
        default=["en"],
        choices={"es", "en"},
    )

    args = parser.parse_args()

    if args.csv:
        export_file = args.csv[0]
    elif args.list:
        export_file = "filmAffinity_{lang}_{id}_list_{list_id}.csv".format(
            id=args.id, lang=args.lang[0], list_id=args.list
        )
    else:
        export_file = "filmAffinity_{lang}_{id}.csv".format(
            id=args.id, lang=args.lang[0]
        )

    try:
        set_locale(args.lang[0])
    except locale.Error:
        print(
            "Could not set locale for '{lang}' and UTF-8 encoding.".format(
                lang=args.lang[0]
            )
        )
        manual_locale = input("locale (empty for default): ").strip()
        if manual_locale:
            try:
                locale.setlocale(locale.LC_ALL, manual_locale)
            except locale.Error as e:
                print(e)
                sys.exit()

    try:
        if args.list:
            data = get_list_data(args.id, args.list, args.lang[0])
        else:
            data = get_profile_data(args.id, args.lang[0])
    except ValueError as v:
        print("Error:", v)
        sys.exit()

    save_to_csv(data, export_file)
