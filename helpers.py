import pandas as pd
import re
import os
import csv
from reftypes import db


def check_db(base, val):

    # Check validity of base and scores values
    if not base in db.keys():
        raise ValueError("Citation database not recognised. Supported values are 'wos' (Web of Science) and 'scopus' (Scopus).")
    # Check validity of base and scores values
    if not val in db[base].keys():
        raise ValueError("Scores value not recognised. Supported values are 'so' (source), 'pu' (publisher) and 'py' (year).")

def get_input(user_input, all_files):

    # Check if USER_INPUT is a valid path
    if not os.path.exists(user_input):
        raise FileNotFoundError('Input path not found. Please check the USER_INPUT variable.')
    
    # Check if USER_INPUT is a folder or a file
    if os.path.isdir(user_input):
        
        # Build list of file paths
        files = [os.path.join(user_input, f) for f in os.listdir(user_input)]
        
        # Ask whether to include individual files - else include entire folder
        if not all_files:
            select_files = []
            for f in files:
                print('Add {} to analysis? (y/n)'.format(f))
                response = input()
                if response.lower() in ['y', 'yes']:
                    select_files.append(f)
                    print('{} added.'.format(f))
                else:
                    print('{} not added.'.format(f))
                    continue
            return select_files
        else:
            print('All files added to analysis.')
            return files
    else:
        # Return path to file as single element list
        return [user_input]

def create_df(files, base, val):
    print('Creating DataFrame...')
    # Setup database parameters from reftypes.py
    separator = db[base]['sep']
    code = db[base]['enc']
    title = db[base]['ti']
    abstract = db[base]['ab']
    quote = db[base]['quote']
    
    # Create empty DataFrame and append each file
    df = pd.DataFrame()
    
    for f in files:
        add_file = pd.read_csv(f, sep=separator, encoding=code, index_col=False, usecols=[title, abstract, val], quoting=quote)
        df = df.append(add_file)
    return df

def scores_df(df, val):
    print('Creating scores table...')
    val_list = df[val].fillna('N/A')
    val_list.reset_index(drop=True, inplace=True)
    
    # Create list of unique values
    values = sorted(list(val_list.unique()))
    values = set([str(i).lower() for i in values])
    
    # Create DataFrame with a binary table of scores
    scores = pd.DataFrame(columns=values, index=val_list.index).fillna('0')
    
    # Populate each row of the binary table
    for i, val in enumerate(val_list):
        scores[str(val).lower()][i] = '1'
    
    return scores

def format_header(scores):
    print('Formatting header...')
    # Remove illegal characters from column names with regular expression:
    scores.columns = [re.sub('[\[\]<>_]', '', col) for col in scores.columns]
    
    # Convert to VOSviewer scores header format:
    scores.columns = ['score<{}>'.format(col) for col in scores.columns]
    
    return scores

def scores_file(scores, val, output_path):
    print('Creating scores file...')
    # Setup output values
    val = val.replace(' ', '_')
    sep_val = '\t'
    
    output_name = '{}_{}_scores.txt'.format(output_path, val)
    if os.path.exists(output_name):
        raise Exception('File already exists. Change OUTPUT_NAME and try again.')
    scores.to_csv(path_or_buf=output_name, sep=sep_val, index=False)
    
    return 'Scores file created.'

def corpus_file(df, base, output_path):
    print('Creating corpus file...')
    # Setup output values
    sep_val = '\t'
    output_name = '{}_corpus.txt'.format(output_path)
    df[db[base]['ab']] = df[db[base]['ab']].fillna('-')
    corpus = pd.DataFrame(df[db[base]['ti']] + ' ' + df[db[base]['ab']])
    if os.path.exists(output_name):
        raise Exception('File already exists. Change OUTPUT_NAME and try again.\nNote: corpus files can be re-used with different scores files from the same data set.')
    corpus.to_csv(path_or_buf=output_name, sep=sep_val, index=False, header=False)
    
    return 'Corpus file created.'

def check_output(output_path):
    if not os.path.exists(output_path):
        print('Output directory not found. Creating path...')
        os.makedirs(output_path)

def generate_files(user_input, output_name, path, val, base, all_files=False, skip=False):

    check_db(base, val)
    value = db[base][val]
    output_path = os.path.join(path, output_name)
    check_output(path)
    # Check input and generate DataFrame
    df = create_df(get_input(user_input, all_files), base, value)

    scores = format_header(scores_df(df, value))

    scores_file(scores, value, output_path)

    if not skip:
        corpus_file(df, base, output_path)

    print('File creation successful.')