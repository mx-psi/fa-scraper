import argparse
import sys

from . import __version__
from .fa_scraper import (
    FILM_FIELDNAMES,
    LIST_FIELDNAMES,
    get_list_data,
    get_profile_data,
    save_lists_to_csv,
    save_to_csv,
)
from .types import FACategory, Lang, ListId, UserId


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generates Letterboxd-compatible csv from Filmaffinity user data.",
        prog="fa-scraper",
    )
    parser.add_argument("id", help="user id", type=UserId)
    parser.add_argument("--list", help="list id", metavar="LIST", type=ListId)
    parser.add_argument("--csv", nargs=1, help="name of export FILE", metavar="FILE")
    parser.add_argument(
        "--lang",
        nargs=1,
        help="language for exporting",
        type=Lang,
        metavar="LANG",
        default=[Lang.EN],
        choices=Lang,
    )
    parser.add_argument("--all-lists", action="store_true", help="download all lists")
    parser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(__version__)
    )
    parser.add_argument(
        "--ignore",
        help="ignore category (default: none)",
        type=FACategory,
        choices=FACategory,
        action="append",
        default=[],
    )

    args = parser.parse_args()

    if args.csv:
        export_file = args.csv[0]
    elif args.list:
        export_file = "filmAffinity_{lang}_{id}_list_{list_id}.csv".format(
            id=args.id, lang=args.lang[0], list_id=args.list
        )
    elif args.all_lists:
        export_file = "filmAffinity_{lang}_{id}_list_{{}}.csv".format(
            id=args.id, lang=args.lang[0]
        )
    else:
        export_file = "filmAffinity_{lang}_{id}.csv".format(
            id=args.id, lang=args.lang[0]
        )

    if args.all_lists:
        save_lists_to_csv(args.id, args.lang[0], export_file, args.ignore)
    else:
        try:
            if args.list:
                data = get_list_data(args.id, args.list, args.lang[0], args.ignore)
                fieldnames = LIST_FIELDNAMES
            else:
                data = get_profile_data(args.id, args.lang[0], args.ignore)
                fieldnames = FILM_FIELDNAMES
        except ValueError as v:
            print("Error:", v)
            sys.exit()

        save_to_csv(data, fieldnames, export_file)
