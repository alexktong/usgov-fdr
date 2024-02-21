# Source: https://disclosures-clerk.house.gov/FinancialDisclosure

import difflib
import os
import pandas as pd
from datetime import datetime
import configparser


# Load config file
def load_config(config_file):
    config_file = config_file

    config_obj = configparser.ConfigParser()
    config_obj.read(config_file)

    return config_obj


def create_directory(directory_path):

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def read_fd_text_file(directory_to_fd_file_txt):
    
    df = pd.read_csv(directory_to_fd_file_txt, sep='\t')

    df['FilingDate'] = pd.to_datetime(df['FilingDate'], format='%m/%d/%Y').dt.date

    df['URL'] = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/' + df['DocID'].astype(str) + '.pdf'

    return df


def get_fd_for_past_days(df, filing_date_lag_days):

    # Filter by filing date
    date_today = datetime.today().date()

    filing_date_since = date_today - pd.Timedelta(days=filing_date_lag_days)

    # Only retrieve records within filing date threshold
    df = df[df['FilingDate'] >= filing_date_since]

    # Sort by filing date
    df = df.sort_values('FilingDate', ascending=False)

    return df


def get_fd_by_full_name(df, list_of_full_names):
    
    # Construct full name
    df['FullName'] = df['First'].str.lower() + ' ' + df['Last'].str.lower()

    # Filter by full name
    list_of_full_names_to_keep = []
    for full_name in list_of_full_names:
        full_name_to_keep = difflib.get_close_matches(full_name, df['FullName'], n=1)

        if len(full_name_to_keep) > 0:
            list_of_full_names_to_keep.append(full_name_to_keep[0])

    df = df[df['FullName'].isin(list_of_full_names_to_keep)]

    return df


def main():

    # Load config file
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config_obj = load_config(config_file)
    
    # Directory to save the output file
    output_directory = config_obj.get('output', 'directory')
    create_directory(output_directory)

    # Name of output file
    output_file = config_obj.get('output', 'file_name')
    
    # Read the txt file as a dataframe
    fd_text_file = config_obj.get('input', 'directory_to_fd_text_file')
    df = read_fd_text_file(fd_text_file)

    # Return FDs within specified time period
    filing_date_lag_days = config_obj.getint('input', 'filing_date_lag_days')
    
    df = get_fd_for_past_days(df, filing_date_lag_days)

    # Return FDs of select individuals by last name
    list_of_full_names = config_obj.get('input', 'list_of_full_names')
    list_of_full_names = list_of_full_names.split(', ')

    df = get_fd_by_full_name(df, list_of_full_names)

    # Save to a CSV file
    df = df[['Prefix', 'FullName', 'FilingDate', 'URL']]

    df.to_csv(os.path.join(output_directory, output_file), index=False)


if __name__ == '__main__':
    main()