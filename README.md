# filmAffinity to Letterboxd

(_[Versión en español](README_es.md)_)

Generates CSV file compatible with
[Letterboxd diary importer](https://letterboxd.com/about/importing-data/) from
FilmAffinity user's data given their ID.

_This program is intended for personal use only; please ensure the person you
are getting the data from consents to it beforehand and check which privacy and
data protection regulations might apply before using the program to get data
from other people._

## Getting your IDs

In order to get your FilmAffinity data you need to find out what your
FilmAffinity ID is. There are different IDs for your user ratings and your
lists.

### How to get your user id

Go to your profile page and copy the `user_id` field from the URL:

`filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**

### How to get your list id

Go to the list pages (in the left menu), and access the list you want (it needs
to be public).

You need to copy the `list_id` field from the URL:

`filmaffinity.com/es/mylist.php?list_id=`**XXXXXX**

## Running the script

### Locally

You need to have [Python 3](https://www.python.org/downloads),
[BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup),
[requests](https://requests.readthedocs.io/en/master/) and
[lxml](https://lxml.de/) installed. Once installed, run:

```sh
./faScrap.py [--csv FILE] [--lang LANG] id
```

### With Docker

You need to install Docker. Once installed, run:

```sh
docker run --name fa-letterboxd fa-letterboxd python3 fa-scrapper.py id
docker cp fa-letterboxd:/*.csv .
docker rm fa-letterboxd`
```

### Options

- `--list LIST` sets ID of the public list you want to export
- `--csv FILE` sets CSV export file name to `FILE`
- `--lang LANG` sets language to `LANG`. Letterboxd importer works best in
  English, the default option.

## Troubleshooting

- `Could not set locale`: The script attempts to guess your
  [locale](<https://en.wikipedia.org/wiki/Locale_(computer_software)>) setting
  given your platform. If it fails to do so you need to provide it yourself. On
  Linux you can get available locales by running `locale -a` in your terminal.
