# ETL (RestAPI to Postgresql) with Pandas
import os
import re
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import String, Integer

load_dotenv()

API_URL = os.getenv('API_URL')
DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(DB_URL)

def extract():
    # Fetch data dari API
    response = requests.get(API_URL)
    response.raise_for_status()

    return response.json()

def transform(raw_data):
    df = pd.DataFrame(raw_data)

    # Flatten nested data
    df['city'] = df['address'].apply(lambda x: x.get('city') if isinstance(x, dict) else None)
    df['company_name'] = df['company'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

    # Filter data
    columns = ['id', 'name', 'email','city', 'company_name']
    df_clean = df[columns].copy()

    return df_clean

def load(df):
    with engine.begin() as conn:

        conn.execute(text("DROP TABLE ID EXISTS api_users CASCADE;"))

        df.to_sql('api_users',con=conn, if_exists = 'replace', index = False,
            dtype={
                'id': Integer(),
                'name': String(150),
                'email': String(150),
                'city': String(100),
                'company_name': String(150)
            })
        conn.execute(text("ALTER TABLE api_users ADD PRIMARY KEY (id);"))

    return True

def main():

    raw_data = extract()
    clean_data = transform(raw_data)
    load(clean_data)

if __name__ == '__main__':
    main()