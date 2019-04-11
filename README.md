## VOSviewer scores file generator

Generate binary tables with scores for [VOSviewer](http://www.vosviewer.com/).

#### Supported citation bases:
- Web of Science
- Scopus

#### Supported values:
- Source ('so')
- Publisher ('pu')
- Year ('py')

#### Input
The programme can handle any number of input files from the same search. The file format differs depending on the citation base. When exporting references choose the following settings:
- Web of Science: Tab-delimited (Win)
- Scopus: CSV Excel

Remember to include title, abstract and the desired scores value (default: source) in the export.

For detailed information and options on file formats and file encodings consult `reftypes.py`.

#### Output
The programme outputs a scores file and optionally a corpus file.

The corpus and scores files can be loaded into VOSviewer by creating a map based on text data and reading data from VOSviewer files.

#### Requirements
The programme is created with and for Python 3.7 and depends on the pandas library as well as a number of standard libraries.