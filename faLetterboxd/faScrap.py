#! /usr/bin/python3
# Author: Pablo Baeyens
# Usage:
#   ./faScrap.py -h
# for usage info and options


import argparse
import requests
import csv
import bs4

from datetime import datetime
import platform
import locale


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
        date_str = tag.string[len("Votada el día: "):].strip()
        fecha = datetime.strptime(date_str, "%d de %B de %Y").date()
    else:
        date_str = tag.string[len("Rated on "):].strip()
        fecha = datetime.strptime(date_str, "%B %d, %Y").date()

    return fecha.strftime("%Y-%m-%d")


def get_directors(tag):
    """Gets directors from a film"""
    directors = list(map(lambda d: d.a["title"], tag.find_all(
        class_="mc-director")[0].find_all(class_="nb")))

    for director in directors:
        if director.endswith("(Creator)"):
            director = director[:-10]

    return ", ".join(directors)


def is_film(tag, lang):
    """Checks if given tag is a film"""

    title = tag.find_all(class_="mc-title")[0].a.string.strip()
    skip = []

    if lang == "es":
        skip = ["(Serie de TV)", "(Miniserie de TV)", "(TV)", "(C)"]
    else:
        skip = ["(TV Series)", "(TV Miniseries)", "(TV)", "(S)"]

    return not any(map(title.endswith, skip))


def get_data(user_id, lang):
    """Gets list of films from user id"""

    data = []
    eof = False
    n = 1
    FA = "https://www.filmaffinity.com/" + lang + \
        "/userratings.php?user_id={id}&p={n}&orderby=4"

    while not eof:
        request = requests.get(FA.format(id=user_id, n=n))
        request.encoding = "utf-8"
        page = bs4.BeautifulSoup(request.text, "lxml")
        tags = page.find_all(
            class_=[
                "user-ratings-header",
                "user-ratings-movie"])
        cur_date = None

        for tag in tags:
            if tag["class"] == ["user-ratings-header"]:
                cur_date = get_date(tag, lang)
            elif is_film(tag, lang):
                title = tag.find_all(class_="mc-title")[0].a
                film = {
                    "Title": title.string.strip(),
                    "Year": title.next_sibling.strip()[
                        1:-1],
                    "Directors": get_directors(tag),
                    "WatchedDate": cur_date,
                    "Rating": int(
                        tag.find_all(
                            class_="ur-mr-rat")[0].string) / 2,
                    "Rating10": tag.find_all(
                        class_="ur-mr-rat")[0].string}
                data.append(film)

        eof = request.status_code != 200
        if not eof:
            print("Página {n}".format(n=n), end="\r")
        else:
            print("Página {n}. Download complete!".format(n=n - 1))

        n += 1

    return data


def save_to_csv(data, filename):
    """Saves list of dictionaries in a csv file"""

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(data[0]))

        for film in data:
            writer.writerow(list(film.values()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates csv compatible with LetterBoxd from Filmaffinity user's id.")
    parser.add_argument("id", help="User's id")
    parser.add_argument(
        "--csv",
        nargs=1,
        help="Name of export FILE",
        metavar="FILE")
    parser.add_argument(
        "--lang",
        nargs=1,
        help="Language for exporting",
        metavar="LANG",
        default=["en"],
        choices={
            "es",
            "en"})

    args = parser.parse_args()
    export_file = args.csv[0] if args.csv else "filmAffinity_{lang}_{id}.csv".format(
        id=args.id, lang=args.lang[0])

    try:
        set_locale(args.lang[0])
    except locale.Error:
        print(
            "Could not set locale for \'{lang}\' and UTF-8 encoding.".format(lang=args.lang[0]))
        manual_locale = input("locale (empty for default): ").strip()
        if manual_locale:
            try:
                locale.setlocale(locale.LC_ALL, manual_locale)
            except locale.Error as e:
                print(e)
                exit()

    try:
        data = get_data(args.id, args.lang[0])
    except ValueError as v:
        print("Error:", v)
        exit()

    save_to_csv(data, export_file)
