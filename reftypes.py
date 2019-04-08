import csv

db = {
    'wos': {
            'sep': '\t',
            'enc': 'utf_16_le',
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
    'proquest_n_a': {
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