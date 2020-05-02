# filmAffinity to Letterboxd

Generates csv file compatible with Letterboxd diary importer from Filmaffinity user's data given their id.

## How to get your id

Go to your profile page and copy the `user_id` field from the url:

`https://www.filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**

## Running the script

You need to have [Python 3](https://www.python.org/downloads) and [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) installed. Once installed just run:

``` sh
./faScrap.py [--csv FILE] [--lang LANG] id
```

## Options

- `--csv FILE` sets csv export file name to `FILE`
- `--lang LANG` sets language to `LANG`. Letterboxd importer works best with english, the default option.

## Troubleshooting

- `Could not set locale`: The script attempts to guess your [locale](https://en.wikipedia.org/wiki/Locale_(computer_software)) setting given your platform. If it fails to do so you need to provide it yourself. On Linux you can get available locales by running `locale -a` in your terminal.
