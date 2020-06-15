# filmAffinity to Letterboxd

(_[Versión en español](https://github.com/mx-psi/fa-scrapper/blob/master/README_es.md)_)

Generates CSV file compatible with
[Letterboxd diary importer](https://letterboxd.com/about/importing-data/) from
FilmAffinity user's data given their ID.

_This program is intended for personal use only; please ensure the person you
are getting the data from consents to it beforehand and check which privacy and
data protection regulations might apply before using the program to get data
from other people._

## Installation

### Using `pip`

You can install `fa-scrapper` using `pip` ([Python 3.5+](https://www.python.org/)):

```sh
pip install fa-scrapper
```

Then run

```sh
fa-scrapper [--csv FILE] [--lang LANG] id
```

### Using Docker

You need to install Docker. Once installed, run:

```sh
docker build -t fa-image https://github.com/mx-psi/fa-scrapper.git#master
docker run --name fa-container fa-image fa-scrapper id
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

## Troubleshooting

- `Could not set locale`: The script attempts to guess your
  [locale](<https://en.wikipedia.org/wiki/Locale_(computer_software)>) setting
  given your platform. If it fails to do so you need to provide it yourself. On
  Linux you can get available locales by running `locale -a` in your terminal.
