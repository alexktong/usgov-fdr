# Source: https://disclosures-clerk.house.gov/FinancialDisclosure

import os
import pandas as pd

list_of_last_names = ['foxx', 'green']


def download_fd_zip(url_source, input_directory):

    # Downloads the source file into specified directory
    os.system(f'wget -N -P {input_directory} {url_source}')
    
    # Unzips the source file into input directory
    os.system(f'unzip -o -d {input_directory} {input_directory}{file_name}')


def get_fd_text_file(file_name):

    file_name_without_extension = os.path.splitext(file_name)[0]

    file_name_txt = f'{file_name_without_extension}.txt'

    return file_name_txt


def read_fd_text_file(input_directory, fd_file_txt):

    fd_file_txt = get_fd_text_file()
    
    df = pd.read_csv(os.path.join(input_directory, fd_file_txt), sep='\t')

    return df


def get_fd_by_last_name(df, list_of_last_names):
    
    df = df[df['Last'].str.lower().isin(list_of_last_names)]

    return df

def main():

    # Link to source file
    url_source = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2024FD.zip'

    # Directory to save the source file
    input_directory = 'input/'

    # Downloads the zipped FD file
    download_fd_zip(url_source, input_directory)


    # Source file name
    file_name = os.path.basename(url_source)

    # Retrieve the txt file
    file_name_txt = get_fd_text_file(file_name)

    # Read the txt file as a dataframe
    df = read_fd_text_file(input_directory, file_name_txt)

    # Return FDs of select individuals by last name
    df = get_fd_by_last_name(df, list_of_last_names)

if __name__ == '__main__':
    main()