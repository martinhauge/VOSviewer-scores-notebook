import csv

# Currently supported databases are Web of Science and Scopus
# The 'db' dictionary allows for additional scores values as well as adjustment of file encodings etc.
db = {
    'wos': {
            'sep': '\t',
            'enc': 'utf_16_le', # Change encoding to 'utf_8' for Win UTF-8 format
            'quote': csv.QUOTE_NONE,
            'ti': 'TI',
            'ab': 'AB',
            'so': 'SO',
            'py': 'PY',
            'pu': 'PU'
            },
    'scopus': {
            'sep': ',',
            'enc': None,
            'quote': csv.QUOTE_ALL,
            'ti': 'Title',
            'ab': 'Abstract',
            'so': 'Source title',
            'py': 'Year',
            'pu': 'Publisher'
            },
    'proquest': {
            'sep': '\t',
            'enc': None,
            'quote': csv.QUOTE_ALL,
            'ti': 'Title',
            'ab': 'Abstract',
            'so': 'pubtitle',
            'py': 'year',
            'pu': 'publisher'
            }
    }