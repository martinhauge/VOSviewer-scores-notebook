import pandas as pd
import datetime
import re
import os
import csv
from ris import ris_df
from reftypes import db


def check_db(base, val):

    # Check validity of base and scores values
    if not base in db.keys():
        raise KeyError("Citation database not recognised. Supported values are 'wos' (Web of Science) and 'scopus' (Scopus).")
    # Check validity of base and scores values
    if not val in db[base].keys():
        raise KeyError("Scores value not recognised. Supported values are 'so' (source), 'pu' (publisher) and 'py' (year).")

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
            
            if not select_files:
                raise Exception('No files added to analysis.')
            
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

    # Special case for RIS-format
    if base == 'ris':
        for f in files:
            df = df.append(ris_df(f))
        return df
    # Special case for ProQuest XLS-format
    if base == 'proquest':
        for f in files:
            add_file = pd.read_excel(f, index_col=False, usecols=[title, abstract, val])
            df = df.append(add_file)
    else:
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
    scores = pd.DataFrame(columns=values, index=val_list.index).fillna(0)
    
    # Populate each row of the binary table
    for i, val in enumerate(val_list):
        scores[str(val).lower()][i] = 1
    
    return scores

def format_header(scores):
    print('Formatting header...')
    # Remove illegal characters from column names with regular expression:
    scores.columns = [re.sub('[\[\]<>_]', '', col) for col in scores.columns]
    
    scores = scores.sort_index(axis=1)
    
    # Convert to VOSviewer scores header format:
    scores.columns = ['score<{}>'.format(col) for col in scores.columns]
    
    return scores

def scores_file(scores, val, output_path, debugging):
    print('Creating scores file...')
    # Setup output values
    val = val.replace(' ', '_')
    sep_val = '\t'
    
    output_name = '{}_{}_scores.txt'.format(output_path, val)
    if os.path.exists(output_name):
        raise Exception('File already exists. Change OUTPUT_NAME and try again.')
    if not debugging:
        scores.to_csv(path_or_buf=output_name, sep=sep_val, index=False)

def corpus_file(df, base, output_path, debugging):
    print('Creating corpus file...')
    # Setup output values
    sep_val = '\t'
    output_name = '{}_corpus.txt'.format(output_path)

    # Get N/A data for summary and clean output
    abstract_na = df[db[base]['ab']].isna().sum()
    df[db[base]['ab']] = df[db[base]['ab']].fillna('-')
    corpus = pd.DataFrame(df[db[base]['ti']] + ' ' + df[db[base]['ab']])
    if os.path.exists(output_name):
        raise Exception('File already exists. Change OUTPUT_NAME and try again.\nNote: corpus files can be re-used with different scores files from the same data set.')
    if not debugging:
        corpus.to_csv(path_or_buf=output_name, sep=sep_val, index=False, header=False)

    # Return number of missing abstracts for summary()
    return int(abstract_na)

def check_output(output_path):
    if not os.path.exists(output_path):
        print('Output directory not found. Creating path...')
        os.makedirs(output_path)

def summary(scores_df, time_elapsed, abstract_na):
    if type(abstract_na) == int:
        abstract_pct = '{:.2%}'.format(abstract_na / len(scores_df))
    else:
        abstract_pct = 'N/A'
    print(  """\n*** SUMMARY *** \nNumber of scores values: {}\nNumber of references: {}\nAbstracts not available: {} ({})\nTime elapsed: {}"""\
            .format(len(scores_df.columns), len(scores_df), abstract_na, abstract_pct, time_elapsed))

### W.I.P. ###
def bucketise(y_series, interval):
    # Define the range of the buckets
    y_min = y_series.min()
    y_max = y_series.max()

    # Generate left-inclusiive list of buckets adjusted for first and last year
    y_list = [y for y in range(y_min - interval, y_max + interval + 1) if y % interval == 0]
    buckets = pd.cut(y_series, y_list, right=False)

    # TODO: Adjust right edge

    # Format output
    buckets = buckets.astype(str).str.strip('[)')
    buckets = buckets.str.replace(', ', '-')

    return buckets

def generate_files(user_input, output_name, path, val, base, all_files=False, skip=False, buckets=False, interval=5, debugging=False):

    # Set timer for summary()
    start_time = datetime.datetime.now()
    # Check user variables
    check_db(base, val)
    check_output(path)

    # Setup
    value = db[base][val]
    output_path = os.path.join(path, output_name)
    abstract_na = 'N/A'
    
    # Check input and generate DataFrame
    df = create_df(get_input(user_input, all_files), base, value)

    # Reset timer if the user has manually selected which files to include
    if not all_files:
        start_time = datetime.datetime.now()

    if buckets:
        # Check input bucket suitability
        if val == 'py':
            # Call bucketise() and assign return value to DataFrame
            years = df[value]
            value = 'buckets'
            df[value] = bucketise(years, interval)
        else:
            raise Exception('Bucketising only works for publication year ("py") - Please check VAL and BUCKETS.')
    
    scores = format_header(scores_df(df, value))

    scores_file(scores, value, output_path, debugging)

    if not skip:
        abstract_na = corpus_file(df, base, output_path, debugging)

    print('File creation successful.')

    # Calculate time elapsed.
    end_time = datetime.datetime.now()
    time_elapsed = end_time - start_time

    # Generate summary of file creation
    summary(scores, time_elapsed, abstract_na)