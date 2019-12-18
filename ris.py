import pandas as pd

def ris_parse(ris_file):
    """ Read RIS file an parse rows and values to list of lists. """

    with open(ris_file, 'r') as f:
        raw = f.read()

    data = raw.strip()

    entry_sep = 'ER  - ' # Use 'ER  - ' or '\n\n' as entry separator.
    line_sep = '\n'

    documents = [item for item in data.split(entry_sep)]
    table = [[item for item in doc.split(line_sep)] for doc in documents]

    return table

def ris_df(ris_file):
    """ Extract and return data as DataFrame. """
    
    table = ris_parse(ris_file)

    # Empty template DataFrame.
    df = pd.DataFrame(columns=['title', 'abstract', 'source', 'year', 'publisher', 'type'], index = range(len(table)))

    # Extract relevant data from RIS file table.
    for n, j in enumerate(table): 
        for i in j:
            if i.startswith('TI'): 
                df.loc[n]['title'] = i[6:] 
            if i.startswith('AB'): 
                df.loc[n]['abstract'] = i[6:] 
            if i.startswith('T2'): 
                df.loc[n]['source'] = i[6:] 
            if i.startswith('PY'):
                df.loc[n]['year'] = i[6:]
            if i.startswith('M3'):
                df.loc[n]['type'] = i[6:]

    return df