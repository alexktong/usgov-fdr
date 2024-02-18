# Source: https://disclosures-clerk.house.gov/FinancialDisclosure

import difflib
import os
import pandas as pd
from datetime import datetime
import configparser


def create_directory(directory_path):

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def download_fd_zip(url_source, input_directory):

    # Downloads the source file into specified directory
    os.system(f'wget -N -P {input_directory} {url_source}')
    

def unzips_fd_zip(input_directory, file_name):

    # Unzips the source file into input directory
    os.system(f'unzip -o -d {input_directory} {os.path.join(input_directory, file_name)}')


def get_fd_text_file(file_name):

    file_name_without_extension = os.path.splitext(file_name)[0]

    file_name_txt = f'{file_name_without_extension}.txt'

    return file_name_txt


def read_fd_text_file(input_directory, fd_file_txt):
    
    df = pd.read_csv(os.path.join(input_directory, fd_file_txt), sep='\t')

    df['FilingDate'] = pd.to_datetime(df['FilingDate'], format='%m/%d/%Y').dt.date

    df['URL'] = 'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/' + df['DocID'].astype(str) + '.pdf'

    return df


def get_fd_by_full_name(df, list_of_full_names, filing_date_lag_days):
    
    # Construct full name
    df['FullName'] = df['First'].str.lower() + ' ' + df['Last'].str.lower()

    # Filter by full name
    list_of_full_names_to_keep = []
    for full_name in list_of_full_names:
        full_name_to_keep = difflib.get_close_matches(full_name, df['FullName'], n=1)

        if len(full_name_to_keep) > 0:
            list_of_full_names_to_keep.append(full_name_to_keep[0])

    df = df[df['FullName'].isin(list_of_full_names_to_keep)]
    
    # Filter by filing date
    date_today = datetime.today().date()

    filing_date_since = date_today - pd.Timedelta(days=filing_date_lag_days)

    df = df[df['FilingDate'] >= filing_date_since]

    return df


def main():

    # Load config file
    config_file = '/home/alexktong_92/python/usgov-fdr/config.ini'

    config_obj = configparser.ConfigParser()
    config_obj.read(config_file)
    
    # Link to source file
    url_source = config_obj.get('input', 'url_source')

    # Directory to save the source file
    input_directory = config_obj.get('input', 'directory')
    create_directory(input_directory)

    # Directory to save the output file
    output_directory = config_obj.get('output', 'directory')
    create_directory(output_directory)

    # Name of output file
    output_file = config_obj.get('output', 'file_name')

    # Reports of individuals to keep
    list_of_full_names = config_obj.get('input', 'list_of_full_names')
    list_of_full_names = list_of_full_names.split(', ')

    # Reports within specified time period
    filing_date_lag_days = config_obj.getint('input', 'filing_date_lag_days')

    # Downloads the zipped FD file
    download_fd_zip(url_source, input_directory)

    # Zipped file name
    file_name = os.path.basename(url_source)

    # Unzips zipped FD file
    unzips_fd_zip(input_directory, file_name)

    # Retrieve the txt file
    file_name_txt = get_fd_text_file(file_name)

    # Read the txt file as a dataframe
    df = read_fd_text_file(input_directory, file_name_txt)

    # Return FDs of select individuals by last name
    df = get_fd_by_full_name(df, list_of_full_names, filing_date_lag_days)

    # Save to a CSV file
    df = df[['Prefix', 'FullName', 'FilingDate', 'URL']]

    df.to_csv(os.path.join(output_directory, output_file), index=False)


if __name__ == '__main__':
    main()