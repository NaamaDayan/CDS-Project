import requests
import pandas as pd
from datetime import datetime
import time


API_KEY = '1a5b7436-1a8b-4b66-a699-43a9a22644f4'

AUTH_ENDPOINT = 'https://utslogin.nlm.nih.gov/cas/v1/api-key'
LOINC_ENDPOINT = 'https://uts-ws.nlm.nih.gov/rest/content/current/CUI/'


def get_tgt(api_key):
    response = requests.post(AUTH_ENDPOINT, data={'apikey': api_key})
    if response.status_code != 201:
        raise Exception(f"Failed to get TGT: {response.status_code}")
    # Extract TGT from HTML form response
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.form['action']


def get_service_ticket(tgt):
    response = requests.post(tgt, data={'service': 'http://umlsks.nlm.nih.gov'})
    if response.status_code != 200:
        raise Exception("Failed to get service ticket")
    return response.text


def get_loinc_long_common_name(loinc_code, tgt):
    service_ticket = get_service_ticket(tgt)
    url = f"https://uts-ws.nlm.nih.gov/rest/content/current/source/LNC/{loinc_code}"
    params = {'ticket': service_ticket}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} for code {loinc_code}")
        return None
    data = response.json()
    return data.get('result', {}).get('name')


def add_loinc_names_to_csv(input_csv_path, output_csv_path=None):
    """
    Add LOINC names to the CSV file by fetching them from the UMLS API.
    Uses pandas apply for efficient processing.
    
    Args:
        input_csv_path (str): Path to the input CSV file
        output_csv_path (str, optional): Path to save the output CSV file. If None, overwrites the input file.
    """
    # Read the CSV file
    df = pd.read_csv(input_csv_path)
    
    # Get TGT for API authentication
    tgt = get_tgt(API_KEY)
    
    # Define a function to get LOINC name with caching
    loinc_name_cache = {}
    def get_loinc_name_with_cache(loinc_num):
        if loinc_num not in loinc_name_cache:
            loinc_name = get_loinc_long_common_name(loinc_num, tgt)
            loinc_name_cache[loinc_num] = loinc_name
            time.sleep(0.5)  # Rate limiting
        return loinc_name_cache[loinc_num]
    
    # Apply the function to get LOINC names
    df['LOINC-NAME'] = df['LOINC-NUM'].apply(get_loinc_name_with_cache)
    
    # Save the updated dataframe
    output_path = output_csv_path if output_csv_path else input_csv_path
    df.to_csv(output_path, index=False)
    
    return df


if __name__ == '__main__':
    # Example usage for single LOINC code
    loinc_codes = ['12181-4']
    tgt = get_tgt(API_KEY)

    for code in loinc_codes:
        name = get_loinc_long_common_name(code, tgt)
        print(f"{code}: {name}")
    
    # Example usage for CSV file
    # add_loinc_names_to_csv("project_db.csv", "project_db_with_names.csv")

