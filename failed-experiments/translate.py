import pandas as pd
import threading
from tqdm import tqdm
from hazm import Normalizer
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import os

normalizer = Normalizer()
df = pd.read_csv('articles_data.csv')
translated_df = df[['Abstract', 'Datetime']]

def translate_text(text):
    url = "http://127.0.0.1:5000/translate"
    data = {
        "q": text,
        "source": "fa",
        "target": "en",
        "format": "text",
        "api_key": ""
    }
    headers = {"Content-Type": "application/json"}
    return requests.post(url, data=json.dumps(data), headers=headers).json().get("translatedText")

def translate_content(row):
    row['Abstract'] = translate_text(normalizer.normalize(row['Abstract']))
    return row

def translate_dataframe(df):
    num_rows = len(df)
    progress_bar = tqdm(total=num_rows, desc='Translating')

    # Create a temporary file to store the translated rows
    temp_file = 'articles_data_translated_temp.csv'
    if os.path.exists(temp_file):
        # If the file already exists, read the last saved row index
        last_row = pd.read_csv(temp_file, nrows=1)
        last_index = last_row.index[0]
        # Skip the rows that have already been translated
        df = df.iloc[last_index + 1:]
    else:
        # If the file does not exist, create it with the column names
        pd.DataFrame(columns=df.columns).to_csv(temp_file, index=False)

    def translate_row(row):
        translated_row = translate_content(row)
        progress_bar.update(1)
        # Append the translated row to the temporary file
        pd.DataFrame([translated_row]).to_csv(temp_file, mode='a', header=False, index=False)
        return translated_row

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(translate_row, row) for _, row in df.iterrows()]
        translated_rows = [future.result() for future in futures]

    # Rename the temporary file to the final file name
    os.rename(temp_file, 'articles_data_translated.csv')
    progress_bar.close()
    return pd.read_csv('articles_data_translated.csv')

# Call the translate_dataframe function
translate_dataframe(translated_df)
