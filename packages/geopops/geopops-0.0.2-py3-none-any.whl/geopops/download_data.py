import os
import json
import pandas as pd
import requests
import zipfile
import gzip
import shutil
import time
from pathlib import Path
import curl_cffi
from curl_cffi import requests as curl_requests
import subprocess

# Set base directory to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Equivalent to R's here package functionality
def here(*args):
    """Function for creating path relative to the base directory. Equivalent to R's here package functionality
    
    Args:
        *args: Variable number of path components to join with the base directory
    
    Returns:
        str: Complete file path constructed by joining the base directory with the provided path components
    """
    return os.path.join(BASE_DIR, *args)

def dim_desc(df):
    """Function for returning dimensions of dataframe as a string
    
    Args:
        df (pandas.DataFrame): The dataframe whose dimensions are to be described
    
    Returns:
        str: A string describing the dimensions in the format "X rows x Y columns"
    """
    return f"{df.shape[0]} rows x {df.shape[1]} columns"

def fips_info(fips_codes, reverse=False):
    """Function for converting FIPS codes to state abbreviations or vice versa. Used for creating destination folders for census data
    
    Args:
        fips_codes (str or list): FIPS code(s) or abbreviation(s) to convert. Can be a single string or a list
        reverse (bool, optional): If True, converts abbreviations to FIPS codes. If False, converts FIPS codes to abbreviations. Defaults to False.
    
    Returns:
        dict: Dictionary with key "abbr" or "fips" containing the converted values. Returns None for invalid codes.
              If input is a list, returns a list of converted values; if input is a string, returns a single converted value.
    """
    # Dictionary mapping FIPS codes to state abbreviations
    fips_to_abbr = {
        "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
        "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
        "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
        "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
        "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
        "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
        "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
        "55": "WI", "56": "WY", "72": "PR"
    }
    
    if reverse:
        # Create reverse mapping from abbreviations to FIPS codes
        abbr_to_fips = {abbr: fips for fips, abbr in fips_to_abbr.items()}
        
        if isinstance(fips_codes, list):
            result = {"fips": [abbr_to_fips.get(code, None) for code in fips_codes]}
            return result
        else:
            return {"fips": abbr_to_fips.get(fips_codes, None)}
    else:
        if isinstance(fips_codes, list):
            result = {"abbr": [fips_to_abbr.get(code, None) for code in fips_codes]}
            return result
        else:
            return {"abbr": fips_to_abbr.get(fips_codes, None)}

