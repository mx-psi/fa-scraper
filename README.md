# filmAffinity to Letterboxd

Generates csv file compatible with Letterboxd diary importer from Filmaffinity user's data given their id.

## How to get your user id

Go to your profile page and copy the `user_id` field from the url:

`https://www.filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**

## How to get your list id

Go to the list pages (in the left menu), and access the list you want (need to be public).

You need to copy the `list_id` field from the url:

`https://www.filmaffinity.com/es/mylist.php?list_id=`**XXXXXX**

## Running the script

You need to have [Python 3](https://www.python.org/downloads), [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup), [requests](https://requests.readthedocs.io/en/master/) and [lxml](https://lxml.de/) installed. Once installed just run:

``` sh
./faScrap.py [--csv FILE] [--lang LANG] id
```

### With docker

First of all you need to have docker installed, and latter you have to run this simple steps

You need to replace `USER_ID` with your current user id

`docker run --name fa-letterboxd fa-letterboxd python3 faScrap.py --lang en --csv fa-to-lbx.csv USER_ID && docker cp fa-letterboxd:/fa-to-lbx.csv . && docker rm fa-letterboxd`

## Options

- `--list LIST` The id of the public list you wanna export, if is available export the list and not your ratings
- `--csv FILE` sets csv export file name to `FILE`
- `--lang LANG` sets language to `LANG`. Letterboxd importer works best with english, the default option.

## Troubleshooting

- `Could not set locale`: The script attempts to guess your [locale](https://en.wikipedia.org/wiki/Locale_(computer_software)) setting given your platform. If it fails to do so you need to provide it yourself. On Linux you can get available locales by running `locale -a` in your terminal.
