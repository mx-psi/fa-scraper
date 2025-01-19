# filmAffinity to Letterboxd

(_[Versión en español](https://github.com/mx-psi/fa-scraper/blob/master/README_es.md)_)

Generates CSV file compatible with
[Letterboxd diary importer](https://letterboxd.com/about/importing-data/) from
FilmAffinity user's data given their ID.

_This program is intended for personal use only; please ensure the person you
are getting the data from consents to it beforehand and check which privacy and
data protection regulations might apply before using the program to get data
from other people._

## Installation

### Using `pip`

You can install `fa-scraper` using `pip` ([Python 3.9+](https://www.python.org)):

```sh
python3 -m pip install fa-scraper
```

Then run

```sh
fa-scraper [--csv FILE] [--lang LANG] id
```

### Using Docker

You need to install Docker. Once installed, run:

```sh
docker run --name fa-container fascraperdev/fascraper fa-scraper id
docker cp fa-container:/*.csv .
docker rm fa-container`
```

## Getting your IDs

In order to get your FilmAffinity data you need to find out what your
FilmAffinity ID is. There are different IDs for your user ratings and your
lists.

### How to get your user id

Go to your profile page and copy the `user_id` field from the URL:

`filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**

### How to get a list id

Go to the list pages (in the left menu), and access the list you want (it needs
to be public).

You need to copy the `list_id` field from the URL:

`filmaffinity.com/es/mylist.php?list_id=`**XXXXXX**

## Options

- `--list LIST` sets ID of the public list you want to export
- `--csv FILE` sets CSV export file name to `FILE`
- `--lang LANG` sets language to `LANG`. Letterboxd importer works best in
  English, the default option.

Run `fa-scraper --help` to see further options.