# Helper function to download files with retry logic
def try_download(src, dst):
    """Function for downloading a file with timeout and retry logic
    
    Args:
        src (str): The source URL to download from
        dst (str): The destination file path where the downloaded file will be saved
    
    Returns:
        int: Status code (0 for success, -1 for failure)
    """
    timeout = 3600  # 1 hour timeout
    retries = 3
    status = 1
    
    while status != 0 and retries > 0:
        try:
            response = requests.get(src, timeout=timeout, stream=True)
            response.raise_for_status()
            
            with open(dst, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            status = 0
        except Exception as e:
            print(f"Download attempt failed: {e}")
            retries -= 1
            status = -1
    
    if status != 0:
        print(f"Download failed: {src}")
        exit(1)
    
    return status

def try_curl_cffi(src, dst):
    """Function for downloading a file using curl_cffi with timeout and retry logic
    
    Args:
        src (str): The source URL to download from
        dst (str): The destination file path where the downloaded file will be saved
    
    Returns:
        int: Status code (0 for success, -1 for failure)
    """
    timeout = 3600  # 1 hour timeout
    retries = 3
    status = 1
    
    while status != 0 and retries > 0:
        try:
            # Use browser impersonation with appropriate headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
            
            # Try with Chrome impersonation
            response = curl_requests.get(
                src, 
                timeout=timeout,
                impersonate="chrome110",
                headers=headers
            )
            
            if response.status_code >= 400:
                raise Exception(f"HTTP Error {response.status_code}")
            
            with open(dst, 'wb') as f:
                f.write(response.content)
            status = 0
            
        except Exception as e:
            print(f"Download attempt failed: {e}")
            retries -= 1
            status = -1
            time.sleep(2)  # Add a small delay between retries
    
    if status != 0:
        print(f"Download failed: {src}")
        exit(1)
    
    return status

def get_census_metadata(name, vintage, type_="variables"):
    """Function for getting ACS and Decennial metadata from Census API
    
    Args:
        name (str): The census dataset name (e.g., "acs/acs5", "dec/dhc", "dec/sf1")
        vintage (str): The year of the census data (e.g., "2020", "2019"). Comes from the config.json file
        type_ (str, optional): The type of metadata to retrieve. Defaults to "variables". Can be "variables" or "geography"
    
    Returns:
        pandas.DataFrame: DataFrame containing the metadata with variables as rows and metadata fields as columns
    """
    url = f"https://api.census.gov/data/{vintage}/{name}/{type_}.json"
    response = requests.get(url)
    response.raise_for_status()
    return pd.DataFrame(response.json()["variables"]).T.reset_index().rename(columns={"index": "name"})

def get_census_data(name, vintage, vars, region, regionin, key):
    """Function for making a Census API call and getting the data. Works with all ACS years and Decennial years before 2020
    
    Args:
        name (str): The census dataset name (e.g., "acs/acs5", "dec/sf1")
        vintage (str): The year of the census data (e.g., "2020", "2019")
        vars (list): List of variables to retrieve from the Census API
        region (str): The geographic level to retrieve data for (e.g., "block group:*")
        regionin (str): The geographic filter for the region (e.g., "state:24 county:*")
        key (str): The Census API key for authentication
    
    Returns:
        pandas.DataFrame: DataFrame containing the census data with variables as columns and geographic units as rows
    """
    # Build the API URL
    base_url = f"https://api.census.gov/data/{vintage}/{name}"
    
    # Prepare parameters
    params = {
        "get": ",".join(vars),
        "for": region,
        "in": regionin,
        "key": key
    }
    
    # Make the request
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    # Convert to DataFrame
    data = response.json()
    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    return df

def get_new_dec_data(vintage, state_fips):
    """Function for getting 2020 Decennial data using the Census API
    
    Args:
        vintage (str): The year of the decennial data (should be "2020")
        state_fips (str): The FIPS code for the state to retrieve data for
    
    Returns:
        pandas.DataFrame: DataFrame containing the 2020 decennial data with variables as columns and geographic units as rows
    """
    base_url = f"https://api.census.gov/data/{vintage}/dec/dhc?get=group(P18)&ucgid=pseudo(0400000US{state_fips}$1500000)"
    response = requests.get(base_url)
    response.raise_for_status()
    data = response.json()
    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    return df

def pull_census_data(state_fips, year_ACS, year_DEC, ACS_table_codes, DEC_table_codes, key):
    """Function for pulling census data for given states
    
    Args:
        state_fips (str): The FIPS code for the state to retrieve data for
        year_ACS (str): The year of the ACS data
        year_DEC (str): The year of the decennial data
    """

    config_path = os.path.join(BASE_DIR, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json file not found at {config_path}. Please create this file with the required configuration.")
    
    with open(config_path, "r") as f:
        config = json.load(f)

    # Get metadata
    ACS_metadata = get_census_metadata(name="acs/acs5", vintage=year_ACS)
    if year_DEC == 2020:
        DEC_metadata = get_census_metadata(name="dec/dhc", vintage=year_DEC)
    else:
        DEC_metadata = get_census_metadata(name="dec/sf1", vintage=year_DEC)
    
    # Save metadata to CSV files
    # ACS_metadata.to_csv('ACS_metadata.csv')
    # DEC_metadata.to_csv('DEC_metadata.csv')
    
    # Combine ACS and DEC metadata
    metadata_required  = pd.concat([ACS_metadata, DEC_metadata], ignore_index=True)
    
    # Create name-label mapping JSON file
    name_label_mapping = dict(zip(metadata_required["name"], metadata_required["label"]))
    mapping_file = os.path.join(BASE_DIR, "census_metadata.json")
    
    with open(mapping_file, "w") as f:
        json.dump(name_label_mapping, f, indent=4)
    
    for state_i in state_fips:

        print(f"*** Pulling Census data for state = {state_i} ***")
        
        # Process ACS table codes
        table_codes = pd.DataFrame({
            "table_codes": [f"group({code})" for code in ACS_table_codes],
            "table_name": [f"ACSDT5Y{year_ACS}.{code}-Data" for code in ACS_table_codes]
        })
        
        for _, row in table_codes.iterrows():
            # print(f"Downloading {row['table_name']}")
            
            # Make the API call and get the data
            data = get_census_data(
                name="acs/acs5",
                vintage=year_ACS,
                vars=[row["table_codes"]],
                region="block group:*",
                regionin=f"state:{state_i} county:*",
                key=key
            )
            
            # Process data using Pandas
            data = data.drop(columns=["state", "county", "tract", "block group"], errors="ignore")
            
            cols = data.columns.to_list()
            if "GEO_ID" in cols and "NAME" in cols: # Move GEO_ID and NAME to the beginning
                cols.remove("GEO_ID")
                cols.remove("NAME")
                cols = ["GEO_ID", "NAME"] + cols
                data = data[cols]
            
            data = data.astype(str) # Convert all columns to string
            data_labels = ACS_metadata[ACS_metadata["name"].isin(data.columns)][["name", "label"]] # Get labels from metadata
            
            label_dict = dict(zip(data_labels["name"], data_labels["label"])) # Create a dictionary of column names to labels
            all_labels = {col: col for col in data.columns} # Ensure all columns have a label
            all_labels.update(label_dict)
            label_df = pd.DataFrame([all_labels]) # Create a DataFrame with labels as the first row
            
            data_with_labels = pd.concat([label_df, data], ignore_index=True)  # Combine label row with data
            data_with_labels = data_with_labels.loc[:, ~data_with_labels.columns.str.endswith(('EA', 'M', 'MA'))] # Remove columns ending with EA, M, or MA
            
            # Create destination folder and save to CSV
            state_abbr = fips_info(state_i)["abbr"]
            destination_folder = here("census", state_abbr.upper())
            os.makedirs(destination_folder, exist_ok=True)
            file_name = f"{row['table_name']}.csv"
            file_path = os.path.join(destination_folder, file_name)
            data_with_labels.to_csv(file_path, index=False)
            print(f"Downloaded: census/{state_abbr.upper()}/{file_name}")
        
        # Process DEC table codes        
        table_codes = pd.DataFrame({
            "table_codes": [f"group({code})" for code in DEC_table_codes],
            "table_name": [f"DECENNIALSF1{year_DEC}.{code}-Data" for code in DEC_table_codes]
        })
        
        for _, row in table_codes.iterrows():
            # print(f"Downloading {row['table_name']}")
            
            # Make the API call and get the data
            if year_DEC == 2020:
                data = get_new_dec_data(year_DEC, state_i)
                # Remove columns ending in 'A'
                data = data.loc[:, ~data.columns.str.endswith('A')]
                data.drop(columns=["ucgid"], inplace=True)
            
            else:
                data = get_census_data(
                    name="dec/sf1",
                    vintage=year_DEC,
                    vars=[row["table_codes"]],
                    region="block group:*",
                    regionin=f"state:{state_i} county:*",
                    key=key
                )
            
            # Process data using Pandas
            data = data.drop(columns=["state", "county", "tract", "block group"], errors="ignore")
            cols = data.columns.to_list() 
            if "GEO_ID" in cols and "NAME" in cols: # Move GEO_ID and NAME to the beginning of the dataframe
                cols.remove("GEO_ID")
                cols.remove("NAME")
                cols = ["NAME","GEO_ID"] + cols
                data = data[cols]
        
            data = data.astype(str) # Convert all columns to string
            data_labels = DEC_metadata[DEC_metadata["name"].isin(data.columns)][["name", "label"]] # Get labels from metadata
            
            
            label_dict = dict(zip(data_labels["name"], data_labels["label"])) # Create a dictionary of column names to labels
            all_labels = {col: col for col in data.columns} # Ensure all columns have a label
            all_labels.update(label_dict)
            label_df = pd.DataFrame([all_labels]) # Create a DataFrame with labels as the first row
            
            data_with_labels = pd.concat([label_df, data], ignore_index=True) # Combine label row with data
            
            if year_DEC == 2020: # 2020 Decennial data has a different format for the labels
                data_with_labels.iloc[0, 2:] = data_with_labels.iloc[0, 2:].str.replace(':', '') # Strip ":" from the second row (labels) starting from fourth column
                data_with_labels.iloc[0, 2:] = data_with_labels.iloc[0, 2:].str[3:] # Remove first two characters from each string in the second row starting from fourth column
            
            data_with_labels = data_with_labels.loc[:, ~data_with_labels.columns.str.endswith('ERR')] # Remove columns ending with ERR
            
            # Create destination folder and save to CSV
            state_abbr = fips_info(state_i)["abbr"]
            destination_folder = here("census", state_abbr.upper())
            os.makedirs(destination_folder, exist_ok=True)
            file_name = f"{row['table_name']}.csv"
            file_path = os.path.join(destination_folder, file_name)
            data_with_labels.to_csv(file_path, index=False)
            print(f"Downloaded: census/{state_abbr.upper()}/{file_name}")

def pull_pums_data(states, year):
    """Function for pulling PUMS microdata for given states
    
    Args:
        states (list): List of state abbreviations
        year (str): The year of the PUMS data
    """
    
    states = [s.lower() for s in states]

    file_urls = []
    
    # Set the URL of the file to download
    for state in states:
        file_urls.append((state, f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/5-Year/csv_h{state}.zip"))
        file_urls.append((state, f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/5-Year/csv_p{state}.zip"))
    
    for state_i in states:
        
        print(f"*** Pulling PUMS data for state = {state_i.upper()} ***")
        
        urls_list = [url for state, url in file_urls if state == state_i]
        
        for url in urls_list:
            download_url = url
            
            # Specify the destination folder and file name
            destination_folder = here("pums")
            file_name = os.path.basename(download_url)
            destination_file = os.path.join(destination_folder, file_name)
            print(destination_folder)
            # Create the destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            
            # Download the file
            try_curl_cffi(download_url, destination_file)
            
            # Extract the contents of the zip file
            with zipfile.ZipFile(destination_file, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
            
            # Remove the zip file
            os.remove(destination_file)
            
            state_fips = fips_info(state_i.upper(), reverse=True)['fips']
            if file_name == f'csv_h{state_i}.zip':
                df_h = pd.read_csv(f"{destination_folder}/psam_h{state_fips}.csv")
                if year >= 2020:
                    # ACCESSINET(formerly ACCESS), TYPEHUGQ (formerly TYPE).
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2016-2020_PUMS_Variable_Changes_and_Explanations.pdf
                    df_h.rename(columns={'ACCESSINET': 'ACCESS'}, inplace=True) # 
                    df_h.rename(columns={'TYPEHUGQ': 'TYPE'}, inplace=True)
                if year >= 2021:
                    # FES variable deleted in 2021. Can be recreated from WORKSTAT.
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2017-2021_PUMS_Variable_Changes_and_Explanations.pdf
                    df_h.loc[(df_h['WORKSTAT'] == 1)|(df_h['WORKSTAT'] == 2)|(df_h['WORKSTAT'] == 5), 'FES'] = 1
                    df_h.loc[(df_h['WORKSTAT'] == 3)|(df_h['WORKSTAT'] == 6), 'FES'] = 2
                    df_h.loc[(df_h['WORKSTAT'] == 7)|(df_h['WORKSTAT'] == 8), 'FES'] = 3
                    df_h.loc[(df_h['WORKSTAT'] == 9), 'FES'] = 4
                    df_h.loc[(df_h['WORKSTAT'] == 10)|(df_h['WORKSTAT'] == 11), 'FES'] = 5
                    df_h.loc[(df_h['WORKSTAT'] == 12), 'FES'] = 6
                    df_h.loc[(df_h['WORKSTAT'] == 13)|(df_h['WORKSTAT'] == 14), 'FES'] = 7
                    df_h.loc[(df_h['WORKSTAT'] == 15), 'FES'] = 8 
                if year >= 2022:
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2018-2022_PUMS_Variable_Changes_and_Explanations.pdf
                    # We may want to use PUMA10 since that's the definition we were using before
                    df_h.rename(columns={'PUMA10': 'PUMA'}, inplace=True)
                if year >= 2023:
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2019-2023_PUMS_Variable_Changes_and_Explanations.pdf
                    # ST variable now called STATE
                    df_h.rename(columns={'STATE': 'ST'}, inplace=True)
                df_h.to_csv(f"{destination_folder}/psam_h{state_fips}.csv", index=False)
                print(f"Downloaded: pums/psam_h{state_fips}.csv")
            else: # psam_p{state_fips}.csv
                df_p = pd.read_csv(f"{destination_folder}/psam_p{state_fips}.csv")
                if year >= 2022:
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2018-2022_PUMS_Variable_Changes_and_Explanations.pdf
                    # In 2022, these variables were renamed to reflect new definitions from 2020 census
                    # We may want to use PUMA10 since that's the definition we were using before
                    df_p.rename(columns={'POWPUMA10': 'POWPUMA'}, inplace=True)
                    df_p.rename(columns={'PUMA10': 'PUMA'}, inplace=True)
                if year >= 2023:
                    # https://www2.census.gov/programs-surveys/acs/tech_docs/pums/variable_changes/ACS2019-2023_PUMS_Variable_Changes_and_Explanations.pdf
                    # ST variable now called STATE
                    # WKW ("Weeks worked during past 12 months") variable deleted. Can now use WKWN
                    df_p.rename(columns={'STATE': 'ST'}, inplace=True)
                    df_p.rename(columns={'WKWN': 'WKW'}, inplace=True)
                df_p.to_csv(f"{destination_folder}/psam_p{state_fips}.csv", index=False)
                print(f"Downloaded: pums/psam_p{state_fips}.csv")

def download_shapefiles(state_fips, year):
    """Function for downloading shapefiles from census web server
    
    Args:
        state_fips (list): List of state abbreviations
        year (str): The year of the shapefiles
    """
    
    file_urls = []
    
    # Set the URL of the file to download
    for state in state_fips:
        file_urls.append((state, f"https://www2.census.gov/geo/tiger/TIGER{year}/BG/tl_{year}_{state}_bg.zip"))
    
    for state_i in state_fips:
        
        print(f"*** Pulling Shapefiles for state = {state_i} ***")
        
        urls_list = [url for state, url in file_urls if state == state_i]
        
        for url in urls_list:
            download_url = url
            
            # Specify the destination folder and file name
            destination_folder = here("geo")
            
            file_name = os.path.basename(download_url)
            destination_file = os.path.join(destination_folder, file_name)
            
            # Create the destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            
            # Download the file
            try_curl_cffi(download_url, destination_file)
            
            # Extract the contents of the zip file
            with zipfile.ZipFile(destination_file, 'r') as zip_ref:
                zip_ref.extractall(destination_folder)
            
            print(f"Downloaded: geo/{file_name}")

def pull_LODES(states_main, states_aux, year):
    """Function for pulling LEHD LODES data (commuting patterns) for given states
    
    Args:
        states_main (list): List of state abbreviations for the main states
        states_aux (list): List of state abbreviations for the auxiliary states
        year (str): The year of the LODES data
        
    Notes: As of June 25, 2025, no LODES data available for 2023.
    """
    # Determine version based on year
    version = "LODES8" if year >= 2020 else "LODES7"
    
    # For the states on the "main" list, download OD main JT01, OD aux JT01, and WAC S000 JT01
    for state_i in states_main:
        # print(f"*** Downloading LODES data for state = {state_i.upper()} ***")
        state_i = state_i.lower()
        state_dir = here("work")
        os.makedirs(state_dir, exist_ok=True)
        
        # Download and save OD main JT01
        # print(f"downloading lodes od main {state_i}")
        
        # For OD main JT01        
        od_main_url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state_i}/od/{state_i}_od_main_JT01_{year}.csv.gz"
        outfile = os.path.join(state_dir, f"{state_i}_od_main_JT01_{year}.csv.gz")
        try_download(od_main_url, outfile)
        
        # Process the file to match old format
        with gzip.open(outfile, 'rt') as f_in:
            with gzip.open(outfile + '.tmp', 'wt') as f_out:
                # Read header
                header = f_in.readline().strip()
                # Write new header with year and state
                f_out.write("year,state," + header + "\n")
                
                # Process each line
                for line in f_in:
                    parts = line.strip().split(',')
                    # Truncate geocodes to 12 digits
                    parts[0] = parts[0][:12]  # w_geocode
                    parts[1] = parts[1][:12]  # h_geocode
                    # Add year and state
                    f_out.write(f"{year},{state_i.upper()}," + ",".join(parts) + "\n")
        print(f"Downloaded: work/{state_i}_od_main_JT01_{year}.csv.gz")
        
        # Replace original file with processed file
        os.replace(outfile + '.tmp', outfile)
        
        # For OD aux JT01
        # print(f"downloading lodes od aux {state_i}")
        od_aux_url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state_i}/od/{state_i}_od_aux_JT01_{year}.csv.gz"
        outfile = os.path.join(state_dir, f"{state_i}_od_aux_JT01_{year}.csv.gz")
        try_download(od_aux_url, outfile)
        
        # Process the file to match old format
        with gzip.open(outfile, 'rt') as f_in:
            with gzip.open(outfile + '.tmp', 'wt') as f_out:
                header = f_in.readline().strip() # Read header
                f_out.write("year,state," + header + "\n")  # Write new header with year and state
                
                # Process each line
                for line in f_in:
                    parts = line.strip().split(',')
                    # Truncate geocodes to 12 digits
                    parts[0] = parts[0][:12]  # w_geocode
                    parts[1] = parts[1][:12]  # h_geocode
                    # Add year and state
                    f_out.write(f"{year},{state_i.upper()}," + ",".join(parts) + "\n")
        print(f"Downloaded: work/{state_i}_od_aux_JT01_{year}.csv.gz")
        
        # Replace original file with processed file
        os.replace(outfile + '.tmp', outfile)
        
        # For WAC S000 JT01
        # print(f"downloading lodes wac {state_i}")
        wac_url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state_i}/wac/{state_i}_wac_S000_JT01_{year}.csv.gz"
        outfile = os.path.join(state_dir, f"{state_i}_wac_S000_JT01_{year}.csv.gz")
        try_download(wac_url, outfile)
        
        # Process the file to match old format
        with gzip.open(outfile, 'rt') as f_in:
            with gzip.open(outfile + '.tmp', 'wt') as f_out:
                header = f_in.readline().strip() # Read header
                f_out.write("year,state," + header + "\n")  # Write new header with year and state
                
                # Process each line
                for line in f_in:
                    parts = line.strip().split(',')
                    # Truncate geocode to 12 digits
                    parts[0] = parts[0][:12]  # w_geocode
                    # Add year and state
                    f_out.write(f"{year},{state_i.upper()}," + ",".join(parts) + "\n")
        print(f"Downloaded: work/{state_i}_wac_S000_JT01_{year}.csv.gz")
        
        # Replace original file with processed file
        os.replace(outfile + '.tmp', outfile)
    
    # For the states on the "aux" list just download OD aux JT01
    for state_i in states_aux:
        state_dir = here("work")
        os.makedirs(state_dir, exist_ok=True)
        
        # Download and save OD aux JT01
        # print(f"downloading lodes od aux {state_i}")
        od_aux_url = f"https://lehd.ces.census.gov/data/lodes/{version}/{state_i.lower()}/od/{state_i.lower()}_od_aux_JT01_{year}.csv.gz"
        outfile = os.path.join(state_dir, f"{state_i.lower()}_od_aux_JT01_{year}.csv.gz")
        try_download(od_aux_url, outfile)
        
        # Process the file to match old format
        with gzip.open(outfile, 'rt') as f_in:
            with gzip.open(outfile + '.tmp', 'wt') as f_out:
                header = f_in.readline().strip() # Read header
                f_out.write("year,state," + header + "\n")  # Write new header with year and state
                
                # Process each line
                for line in f_in:
                    parts = line.strip().split(',')
                    # Truncate geocodes to 12 digits
                    parts[0] = parts[0][:12]  # w_geocode
                    parts[1] = parts[1][:12]  # h_geocode
                    # Add year and state
                    f_out.write(f"{year},{state_i.upper()}," + ",".join(parts) + "\n")
        print(f"Downloaded: work/{state_i}_od_aux_JT01_{year}.csv.gz")
        
        # Replace original file with processed file
        os.replace(outfile + '.tmp', outfile)
    

def main():
    """Main function for pulling Census data (ACS and Decennial), PUMS data, shapefiles, and LODES data"""
    
    # Read config.json
    config_path = os.path.join(BASE_DIR, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json file not found at {config_path}. Please create this file with the required configuration.")
    
    with open(config_path, "r") as f:
        config = json.load(f)

    # Get API key from config
    if "census_api_key" not in config:
        raise KeyError("census_api_key not found in config.json. Please add your Census API key to the configuration file.")
    key = config["census_api_key"]

    # Get years from config
    if "main_year" not in config:
        raise KeyError("main_year not found in config.json. Please add the main year to the configuration file.")
    if "decennial_year" not in config:
        raise KeyError("decennial_year not found in config.json. Please add the decennial year to the configuration file.")
    main_year = config["main_year"]
    decennial_year = config["decennial_year"]

    # Extract state FIPS codes
    main_fips = [fips[:2] for fips in config["geos"]]
    main_fips = list(set(main_fips))  # unique values
    main_abbr = [abbr for abbr in fips_info(main_fips)["abbr"] if abbr is not None]

    # Handle use_pums
    if "use_pums" not in config or config["use_pums"] is None:
        use_pums = main_abbr
    else:
        use_pums = [abbr for abbr in fips_info(config["use_pums"])["abbr"] if abbr is not None]

    # Handle commute_states
    if "commute_states" not in config or config["commute_states"] is None:
        aux_abbr = []
    else:
        # Filter out states already in main_fips
        aux_states = [state for state in config["commute_states"] if state not in main_fips]
        aux_abbr = [abbr for abbr in fips_info(aux_states)["abbr"] if abbr is not None]

    # Get required table codes from config
    acs_required = config["acs_required"]
    
    # Get required table codes for Decennial data (Group quarters data)
    if decennial_year == 2020:
        dec_required = [config["dec_required"][1]] # "P18" the code changed for 2020
    else:
        dec_required = [config["dec_required"][0]] # "P43"

    # Pull census data
    pull_census_data(
        state_fips=main_fips,
        year_ACS=main_year,
        year_DEC=decennial_year,
        ACS_table_codes=acs_required,
        DEC_table_codes=dec_required,
        key=key
    )

    # Pull PUMS data
    pull_pums_data(states=use_pums, year=main_year)

    # Download shapefiles
    download_shapefiles(main_fips, main_year)

    # Pull LODES data
    print(f"Pulling LODES for state = {', '.join(main_abbr)} and aux-only for state = {', '.join(aux_abbr)} (blank if no aux states)")
    pull_LODES(main_abbr, aux_abbr, main_year)

if __name__ == "__main__":
    main()