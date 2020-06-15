import sys
import argparse
import locale
from .fa_scrapper import set_locale, get_list_data, get_profile_data, save_to_csv

__version__ = "0.1.0"


def main():
    """Main function"""
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
